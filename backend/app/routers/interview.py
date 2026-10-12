import datetime
import logging
from typing import List
from fastapi import APIRouter, HTTPException
from app.core.db import get_database
from app.routers.session import in_memory_sessions
from app.services.interview_engine import (
    generate_first_question,
    process_turn_and_get_next_question,
    generate_all_questions_for_session,
    evaluate_batch_answers,
)
from app.services.scorer import generate_evaluation_report
from app.models.schemas import (
    InterviewQuestionResponse,
    AnswerSubmitRequest,
    FullInterviewQuestionsResponse,
    BatchAnswerSubmitRequest,
    EvaluationReportResult,
)

logger = logging.getLogger("uvicorn.error")
router = APIRouter(prefix="/sessions", tags=["Interview Engine"])

async def get_session_or_404(session_id: str) -> dict:
    db = get_database()
    sess = None
    if db is not None:
        sess = await db.sessions.find_one({"session_id": session_id})
    if not sess:
        sess = in_memory_sessions.get(session_id)
    if not sess:
        raise HTTPException(status_code=404, detail="Interview session not found.")
    return sess

@router.get("/{session_id}/questions", response_model=FullInterviewQuestionsResponse)
async def get_full_interview_questions(session_id: str):
    """Generate all interview questions upfront across all 4 stages for a stable, jumpable interview loop."""
    sess = await get_session_or_404(session_id)
    resume_data = sess.get("resume_analysis", {})
    role_data = sess.get("role_analysis", {})
    company_data = sess.get("company_info", {})

    questions_list = generate_all_questions_for_session(sess)

    # Persist in session state if newly started
    if sess.get("status") in ["created", None]:
        sess["status"] = "in_progress"
        sess["total_questions_planned"] = len(questions_list)
        db = get_database()
        if db is not None:
            await db.sessions.update_one(
                {"session_id": session_id},
                {"$set": {
                    "status": "in_progress",
                    "total_questions_planned": len(questions_list),
                    "updated_at": datetime.datetime.now(datetime.timezone.utc)
                }}
            )
        in_memory_sessions[session_id] = sess

    return FullInterviewQuestionsResponse(
        session_id=session_id,
        candidate_name=resume_data.get("candidate_name", "Candidate"),
        role_title=role_data.get("role_title", "Software Engineer"),
        company_name=company_data.get("company_name", "Target Company"),
        role_category=sess.get("role_category", "tech"),
        difficulty_level=sess.get("difficulty_level", "medium"),
        total_questions=len(questions_list),
        company_profile=company_data,
        job_description=sess.get("job_description"),
        questions=questions_list
    )

@router.post("/{session_id}/submit-all", response_model=EvaluationReportResult)
async def submit_all_interview_answers(session_id: str, payload: BatchAnswerSubmitRequest):
    """
    Evaluate all submitted candidate answers concurrently using asyncio.gather
    and generate the final comprehensive evaluation report.
    """
    sess = await get_session_or_404(session_id)

    raw_answers = [item.model_dump() for item in payload.answers]
    evaluated_turns = await evaluate_batch_answers(sess, raw_answers)

    sess["turns"] = evaluated_turns
    sess["status"] = "completed"
    sess["current_turn"] = len(evaluated_turns)

    report = await generate_evaluation_report(sess)
    report_dict = report.model_dump()
    sess["evaluation_report"] = report_dict

    db = get_database()
    if db is not None:
        await db.sessions.update_one(
            {"session_id": session_id},
            {"$set": {
                "turns": evaluated_turns,
                "status": "completed",
                "current_turn": len(evaluated_turns),
                "evaluation_report": report_dict,
                "updated_at": datetime.datetime.now(datetime.timezone.utc)
            }}
        )
    in_memory_sessions[session_id] = sess

    return report


