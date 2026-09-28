import datetime
import logging
from fastapi import APIRouter, HTTPException
from app.core.db import get_database
from app.routers.session import in_memory_sessions
from app.services.interview_engine import generate_first_question, process_turn_and_get_next_question
from app.models.schemas import InterviewQuestionResponse, AnswerSubmitRequest

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
