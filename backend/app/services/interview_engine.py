import logging
from typing import Dict, Any, Tuple
from app.core.security import sanitize_user_answer
from app.core.llm import llm_client
from app.models.schemas import (
    InterviewQuestionResponse,
    AnswerEvaluationResult,
    StepNextQuestionResponse
)
from app.prompts.interview_prompt import (
    INTERVIEW_QUESTION_SYSTEM_PROMPT,
    INTERVIEW_QUESTION_USER_PROMPT,
    EVALUATE_ANSWER_SYSTEM_PROMPT,
    EVALUATE_ANSWER_USER_PROMPT
)

logger = logging.getLogger("uvicorn.error")

TOPIC_ROTATION = [
    "Background & Resume Alignment",
    "Core Technical Depth",
    "System Architecture & Scaling",
    "Target Company Tech & Product Alignment",
    "Behavioral & Situational Leadership",
    "Problem Solving Under Constraints"
]

def calculate_initial_planned_questions(seniority: str) -> int:
    """Calculate default total interview length based on role seniority calibration."""
    sen_lower = seniority.lower()
    if "junior" in sen_lower or "entry" in sen_lower:
        return 6
    elif "senior" in sen_lower or "lead" in sen_lower or "staff" in sen_lower:
        return 10
    else:
        return 8  # Mid-level default

async def generate_first_question(
    session_id: str,
    resume_data: Dict[str, Any],
    role_data: Dict[str, Any],
    company_data: Dict[str, Any]
) -> InterviewQuestionResponse:
    """Generate the initial opening question for Turn 1."""
    role_title = role_data.get("role_title", "Target Role")
    seniority = role_data.get("seniority_level", "Mid")
    company_name = company_data.get("company_name", "Target Company")
    total_planned = calculate_initial_planned_questions(seniority)

    history_str = "No prior history. This is the first question of the interview."
    candidate_skills = ", ".join(resume_data.get("skills", [])[:8])
    experience_years = resume_data.get("experience_years", 3.0)
    company_tech = ", ".join(company_data.get("tech_stack", [])[:6])

    prompt = INTERVIEW_QUESTION_USER_PROMPT.format(
        role_title=role_title,
        seniority_level=seniority,
        company_name=company_name,
        company_tech_stack=company_tech or "Modern Web & Distributed Systems",
        candidate_skills=candidate_skills or "Software Engineering",
        experience_years=experience_years,
        conversation_history=history_str,
        turn_number=1,
        total_questions=total_planned,
        target_topic="Background & Resume Alignment",
        difficulty=3
    )

    result: StepNextQuestionResponse = await llm_client.generate_json(
        prompt=prompt,
        schema_cls=StepNextQuestionResponse,
        system_prompt=INTERVIEW_QUESTION_SYSTEM_PROMPT
    )

    question_text = result.next_question
    if not question_text or len(question_text.strip()) < 10:
        question_text = f"Welcome! To kick off our interview for the {role_title} position at {company_name}, could you briefly introduce yourself and highlight a recent project that best showcases your relevant skills?"

    return InterviewQuestionResponse(
        session_id=session_id,
        turn_number=1,
        total_questions=total_planned,
        question=question_text,
        topic=result.topic or "Background & Resume Alignment",
        difficulty=3,
        is_final=False,
        reason="Opening interview turn"
    )

async def evaluate_candidate_answer(
    question_asked: str,
    raw_user_answer: str,
    role_data: Dict[str, Any]
) -> AnswerEvaluationResult:
    """Evaluate candidate text answer objectively."""
    sanitized_answer = sanitize_user_answer(raw_user_answer)
    role_title = role_data.get("role_title", "Software Engineer")
    seniority = role_data.get("seniority_level", "Mid")

    prompt = EVALUATE_ANSWER_USER_PROMPT.format(
        question_asked=question_asked,
        sanitized_user_answer=sanitized_answer,
        role_title=role_title,
        seniority_level=seniority
    )

    eval_result: AnswerEvaluationResult = await llm_client.generate_json(
        prompt=prompt,
        schema_cls=AnswerEvaluationResult,
        system_prompt=EVALUATE_ANSWER_SYSTEM_PROMPT
    )

    # Compute overall turn score
    computed_score = (
        0.30 * eval_result.relevance_score +
        0.35 * eval_result.depth_score +
        0.20 * eval_result.correctness_score +
        0.15 * eval_result.communication_score
    )
    eval_result.turn_score = round(computed_score, 1)
    return eval_result