@router.post("/{session_id}/start", response_model=InterviewQuestionResponse)
async def start_interview(session_id: str):
    """Start the mock interview loop and return Question 1."""
    sess = await get_session_or_404(session_id)

    # Check if first question already generated
    turns = sess.get("turns", [])
    if turns:
        first_turn = turns[0]
        return InterviewQuestionResponse(
            session_id=session_id,
            turn_number=1,
            total_questions=sess.get("total_questions_planned", 8),
            question=first_turn.get("question", ""),
            topic=first_turn.get("topic", "Opening"),
            difficulty=first_turn.get("difficulty", 3),
            stage_title=first_turn.get("stage_title", "Round 1: Initial Assessment"),
            stage_category=first_turn.get("stage_category", "aptitude"),
            question_type=first_turn.get("question_type", "mcq"),
            options=first_turn.get("options"),
            coding_starter_code=first_turn.get("coding_starter_code"),
            coding_language=first_turn.get("coding_language"),
            email_context=first_turn.get("email_context"),
            is_final=False,
            reason="Resuming active session"
        )

    resume_data = sess.get("resume_analysis", {})
    role_data = sess.get("role_analysis", {})
    company_data = sess.get("company_info", {})

    q1_resp = await generate_first_question(
        session_id=session_id,
        resume_data=resume_data,
        role_data=role_data,
        company_data=company_data
    )

    # Record turn 1 initialized in session
    turn_1_entry = {
        "turn_number": 1,
        "question": q1_resp.question,
        "topic": q1_resp.topic,
        "difficulty": q1_resp.difficulty,
        "stage_title": q1_resp.stage_title,
        "stage_category": q1_resp.stage_category,
        "question_type": q1_resp.question_type,
        "options": q1_resp.options,
        "coding_starter_code": q1_resp.coding_starter_code,
        "coding_language": q1_resp.coding_language,
        "email_context": q1_resp.email_context,
        "user_answer": None,
        "evaluation": None,
        "created_at": datetime.datetime.now(datetime.timezone.utc)
    }

    sess["status"] = "in_progress"
    sess["current_turn"] = 1
    sess["total_questions_planned"] = q1_resp.total_questions
    sess["turns"] = [turn_1_entry]

    db = get_database()
    if db is not None:
        await db.sessions.update_one(
            {"session_id": session_id},
            {"$set": {
                "status": "in_progress",
                "current_turn": 1,
                "total_questions_planned": q1_resp.total_questions,
                "turns": [turn_1_entry],
                "updated_at": datetime.datetime.now(datetime.timezone.utc)
            }}
        )
    in_memory_sessions[session_id] = sess

    return q1_resp

@router.post("/{session_id}/answer", response_model=InterviewQuestionResponse)
async def submit_answer(session_id: str, payload: AnswerSubmitRequest):
    """Submit text answer for current turn, execute evaluation & adaptation, return next question."""
    sess = await get_session_or_404(session_id)
    turns = sess.get("turns", [])

    if not turns:
        raise HTTPException(status_code=400, detail="Interview session has not been started yet. Call /start first.")

    # Save user answer to latest open turn
    current_turn = turns[-1]
    current_turn["user_answer"] = payload.answer.strip()
    if payload.selected_option:
        current_turn["selected_option"] = payload.selected_option

    # Process evaluation and next question
    eval_result, next_q_resp = await process_turn_and_get_next_question(
        session_data=sess,
        raw_user_answer=payload.answer.strip()
    )

    current_turn["evaluation"] = eval_result.model_dump()

    # Update session turns
    if not next_q_resp.is_final:
        next_turn_entry = {
            "turn_number": next_q_resp.turn_number,
            "question": next_q_resp.question,
            "topic": next_q_resp.topic,
            "difficulty": next_q_resp.difficulty,
            "stage_title": next_q_resp.stage_title,
            "stage_category": next_q_resp.stage_category,
            "question_type": next_q_resp.question_type,
            "options": next_q_resp.options,
            "coding_starter_code": next_q_resp.coding_starter_code,
            "coding_language": next_q_resp.coding_language,
            "email_context": next_q_resp.email_context,
            "user_answer": None,
            "evaluation": None,
            "created_at": datetime.datetime.now(datetime.timezone.utc)
        }
        turns.append(next_turn_entry)
        sess["current_turn"] = next_q_resp.turn_number
    else:
        sess["status"] = "completed"

    sess["current_difficulty"] = next_q_resp.difficulty
    sess["total_questions_planned"] = next_q_resp.total_questions
    sess["turns"] = turns

    db = get_database()
    if db is not None:
        await db.sessions.update_one(
            {"session_id": session_id},
            {"$set": {
                "status": sess["status"],
                "current_turn": sess.get("current_turn", 1),
                "current_difficulty": next_q_resp.difficulty,
                "total_questions_planned": next_q_resp.total_questions,
                "turns": turns,
                "updated_at": datetime.datetime.now(datetime.timezone.utc)
            }}
        )
    in_memory_sessions[session_id] = sess

    return next_q_resp