def decide_adaptation(
    current_turn: int,
    current_planned_total: int,
    current_difficulty: int,
    last_turn_score: float,
    all_turn_scores: list[float]
) -> Tuple[int, int, bool, str]:
    """
    Execute adaptive rules engine logic:
    Returns (next_difficulty, new_planned_total, is_final, reason).
    """
    # 1. Update Difficulty (1 to 5)
    next_diff = current_difficulty
    if last_turn_score >= 80:
        next_diff = min(5, current_difficulty + 1)
    elif last_turn_score <= 45:
        next_diff = max(1, current_difficulty - 1)

    new_total = current_planned_total
    avg_score = sum(all_turn_scores) / len(all_turn_scores) if all_turn_scores else 70.0

    # 2. Check Shorten / Extend Logic
    # Shorten condition: Very low performance over 4+ turns OR high early mastery
    if current_turn >= 5 and avg_score <= 35:
        return next_diff, current_turn, True, "Early termination due to consistent severe skill gaps."

    if current_turn >= 5 and avg_score >= 92 and current_turn < current_planned_total:
        new_total = current_turn  # Shorten to finish early on clear high-mastery
        return next_diff, current_turn, True, "Early completion on demonstrated mastery across core competencies."

    # Extend condition: Strong answers but borderline average score requiring clarification (max 15 questions)
    if current_turn == current_planned_total and avg_score >= 65 and current_planned_total < 15:
        new_total = min(15, current_planned_total + 2)

    is_final = (current_turn >= new_total)
    reason = "Interview completed" if is_final else "Advancing to next question"

    return next_diff, new_total, is_final, reason

async def process_turn_and_get_next_question(
    session_data: Dict[str, Any],
    raw_user_answer: str
) -> Tuple[AnswerEvaluationResult, InterviewQuestionResponse]:
    """Process user answer, execute evaluation, update session state, and generate next question."""
    session_id = session_data["session_id"]
    turns = session_data.get("turns", [])
    current_turn_number = len(turns) + 1
    current_planned = session_data.get("total_questions_planned", 8)
    current_difficulty = session_data.get("current_difficulty", 3)

    last_turn_data = turns[-1] if turns else {"question": "Describe your engineering background."}
    question_asked = last_turn_data.get("question", "")

    # 1. Evaluate answer
    eval_result = await evaluate_candidate_answer(
        question_asked=question_asked,
        raw_user_answer=raw_user_answer,
        role_data=session_data.get("role_analysis", {})
    )

    # 2. Compute adaptation
    all_scores = []
    for t in turns:
        ev = t.get("evaluation")
        if ev and isinstance(ev, dict):
            all_scores.append(ev.get("turn_score", 75.0))
        else:
            all_scores.append(75.0)
    all_scores.append(eval_result.turn_score)

    next_diff, new_planned_total, is_final, adaptation_reason = decide_adaptation(
        current_turn=current_turn_number,
        current_planned_total=current_planned,
        current_difficulty=current_difficulty,
        last_turn_score=eval_result.turn_score,
        all_turn_scores=all_scores
    )

    if is_final:
        final_resp = InterviewQuestionResponse(
            session_id=session_id,
            turn_number=current_turn_number,
            total_questions=new_planned_total,
            question="Thank you! You have completed all questions in the mock interview loop.",
            topic="Completed",
            difficulty=next_diff,
            is_final=True,
            reason=adaptation_reason
        )
        return eval_result, final_resp

    # 3. Generate Next Question via LLM
    next_topic = TOPIC_ROTATION[current_turn_number % len(TOPIC_ROTATION)]
    if eval_result.relevance_score < 55 or eval_result.depth_score < 50:
        next_topic = f"Follow-up: {last_turn_data.get('topic', 'Technical Depth')}"

    # Build history string
    history_lines = []
    for t in turns[-3:]:  # Last 3 turns context
        history_lines.append(f"Q: {t.get('question')}\nA: {t.get('user_answer')[:300]}")
    history_str = "\n\n".join(history_lines) if history_lines else "No previous history."

    role_data = session_data.get("role_analysis", {})
    resume_data = session_data.get("resume_analysis", {})
    company_data = session_data.get("company_info", {})

    prompt = INTERVIEW_QUESTION_USER_PROMPT.format(
        role_title=role_data.get("role_title", "Role"),
        seniority_level=role_data.get("seniority_level", "Mid"),
        company_name=company_data.get("company_name", "Company"),
        company_tech_stack=", ".join(company_data.get("tech_stack", [])[:5]),
        candidate_skills=", ".join(resume_data.get("skills", [])[:6]),
        experience_years=resume_data.get("experience_years", 3.0),
        conversation_history=history_str,
        turn_number=current_turn_number + 1,
        total_questions=new_planned_total,
        target_topic=next_topic,
        difficulty=next_diff
    )

    llm_step: StepNextQuestionResponse = await llm_client.generate_json(
        prompt=prompt,
        schema_cls=StepNextQuestionResponse,
        system_prompt=INTERVIEW_QUESTION_SYSTEM_PROMPT
    )

    next_q_resp = InterviewQuestionResponse(
        session_id=session_id,
        turn_number=current_turn_number + 1,
        total_questions=new_planned_total,
        question=llm_step.next_question,
        topic=llm_step.topic or next_topic,
        difficulty=next_diff,
        is_final=llm_step.is_final or False,
        reason=adaptation_reason
    )

    return eval_result, next_q_resp
