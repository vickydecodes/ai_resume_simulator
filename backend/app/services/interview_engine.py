import asyncio
import logging
from typing import Dict, Any, Tuple, List
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
from app.services.question_bank import detect_role_category, get_questions_for_track

logger = logging.getLogger("uvicorn.error")

TOPIC_ROTATION = [
    "Quantitative Logic & Capacity Sizing",
    "System Concurrency & Architecture",
    "Distributed Data & Resilient Caching",
    "Technical Trade-offs & Leadership",
    "Executive Incident Communication",
    "Algorithmic Implementation & Problem Solving"
]

def detect_role_track(role_title: str, required_skills: list = None) -> str:
    """Detect whether the role is technical, non-technical, or product/analytical."""
    combined = (role_title + " " + " ".join(required_skills or [])).lower()
    non_tech_keywords = [
        "marketing", "sales", "hr", "human resources", "recruiter", "talent",
        "operations", "content", "copywriter", "finance", "accountant",
        "business development", "customer success", "support", "community",
        "legal", "compliance", "administrative", "public relations", "pr manager"
    ]
    product_keywords = [
        "product manager", "project manager", "scrum", "agile coach",
        "data analyst", "business analyst", "ui/ux", "designer", "product owner"
    ]
    if any(k in combined for k in non_tech_keywords):
        return "non_technical"
    elif any(k in combined for k in product_keywords):
        return "product_analytical"
    return "technical"

def get_stage_for_turn(turn_number: int, total_questions: int, role_track: str) -> Dict[str, Any]:
    """
    Calculate the active interview stage, question format, and focus topic based on turn progression and role track.
    Evenly distributes the 4 standard interview rounds across the total planned questions:
    - Round 1: Aptitude & Quantitative Logic (MCQ)
    - Round 2: Core Technical & Domain Knowledge (MCQ)
    - Round 3: Situational Leadership & Professional Communication / Email (Scenario / Email)
    - Round 4: Practical Hands-on Challenge (Coding / Applied Case)
    """
    t = max(1, min(turn_number, total_questions))

    # Calculate partition boundaries for the 4 rounds
    p1 = max(1, round(total_questions * 0.25))
    p2 = max(p1 + 1, round(total_questions * 0.50))
    p3 = max(p2 + 1, round(total_questions * 0.75))

    if role_track == "non_technical":
        if t <= p1:
            return {
                "stage_title": "Round 1: Numerical Reasoning & Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "target_topic": "Business Math, Quantitative Estimation & Logic"
            }
        elif t <= p2:
            return {
                "stage_title": "Round 2: Domain Strategy & Role Knowledge",
                "stage_category": "mcq",
                "question_type": "mcq",
                "target_topic": "Domain Best Practices, KPIs, Funnels & Compliance"
            }
        elif t <= p3:
            return {
                "stage_title": "Round 3: Professional Business Communication",
                "stage_category": "email_writing",
                "question_type": "email_writing" if t % 2 == 0 else "communication",
                "target_topic": "Executive & Client Communication Draft"
            }
        else:
            return {
                "stage_title": "Round 4: Strategic Scenario & Crisis Resolution",
                "stage_category": "communication",
                "question_type": "communication",
                "target_topic": "Crisis Resolution & High-Stakes Negotiation"
            }

    elif role_track == "product_analytical":
        if t <= p1:
            return {
                "stage_title": "Round 1: Analytical Logic & Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "target_topic": "Critical Logic, Metric Analysis & Estimation"
            }
        elif t <= p2:
            return {
                "stage_title": "Round 2: Product Strategy & Domain Knowledge",
                "stage_category": "mcq",
                "question_type": "mcq",
                "target_topic": "Product Metrics, User Journeys & Unit Economics"
            }
        elif t <= p3:
            return {
                "stage_title": "Round 3: Stakeholder Alignment & Leadership",
                "stage_category": "communication",
                "question_type": "email_writing" if t % 2 == 0 else "communication",
                "target_topic": "Feature Prioritization & Cross-Functional Alignment"
            }
        else:
            return {
                "stage_title": "Round 4: Practical PRD & Launch Challenge",
                "stage_category": "communication",
                "question_type": "communication",
                "target_topic": "Execution Plan & Go-To-Market Case"
            }

    else:  # Technical track (Software Engineer, Fullstack, DevOps, Data Engineer, etc.)
        if t <= p1:
            return {
                "stage_title": "Round 1: Aptitude & Logical Reasoning",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "target_topic": "Quantitative Logic & Capacity Estimation"
            }
        elif t <= p2:
            return {
                "stage_title": "Round 2: Core Technical & Architecture MCQs",
                "stage_category": "mcq",
                "question_type": "mcq",
                "target_topic": "Tech Stack Internals, Concurrency & API Architecture"
            }
        elif t <= p3:
            return {
                "stage_title": "Round 3: Behavioral & Engineering Communication",
                "stage_category": "communication",
                "question_type": "email_writing" if t % 2 == 0 else "communication",
                "target_topic": "System Trade-offs, Incident Management & Team Alignment"
            }
        else:
            return {
                "stage_title": "Round 4: Hands-on Practical Coding Challenge",
                "stage_category": "coding",
                "question_type": "coding",
                "target_topic": "Algorithms, Data Structures & Implementation"
            }

def calculate_initial_planned_questions(seniority: str) -> int:
    """Calculate default total interview length based on role seniority calibration."""
    sen_lower = (seniority or "").lower()
    if "junior" in sen_lower or "entry" in sen_lower:
        return 6
    elif "senior" in sen_lower or "lead" in sen_lower or "staff" in sen_lower:
        return 10
    else:
        return 8  # Mid-level default

def decide_adaptation(
    current_turn: int,
    current_planned_total: int,
    current_difficulty: int,
    last_turn_score: float,
    all_turn_scores: list = None
) -> Tuple[int, int, bool, str]:
    """
    Execute adaptive rules engine logic:
    Returns (next_difficulty, new_planned_total, is_final, reason).
    """
    next_diff = current_difficulty
    if last_turn_score >= 80:
        next_diff = min(5, current_difficulty + 1)
    elif last_turn_score <= 45:
        next_diff = max(1, current_difficulty - 1)

    new_total = current_planned_total
    is_final = (current_turn >= new_total)
    reason = "Interview loop completed" if is_final else f"Advancing to Turn {current_turn + 1} of {new_total}"
    return next_diff, new_total, is_final, reason


async def generate_turn_question(
    session_data: Dict[str, Any],
    turn_number: int,
    total_planned: int,
    difficulty: int
) -> StepNextQuestionResponse:
    """Generate question step for a specified turn number with rich conversation context."""
    turns = session_data.get("turns", [])
    role_data = session_data.get("role_analysis", {})
    resume_data = session_data.get("resume_analysis", {})
    company_data = session_data.get("company_info", {})

    role_title = role_data.get("role_title", "Software Engineer")
    seniority = role_data.get("seniority_level", "Mid")
    company_name = company_data.get("company_name", "Target Company")
    company_tech = ", ".join(company_data.get("tech_stack", [])[:5]) or "Distributed Web Platforms"
    candidate_skills = ", ".join(resume_data.get("skills", [])[:6]) or "Software Engineering"
    experience_years = resume_data.get("experience_years", 3.0)

    role_track = detect_role_track(role_title, role_data.get("required_skills", []))
    stage_info = get_stage_for_turn(turn_number, total_planned, role_track)

    # Build conversation context from previous turns
    history_lines = []
    for t in turns[-3:]:
        q_txt = t.get("question", "")
        a_txt = (t.get("user_answer") or "")[:250]
        if q_txt:
            history_lines.append(f"Interviewer: {q_txt}\nCandidate: {a_txt}")
    history_str = "\n\n".join(history_lines) if history_lines else "Opening round of assessment."

    prompt = INTERVIEW_QUESTION_USER_PROMPT.format(
        role_title=role_title,
        seniority_level=seniority,
        company_name=company_name,
        company_tech_stack=company_tech,
        candidate_skills=candidate_skills,
        experience_years=experience_years,
        conversation_history=history_str,
        turn_number=turn_number,
        total_questions=total_planned,
        stage_title=stage_info["stage_title"],
        stage_category=stage_info["stage_category"],
        question_type=stage_info["question_type"],
        target_topic=stage_info["target_topic"],
        difficulty=difficulty
    )

    llm_step: StepNextQuestionResponse = await llm_client.generate_json(
        prompt=prompt,
        schema_cls=StepNextQuestionResponse,
        system_prompt=INTERVIEW_QUESTION_SYSTEM_PROMPT
    )

    return llm_step

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

    role_track = detect_role_track(role_title, role_data.get("required_skills", []))
    stage_info = get_stage_for_turn(1, total_planned, role_track)

    session_data = {
        "session_id": session_id,
        "turns": [],
        "role_analysis": role_data,
        "resume_analysis": resume_data,
        "company_info": company_data,
        "total_questions_planned": total_planned,
        "current_difficulty": 3
    }

    result = await generate_turn_question(
        session_data=session_data,
        turn_number=1,
        total_planned=total_planned,
        difficulty=3
    )

    q_type = result.question_type or stage_info["question_type"]
    options = result.options

    # Ensure MCQ options are present if question_type is mcq
    if q_type == "mcq" and (not options or len(options) < 2):
        options = [
            "A) Approximately 45%",
            "B) Approximately 175% (the monthly error budget was depleted and breached)",
            "C) Approximately 88%",
            "D) Approximately 22%"
        ]

    return InterviewQuestionResponse(
        session_id=session_id,
        turn_number=1,
        total_questions=total_planned,
        question=result.next_question,
        topic=result.topic or stage_info["target_topic"],
        difficulty=3,
        stage_title=result.stage_title or stage_info["stage_title"],
        stage_category=result.stage_category or stage_info["stage_category"],
        question_type=q_type,
        options=options,
        coding_starter_code=result.coding_starter_code,
        coding_language=result.coding_language,
        email_context=result.email_context,
        is_final=False,
        reason="Opening round of structured interview loop"
    )

async def evaluate_candidate_answer(
    question_asked: str,
    raw_user_answer: str,
    role_data: Dict[str, Any]
) -> AnswerEvaluationResult:
    """Evaluate candidate answer objectively against rubric."""
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

async def process_turn_and_get_next_question(
    session_data: Dict[str, Any],
    raw_user_answer: str
) -> Tuple[AnswerEvaluationResult, InterviewQuestionResponse]:
    """
    Process candidate answer with concurrent evaluation and next question generation via asyncio.gather.
    Ensures stable question count progression across all 4 stages without premature termination.
    """
    session_id = session_data["session_id"]
    turns = session_data.get("turns", [])
    current_planned = session_data.get("total_questions_planned", 8)
    current_difficulty = session_data.get("current_difficulty", 3)

    last_turn_data = turns[-1] if turns else {"turn_number": 1, "question": "Describe your background."}
    completed_turn_number = last_turn_data.get("turn_number", len(turns))
    question_asked = last_turn_data.get("question", "")

    # Check if this was the final planned question
    is_final_turn = (completed_turn_number >= current_planned)

    if is_final_turn:
        # Evaluate the final turn response
        eval_result = await evaluate_candidate_answer(
            question_asked=question_asked,
            raw_user_answer=raw_user_answer,
            role_data=session_data.get("role_analysis", {})
        )
        final_resp = InterviewQuestionResponse(
            session_id=session_id,
            turn_number=completed_turn_number,
            total_questions=current_planned,
            question="Thank you! You have successfully completed all stages of the mock interview loop. We are compiling your comprehensive performance report.",
            topic="Interview Completed",
            difficulty=current_difficulty,
            is_final=True,
            reason="All planned interview stages completed."
        )
        return eval_result, final_resp

    # Advance to next turn strictly (1 -> 2 -> 3 -> ... -> N)
    next_turn_number = completed_turn_number + 1

    # CRITICAL PERFORMANCE REQUIREMENT: Execute evaluation and next question generation concurrently via asyncio.gather
    eval_task = evaluate_candidate_answer(
        question_asked=question_asked,
        raw_user_answer=raw_user_answer,
        role_data=session_data.get("role_analysis", {})
    )
    next_q_task = generate_turn_question(
        session_data=session_data,
        turn_number=next_turn_number,
        total_planned=current_planned,
        difficulty=current_difficulty
    )

    eval_result, llm_step = await asyncio.gather(eval_task, next_q_task)

    # Adaptive difficulty calibration for the next turn
    if eval_result.turn_score >= 80:
        next_diff = min(5, current_difficulty + 1)
    elif eval_result.turn_score <= 45:
        next_diff = max(1, current_difficulty - 1)
    else:
        next_diff = current_difficulty

    role_data = session_data.get("role_analysis", {})
    role_track = detect_role_track(role_data.get("role_title", "Role"), role_data.get("required_skills", []))
    stage_info = get_stage_for_turn(next_turn_number, current_planned, role_track)

    q_type = llm_step.question_type or stage_info["question_type"]
    options = llm_step.options

    # Ensure MCQ options exist if type is mcq
    if q_type == "mcq" and (not options or len(options) < 2):
        options = [
            "A) It optimizes CPU cache locality and registers.",
            "B) It isolates execution to separate asynchronous workers.",
            "C) It halts the main runtime thread, degrading overall throughput.",
            "D) It only affects background queue tasks without degrading response latency."
        ]

    # Ensure coding starter code if coding
    coding_starter = llm_step.coding_starter_code
    coding_lang = llm_step.coding_language or "python"
    if q_type == "coding" and not coding_starter:
        coding_starter = "def solution(data):\n    # Implement your algorithm here\n    pass"

    # Ensure email context if email_writing
    email_ctx = llm_step.email_context
    if q_type == "email_writing" and not email_ctx:
        email_ctx = {
            "recipient": "Senior Stakeholder / Client Lead",
            "scenario": "Address deliverable adjustments and propose immediate resolution path",
            "required_tone": "Professional, empathetic, and action-oriented"
        }

    next_q_resp = InterviewQuestionResponse(
        session_id=session_id,
        turn_number=next_turn_number,
        total_questions=current_planned,
        question=llm_step.next_question,
        topic=llm_step.topic or stage_info["target_topic"],
        difficulty=next_diff,
        stage_title=llm_step.stage_title or stage_info["stage_title"],
        stage_category=llm_step.stage_category or stage_info["stage_category"],
        question_type=q_type,
        options=options,
        coding_starter_code=coding_starter,
        coding_language=coding_lang,
        email_context=email_ctx,
        is_final=False,
        reason=f"Advancing to Turn {next_turn_number} of {current_planned}"
    )

    return eval_result, next_q_resp

def is_non_tech_role(role_title: str) -> bool:
    role_lower = role_title.lower()
    non_tech_keywords = [
        "sales", "account executive", "bdr", "sdr", "business development",
        "marketing", "human resources", "hr", "recruiter", "talent",
        "customer success", "csm", "account manager", "operations", "finance",
        "sales manager", "sales representative", "client relations"
    ]
    return any(k in role_lower for k in non_tech_keywords)

def generate_all_questions_for_session(session_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate all 20 interview questions upfront (10 Aptitude & 10 Role/Technical questions).
    Adapts strictly between Tech roles and Non-Tech roles (such as Sales, Marketing, etc.).
    Coding rounds and terminal shells are eliminated in favor of high-clarity multiple-choice
    and architectural scenarios with complete rationales and company profile integration.
    """
    role_data = session_data.get("role_analysis", {})
    company_data = session_data.get("company_info", {})
    role_title = role_data.get("role_title", "Target Role")
    company_name = company_data.get("company_name", "Target Company")
    total_planned = session_data.get("total_questions_planned", 20)
    turns = session_data.get("turns", [])
    turns_by_num = {t.get("turn_number"): t for t in turns}
    diff_setting = session_data.get("difficulty_level", "medium").lower()
    calibrated_diff = 4 if diff_setting == "hard" else (2 if diff_setting in ["low", "easy"] else 3)
    track = detect_role_category(role_title)

    if track in ["pm", "data", "finance"]:
        questions_pool = get_questions_for_track(track, role_title, company_name)
    elif track == "sales":
        # =========================================================================
        # NON-TECH / SALES PROFILE: 10 Business Aptitude + 10 Domain Sales Questions
        # =========================================================================
        questions_pool = [
            # --- 10 APTITUDE / BUSINESS REASONING QUESTIONS (1 to 10) ---
            {
                "turn_number": 1,
                "stage_title": "Round 1: Business Aptitude & Numerical Reasoning",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Annual Quota & Pipeline Coverage Calculation",
                "question": f"At {company_name}, an Enterprise Account Executive carries an annual quota of $1,200,000 Net ARR. If your historical win rate from qualified Stage-2 discovery to closed-won is 25%, what is the minimum qualified pipeline coverage required entering Q1 to ensure quota achievement?",
                "options": [
                    "A) $2,400,000 (2x pipeline coverage)",
                    "B) $3,600,000 (3x pipeline coverage)",
                    "C) $4,800,000 (4x pipeline coverage)",
                    "D) $1,500,000 (1.25x pipeline coverage)"
                ],
                "correct_option": "C",
                "correct_answer_explanation": "With a 25% win rate (1 in 4 deals closed), quota attainment requires 1 / 0.25 = 4x pipeline coverage. For a $1.2M quota, 4 * $1.2M = $4,800,000 in qualified pipeline.",
                "company_context": f"{company_name}'s enterprise go-to-market model relies on maintaining minimum 3.5x to 4x pipeline coverage per quota-carrying rep."
            },
            {
                "turn_number": 2,
                "stage_title": "Round 1: Business Aptitude & Numerical Reasoning",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Net Revenue Retention (NRR) & Expansion Economics",
                "question": f"Suppose {company_name} begins the fiscal year with $10,000,000 in existing Annual Recurring Revenue (ARR). Over the year, existing customer expansions generate $2,000,000, while customer downgrades account for $300,000 and cancellations account for $500,000. What is {company_name}'s Net Revenue Retention (NRR) rate for the year?",
                "options": [
                    "A) 112%",
                    "B) 120%",
                    "C) 108%",
                    "D) 92%"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "NRR = (Starting ARR + Expansion - Downgrades - Churn) / Starting ARR. Here: ($10M + $2M - $0.3M - $0.5M) / $10M = $11.2M / $10M = 112%.",
                "company_context": f"Top-tier B2B enterprise software companies like {company_name} target NRR benchmarks above 110-120%."
            },
            {
                "turn_number": 3,
                "stage_title": "Round 1: Business Aptitude & Numerical Reasoning",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Customer Acquisition Cost (CAC) Payback Period",
                "question": f"At {company_name}, acquiring a new enterprise customer costs $90,000 across marketing and sales expenses (CAC). The customer signs an annual contract of $150,000 with an 80% gross margin. What is the CAC payback period in months?",
                "options": [
                    "A) 6.0 months",
                    "B) 9.0 months",
                    "C) 12.0 months",
                    "D) 15.0 months"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Annual gross profit per customer = $150,000 * 80% = $120,000/year = $10,000/month. CAC payback = $90,000 / $10,000 per month = 9.0 months.",
                "company_context": f"SaaS sales sustainability at {company_name} mandates CAC payback periods under 12 months for enterprise deals."
            },
            {
                "turn_number": 4,
                "stage_title": "Round 1: Business Aptitude & Numerical Reasoning",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Discounting & Sales Deal Gross Margin Impact",
                "question": f"A prospect negotiating with {company_name} requests a 20% discount on a $200,000 enterprise software subscription (list price). If {company_name}'s cost to deliver and support the service is fixed at $40,000, by what percentage does the Rep's deal gross profit decrease if the 20% discount is granted?",
                "options": [
                    "A) Exactly 20%",
                    "B) Exactly 25%",
                    "C) Exactly 33.3%",
                    "D) Exactly 15%"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "At list price, gross profit = $200k - $40k = $160,000. With a 20% discount, selling price = $160k, so gross profit = $160k - $40k = $120,000. The profit drop is ($160k - $120k)/$160k = $40k/$160k = 25%.",
                "company_context": f"Understanding gross margin leverage enables reps at {company_name} to defend price points effectively."
            },
            {
                "turn_number": 5,
                "stage_title": "Round 1: Business Aptitude & Numerical Reasoning",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Sales Velocity & Deal Throughput Formula",
                "question": f"Sales Velocity is calculated as: (Number of Opportunities * Average Deal Size * Win Rate) / Sales Cycle Length in days. If {company_name}'s team has 40 opportunities, an average deal size of $50,000, a 20% win rate, and an average sales cycle of 80 days, what is the daily sales velocity?",
                "options": [
                    "A) $5,000 / day",
                    "B) $10,000 / day",
                    "C) $2,500 / day",
                    "D) $15,000 / day"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Velocity = (40 * $50,000 * 0.20) / 80 = $400,000 / 80 = $5,000 per day.",
                "company_context": f"{company_name}'s sales leadership monitors sales velocity to forecast quarterly quota reliability."
            },
            {
                "turn_number": 6,
                "stage_title": "Round 1: Business Aptitude & Numerical Reasoning",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Multi-Year Contract Pre-payment & Cash Flow Modeling",
                "question": f"A customer at {company_name} is deciding between paying $100,000 annually for 3 years ($300,000 total) or paying upfront for all 3 years with an 8% pre-payment discount. What is the upfront discounted contract value received by {company_name}?",
                "options": [
                    "A) $276,000",
                    "B) $292,000",
                    "C) $268,000",
                    "D) $284,000"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Total 3-year undiscounted contract = 3 * $100,000 = $300,000. An 8% discount reduces the price by $24,000: $300,000 * 0.92 = $276,000.",
                "company_context": f"Multi-year upfront payments accelerate free cash flow for {company_name}."
            },
            {
                "turn_number": 7,
                "stage_title": "Round 1: Business Aptitude & Numerical Reasoning",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Inbound Lead Funnel Conversion & Meeting Generation",
                "question": f"During a monthly digital campaign at {company_name}, 2,000 marketing qualified leads (MQLs) are generated. The SDR team connects with 15% of MQLs. Of those connected, 40% agree to an initial executive discovery meeting. If 75% of those meetings actually show up and qualify, how many qualified Sales Accepted Opportunities (SAOs) are produced?",
                "options": [
                    "A) 90 SAOs",
                    "B) 120 SAOs",
                    "C) 60 SAOs",
                    "D) 150 SAOs"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Connected leads = 2,000 * 0.15 = 300. Meetings booked = 300 * 0.40 = 120. Qualified SAOs completed = 120 * 0.75 = 90 SAOs.",
                "company_context": f"Funnel conversion tracking allows {company_name} reps to budget outbound vs inbound deal volumes."
            },
            {
                "turn_number": 8,
                "stage_title": "Round 1: Business Aptitude & Numerical Reasoning",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Sales Commission Accelerator Tier Logic",
                "question": f"At {company_name}, your compensation plan pays 10% commission on revenue up to 100% of quota ($1,000,000), and an accelerated 20% commission on any revenue closed above 100% of quota. If you close $1,400,000 in total revenue for the year, what is your total earned commission payout?",
                "options": [
                    "A) $140,000",
                    "B) $180,000",
                    "C) $280,000",
                    "D) $160,000"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Base commission on first $1,000,000 = $1,000,000 * 10% = $100,000. Accelerator commission on excess $400,000 = $400,000 * 20% = $80,000. Total payout = $100,000 + $80,000 = $180,000.",
                "company_context": f"Standard B2B enterprise accelerator plans incentivize over-performance beyond 100% quota attainment."
            },
            {
                "turn_number": 9,
                "stage_title": "Round 1: Business Aptitude & Numerical Reasoning",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Customer Lifetime Value (LTV) to CAC Ratio",
                "question": f"If an enterprise client at {company_name} generates $60,000 in annual gross profit with an expected annual churn rate of 10% (implied customer lifetime of 10 years), and the total cost to acquire the client (CAC) is $120,000, what is the LTV:CAC ratio?",
                "options": [
                    "A) 3:1",
                    "B) 5:1",
                    "C) 2:1",
                    "D) 7.5:1"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "LTV = Annual Gross Profit / Churn Rate = $60,000 / 0.10 = $600,000. LTV:CAC Ratio = $600,000 / $120,000 = 5:1.",
                "company_context": f"Healthy enterprise SaaS economics at {company_name} target an LTV:CAC ratio of at least 3:1 to 5:1."
            },
            {
                "turn_number": 10,
                "stage_title": "Round 1: Business Aptitude & Numerical Reasoning",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Sales Territory Opportunity Sizing & Win Allocation",
                "question": f"In your assigned enterprise sales territory at {company_name}, there are 200 target Tier-1 enterprise logos. If {company_name} currently penetrates 15% of these accounts, and market research indicates 40% of the remaining unpenetrated accounts will evaluate a solution this year, how many active evaluation opportunities exist in your territory this year?",
                "options": [
                    "A) 68 accounts",
                    "B) 80 accounts",
                    "C) 52 accounts",
                    "D) 34 accounts"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Current customers = 200 * 0.15 = 30 accounts. Remaining unpenetrated = 200 - 30 = 170 accounts. Active evaluations this year = 170 * 40% = 68 accounts.",
                "company_context": f"Territory planning at {company_name} focuses on segmenting addressable whitespace in key strategic verticals."
            },

            # --- 10 DOMAIN SALES & STRATEGIC EXECUTION QUESTIONS (11 to 20) ---
            {
                "turn_number": 11,
                "stage_title": "Round 2: Strategic Sales & Client Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "MEDDPICC Qualification: Identifying the Economic Buyer",
                "question": f"When executing an enterprise opportunity for {role_title} at {company_name}, your champion is a Senior Director who loves the product but cannot sign off on capital expenditures above $100K. According to the MEDDPICC framework, what is your immediate strategic next step?",
                "options": [
                    "A) Send a formal contract immediately and hope the Director gets budget approval later",
                    "B) Partner with your Champion to map out the business case and co-present directly to the Economic Buyer (C-level/VP with P&L sign-off)",
                    "C) Offer a 50% discount to force the deal below the Director's $100K authorization threshold",
                    "D) Pause all sales communication until the Director contacts you with final board authorization"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "In enterprise sales, deals stall when reps mistake a Champion for an Economic Buyer. A top enterprise rep arms the Champion with ROI metrics and gains direct executive alignment.",
                "company_context": f"At {company_name}, multi-threaded engagement with the true Economic Buyer is required for predictable deal closure."
            },
            {
                "turn_number": 12,
                "stage_title": "Round 2: Strategic Sales & Client Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Enterprise Objection Handling: Defending Value vs Price Resistance",
                "question": f"During final negotiations at {company_name}, the prospect's procurement director states: 'Your solution is 30% more expensive than your top competitor. Match their price or we are going with them.' How should you respond?",
                "options": [
                    "A) Immediately match the competitor's price to preserve the booking volume",
                    "B) Re-anchor on the verified business metrics and unaddressed risks the competitor cannot fulfill, then trade concessions (e.g. multi-year term or case study) for any modest pricing adjustment",
                    "C) Criticize the competitor's leadership team and claim they are going out of business",
                    "D) Refuse to speak with procurement and only email the CEO directly"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Never discount without getting value in return. Re-anchoring on ROI and trading concessions (longer commitment, logo rights, payment terms) protects contract profitability.",
                "company_context": f"{company_name}'s market reputation is built on superior product ROI and reliability rather than commoditized price-cutting."
            },
            {
                "turn_number": 13,
                "stage_title": "Round 2: Strategic Sales & Client Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Multi-Threaded Account Management & Consensus Building",
                "question": f"In an enterprise deal at {company_name}, the Head of Engineering supports your platform, but the Chief Information Security Officer (CISO) and Legal counsel raise unexpected compliance concerns. What is the most effective approach?",
                "options": [
                    "A) Ignore the CISO and urge the Head of Engineering to override them",
                    "B) Proactively schedule a dedicated security & compliance session with {company_name}'s technical architects and security team to address SOC2/ISO/GDPR requirements directly",
                    "C) Send a 200-page generic security document via email and demand they sign off within 48 hours",
                    "D) Drop the opportunity and focus exclusively on accounts without security teams"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Enterprise SaaS deals require multi-threading. Bringing in internal security specialists to collaborate directly with the customer's CISO turns potential blockers into confident partners.",
                "company_context": f"Security and regulatory compliance are primary enterprise gating criteria for all deployments at {company_name}."
            },
            {
                "turn_number": 14,
                "stage_title": "Round 2: Strategic Sales & Client Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Competitive Displacement Strategy",
                "question": f"A target enterprise account is currently locked into an incumbent competitor's contract for another 9 months. What is the best strategic play as an Enterprise Rep at {company_name}?",
                "options": [
                    "A) Wait 8 months before contacting them so you don't waste time",
                    "B) Initiate strategic discovery now, uncover pain points with their existing deployment, build champion relationships, and propose a transition plan or deferred billing schedule",
                    "C) Encourage the customer to breach their contract immediately and promise to pay their legal fees",
                    "D) Send unsolicited daily cold emails until their existing contract expires"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Enterprise displacement cycles take 6 to 9 months. Seeding the value proposition and establishing relationships before RFP kickoff ensures {company_name} is in pole position when the renewal window opens.",
                "company_context": f"Competitive displacements at {company_name} succeed through early relationship architecture and quantifiable operational differentiation."
            },
            {
                "turn_number": 15,
                "stage_title": "Round 2: Strategic Sales & Client Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Executive Discovery: Uncovering Business Pain vs Feature Requests",
                "question": f"During a first executive discovery call with a prospect, they state: 'We need a dashboard with automated CSV export.' As a consultative seller at {company_name}, how should you proceed?",
                "options": [
                    "A) Say 'Yes, we have CSV export,' and proceed to demo the feature immediately",
                    "B) Probe deeper by asking what business outcome or decision depends on that data, how many hours are currently lost compiling it, and what happens if those reports are inaccurate",
                    "C) Tell the prospect that CSV exports are obsolete and they should only use APIs",
                    "D) Hand the deal off to customer support to answer the feature question"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Consultative selling uncovers the business problem behind the feature request. Asking why they need it reveals executive metrics, urgency, and the true commercial value.",
                "company_context": f"At {company_name}, enterprise reps sell strategic business outcomes rather than commoditized point features."
            },
            {
                "turn_number": 16,
                "stage_title": "Round 2: Strategic Sales & Client Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Mutual Action Plan (MAP) Execution",
                "question": f"To prevent deal slippage at end of quarter at {company_name}, what is the purpose of a Mutual Action Plan (MAP)?",
                "options": [
                    "A) A document listing reps' personal quota goals to guilt the customer into signing",
                    "B) A shared, chronological project plan establishing required milestones (technical validation, legal redlines, security sign-off, board approval) with assigned owners and target dates on both sides",
                    "C) An internal-only document hidden from the customer until after contract execution",
                    "D) A formal non-disclosure agreement required before sharing product pricing"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "A Mutual Action Plan (MAP) creates shared accountability between buyer and seller, establishing exact dates for procurement, security, legal, and final executive sign-off.",
                "company_context": f"Predictable revenue delivery at {company_name} requires rigorous MAP alignment on all six-figure enterprise deals."
            },
            {
                "turn_number": 17,
                "stage_title": "Round 2: Strategic Sales & Client Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Post-Demo Momentum & Next Step Commitment",
                "question": f"You just concluded a successful demonstration of {company_name}'s platform to the prospect's team. They say: 'This looks fantastic, send us some info and we will be in touch.' How do you respond?",
                "options": [
                    "A) Say 'Thank you!' and wait for them to reach out when they are ready",
                    "B) Acknowledge the positive feedback, summarize the key value items discussed, and secure a firm calendar date and agenda for the next milestone (e.g. scoping with technical leads)",
                    "C) Call them every morning at 8 AM until they reply to your email",
                    "D) Demand that they sign a letter of intent before leaving the Zoom room"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Never end a meeting without a firm next step on the calendar. Leaving the next action open-ended is the leading cause of deal stall in B2B sales cycles.",
                "company_context": f"{company_name}'s high-performing sales professionals maintain strict calendar momentum on every active engagement."
            },
            {
                "turn_number": 18,
                "stage_title": "Round 2: Strategic Sales & Client Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "CRM Pipeline Hygiene & Forecast Accuracy",
                "question": f"In {company_name}'s CRM forecasting review, what is the key difference between an opportunity marked as 'Commit' versus 'Best Case'?",
                "options": [
                    "A) Commit deals have signed contracts already; Best Case deals are cold leads",
                    "B) Commit deals have complete economic buyer alignment, cleared legal/security milestones, and a verified mutual close date within the current quarter; Best Case deals still have an outstanding risk or unverified dependency",
                    "C) Commit deals have been discounted by 50%; Best Case deals are full price",
                    "D) There is no difference; both categories are identical in sales operations"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Commit represents a locked forecast backed by verified milestones and zero outstanding gating obstacles. Best Case contains upside that could close if all stars align.",
                "company_context": f"Executive credibility and resource planning at {company_name} depend on accurate quarterly Commit forecasting."
            },
            {
                "turn_number": 19,
                "stage_title": "Round 2: Strategic Sales & Client Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "Land-and-Expand Strategy & Account Penetration",
                "question": f"At {company_name}, an existing enterprise client purchased 200 user licenses last year. Their company just expanded into a new subsidiary with 1,500 additional employees. How do you execute the expansion opportunity?",
                "options": [
                    "A) Wait for their annual renewal in 10 months to mention the new subsidiary",
                    "B) Review their existing license utilization, interview internal power users for ROI metrics, and arrange an executive introduction to the new subsidiary's leadership showcasing proven internal success",
                    "C) Cold call the new subsidiary pretending you do not work with their parent company",
                    "D) Disable the existing 200 licenses to force a meeting with executive leadership"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Land-and-expand leverages verified internal case studies and enthusiastic champions from the initial deployment to accelerate adoption across sister divisions.",
                "company_context": f"Enterprise account growth at {company_name} is fueled by multi-division expansion across large corporate portfolios."
            },
            {
                "turn_number": 20,
                "stage_title": "Round 2: Strategic Sales & Client Execution",
                "stage_category": "domain",
                "question_type": "mcq",
                "topic": "End-of-Quarter Deal Slippage Contingency Planning",
                "question": f"It is 5 days before the end of Q4 at {company_name}. A $300,000 deal in your Commit forecast encounters an unexpected legal bottleneck regarding indemnity clauses. What is the most effective action?",
                "options": [
                    "A) Concede all indemnity liability without consulting your company's general counsel",
                    "B) Coordinate an immediate live redline call between your in-house legal counsel, the customer's attorney, and the Economic Buyer to negotiate a standard middle-ground language clause",
                    "C) Threaten the prospect that you will cancel their order if they do not sign today",
                    "D) Remove the deal from your forecast without attempting resolution"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Email exchanges between lawyers drag on for weeks. A live attorney-to-attorney negotiation call with business leaders present resolves indemnity impasses in hours.",
                "company_context": f"High-stakes quarter-end closing at {company_name} requires decisive leadership in facilitating cross-functional consensus."
            }
        ]

    else:
        # =========================================================================
        # TECH PROFILE: 10 Analytical Aptitude + 10 Technical Architecture Questions
        # =========================================================================
        questions_pool = [
            # --- 10 APTITUDE / ANALYTICAL REASONING QUESTIONS (1 to 10) ---
            {
                "turn_number": 1,
                "stage_title": "Round 1: Numerical Reasoning & Analytical Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "SLA & Outage Error Budget Depletion",
                "question": f"At {company_name}, our core production infrastructure operates under a 99.95% monthly uptime SLA (~43,200 total minutes in a 30-day billing cycle). If an unexpected service degradation outage lasts for 38 minutes before automated remediation restores traffic, approximately what percentage of the monthly allowable error budget was consumed by this incident?",
                "options": [
                    "A) Approximately 45%",
                    "B) Approximately 175% (the entire monthly error budget was depleted and breached)",
                    "C) Approximately 88%",
                    "D) Approximately 22%"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "At 99.95% uptime, allowable downtime = (1 - 0.9995) * 43,200 = 0.0005 * 43,200 = 21.6 minutes. An outage of 38 minutes consumed 38 / 21.6 = 175.9% of the allowable budget, breaching the SLA.",
                "company_context": f"Production engineering at {company_name} utilizes error budgets to balance release velocity with platform availability."
            },
            {
                "turn_number": 2,
                "stage_title": "Round 1: Numerical Reasoning & Analytical Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "System Throughput & In-Memory Redis Sizing",
                "question": f"At {company_name}, a real-time event streaming pipeline ingests 15,000 JSON payloads per second, with an average compressed payload size of 600 bytes. If incoming messages must be buffered in an in-memory Redis cluster for exactly 2 hours before asynchronous cold-storage archival, what is the minimum memory capacity required solely for raw data storage?",
                "options": [
                    "A) Approximately 64.8 GB",
                    "B) Approximately 12.5 GB",
                    "C) Approximately 180.0 GB",
                    "D) Approximately 32.4 GB"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Throughput = 15,000 msgs/sec * 600 bytes = 9,000,000 bytes/sec = 9 MB/sec. Over 2 hours (7,200 seconds): 9 MB/sec * 7,200 sec = 64,800 MB = 64.8 GB.",
                "company_context": f"Capacity modeling is essential when architecting scalable telemetry infrastructure at {company_name}."
            },
            {
                "turn_number": 3,
                "stage_title": "Round 1: Numerical Reasoning & Analytical Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Disk IOPS & Database Transaction Log Sizing",
                "question": f"A write-heavy PostgreSQL cluster at {company_name} executes 4,000 write transactions per second. Each transaction generates an average of 4 KB written to the Write-Ahead Log (WAL). If the storage volume is provisioned for 200 MB/sec sequential write bandwidth, what percentage of the disk's write bandwidth is consumed by WAL writes?",
                "options": [
                    "A) 8.0%",
                    "B) 16.0%",
                    "C) 32.0%",
                    "D) 64.0%"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "WAL throughput = 4,000 * 4 KB = 16,000 KB/sec = 16 MB/sec. Bandwidth utilization = 16 MB/sec / 200 MB/sec = 8.0%.",
                "company_context": f"High write-volume database scaling at {company_name} requires monitoring WAL I/O saturation."
            },
            {
                "turn_number": 4,
                "stage_title": "Round 1: Numerical Reasoning & Analytical Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Network Bandwidth & Payload Compression Savings",
                "question": f"At {company_name}, an API service transmits 50,000,000 responses daily with an uncompressed JSON size of 40 KB. Introducing Brotli/Gzip compression reduces payload size by 75%. Approximately how much egress bandwidth data transfer is saved per 30-day month?",
                "options": [
                    "A) Approximately 45 TB",
                    "B) Approximately 15 TB",
                    "C) Approximately 60 TB",
                    "D) Approximately 90 TB"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Daily savings = 50,000,000 * (40 KB * 0.75) = 50M * 30 KB = 1,500,000,000 KB = 1.5 TB/day. Over 30 days: 1.5 TB * 30 = 45 TB.",
                "company_context": f"Reducing cloud egress bandwidth directly reduces platform operating expenses across {company_name}'s global clusters."
            },
            {
                "turn_number": 5,
                "stage_title": "Round 1: Numerical Reasoning & Analytical Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Cache Hit Ratio & Database Query Load Reduction",
                "question": f"A backend service at {company_name} receives 100,000 requests per minute. Originally, all requests hit the primary database. After deploying a distributed Redis caching layer with an 92% cache hit ratio, how many queries per minute now hit the database?",
                "options": [
                    "A) 8,000 queries/min",
                    "B) 92,000 queries/min",
                    "C) 16,000 queries/min",
                    "D) 4,000 queries/min"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Database queries = Total requests * (1 - Hit Ratio) = 100,000 * (1 - 0.92) = 100,000 * 0.08 = 8,000 queries/min.",
                "company_context": f"Protecting database tiers from query spikes is a primary design pattern across {company_name} microservices."
            },
            {
                "turn_number": 6,
                "stage_title": "Round 1: Numerical Reasoning & Analytical Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Consistent Hashing & Partition Key Distribution",
                "question": f"When partitioning a distributed database across 16 primary shards at {company_name}, an uneven partition key causes one single shard to receive 25% of all traffic while the remaining 15 shards share the rest equally. Approximately what percentage of traffic does each of the other 15 shards handle?",
                "options": [
                    "A) 5.0%",
                    "B) 6.25%",
                    "C) 7.5%",
                    "D) 4.0%"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Remaining traffic = 100% - 25% = 75%. Shared equally across 15 shards: 75% / 15 = 5.0% per shard.",
                "company_context": f"Avoiding partition hotspots is crucial for maintaining low tail latencies in distributed storage at {company_name}."
            },
            {
                "turn_number": 7,
                "stage_title": "Round 1: Numerical Reasoning & Analytical Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Microservices Serial Latency Budget Estimation",
                "question": f"A user checkout request at {company_name} makes 4 synchronous internal service calls sequentially: Auth Service (15ms), Inventory Service (25ms), Payment Gateway (120ms), and Notification Service (40ms). If Payment and Notification can be refactored to execute concurrently using async coroutines, what is the new estimated service latency (excluding network overhead)?",
                "options": [
                    "A) 160ms",
                    "B) 200ms",
                    "C) 120ms",
                    "D) 175ms"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Originally: 15 + 25 + 120 + 40 = 200ms. Executing Payment and Notification concurrently takes max(120, 40) = 120ms. Total = 15 + 25 + 120 = 160ms (saving 40ms).",
                "company_context": f"At {company_name}, optimizing checkout latency directly improves user conversion rates."
            },
            {
                "turn_number": 8,
                "stage_title": "Round 1: Numerical Reasoning & Analytical Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Asynchronous Message Queue Drain Rate Math",
                "question": f"A message queue at {company_name} has accumulated a backlog of 360,000 tasks during an upstream outage. Workers consume tasks at a combined rate of 800 tasks/second, while new tasks continue arriving at 200 tasks/second. How many minutes will it take for the workers to fully clear the backlog?",
                "options": [
                    "A) 10.0 minutes",
                    "B) 7.5 minutes",
                    "C) 15.0 minutes",
                    "D) 12.5 minutes"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Net drain rate = Consumption rate - Arrival rate = 800 - 200 = 600 tasks/sec. Time to drain 360,000 tasks = 360,000 / 600 = 600 seconds = 10.0 minutes.",
                "company_context": f"Queue consumer autoscaling at {company_name} prevents customer notification delays after upstream recoveries."
            },
            {
                "turn_number": 9,
                "stage_title": "Round 1: Numerical Reasoning & Analytical Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Canary Deployment Error Rate Thresholds",
                "question": f"During a canary release at {company_name}, 10% of total production traffic (5,000 requests/sec) is routed to the canary instance. Over a 5-minute sampling window, the canary produces 150 HTTP 500 errors, while the baseline fleet (90% traffic) produces 300 HTTP 500 errors. What is the canary's error rate compared to the baseline fleet's error rate?",
                "options": [
                    "A) Canary error rate is 4.5x higher than baseline",
                    "B) Canary error rate is 2.0x higher than baseline",
                    "C) Canary error rate is identical to baseline",
                    "D) Canary error rate is lower than baseline"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Canary traffic in 5 min = 5,000 * 300 = 1.5M requests. Canary error rate = 150 / 1.5M = 0.01% (100 ppm). Baseline traffic = 45,000 * 300 = 13.5M requests. Baseline error rate = 300 / 13.5M = 0.0022% (22.2 ppm). Ratio = 100 / 22.2 = 4.5x higher.",
                "company_context": f"Automated canary rollback systems at {company_name} trigger when canary error rates exceed baseline tolerances."
            },
            {
                "turn_number": 10,
                "stage_title": "Round 1: Numerical Reasoning & Analytical Aptitude",
                "stage_category": "aptitude",
                "question_type": "mcq",
                "topic": "Horizontal Pod Autoscaler (HPA) Capacity Sizing",
                "question": f"A Kubernetes cluster at {company_name} currently runs 6 pods with average CPU utilization of 85%. The target utilization configured in the Horizontal Pod Autoscaler (HPA) is 60%. Approximately how many total pods will the HPA scale up to in order to meet the target utilization threshold?",
                "options": [
                    "A) 9 pods",
                    "B) 12 pods",
                    "C) 8 pods",
                    "D) 15 pods"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "Desired Pods = ceil(Current Pods * (Current Utilization / Target Utilization)) = ceil(6 * (85 / 60)) = ceil(6 * 1.416) = ceil(8.5) = 9 pods.",
                "company_context": f"Configuring target metric thresholds in Kubernetes ensures reliable elasticity during peak user traffic."
            },

            # --- 10 TECHNICAL ARCHITECTURE & SYSTEMS QUESTIONS (11 to 20) ---
            {
                "turn_number": 11,
                "stage_title": "Round 2: Technical & Domain Architecture",
                "stage_category": "technical",
                "question_type": "mcq",
                "topic": "Asynchronous Concurrency & Event Loop Mechanics",
                "question": f"In an asynchronous backend runtime (such as FastAPI with asyncio or Node.js) at {company_name}, what is the direct architectural consequence of executing an intensive synchronous, CPU-bound cryptographic loop directly within an async route handler without offloading it?",
                "options": [
                    "A) The runtime automatically spawns a background OS thread with no latency impact",
                    "B) It blocks the single main event loop thread, preventing all concurrent coroutines and incoming network requests from progressing until the calculation completes",
                    "C) Only WebSocket connections stall, while REST HTTP requests bypass the handler",
                    "D) The operating system raises an uncatchable SIGKILL signal and terminates the container"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "In cooperative multitasking, CPU-bound synchronous code monopolizes the event loop thread. Async frameworks cannot interleave I/O until the synchronous function yields control or is offloaded via run_in_executor / Celery.",
                "company_context": f"High-throughput API microservices at {company_name} strictly isolate CPU-bound tasks to prevent latency spikes."
            },
            {
                "turn_number": 12,
                "stage_title": "Round 2: Technical & Domain Architecture",
                "stage_category": "technical",
                "question_type": "mcq",
                "topic": "Distributed Caching: Cache Stampede Mitigation",
                "question": f"When scaling a distributed caching layer (Redis) fronting a relational database at {company_name}, which architectural technique is most effective at preventing a 'cache stampede' (thundering herd) when a high-traffic cache key expires?",
                "options": [
                    "A) Setting all Redis key TTL values to zero",
                    "B) Implementing probabilistic early expiration (such as the XFetch algorithm) or acquiring a distributed mutex lock (Redlock) so only a single worker queries the database to rebuild the cache",
                    "C) Increasing database connection pool size to 10,000 connections",
                    "D) Storing all cached state on the client-side browser"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Probabilistic early expiration (XFetch) or distributed locking ensures only one worker rebuilds the expired cache key while others receive stale data or wait, preventing database overload.",
                "company_context": f"{company_name}'s high-traffic catalog and pricing APIs use probabilistic caching to withstand traffic bursts."
            },
            {
                "turn_number": 13,
                "stage_title": "Round 2: Technical & Domain Architecture",
                "stage_category": "technical",
                "question_type": "mcq",
                "topic": "Database Isolation Levels & Anomalies",
                "question": f"In a relational database (PostgreSQL/MySQL) powering financial ledger transactions at {company_name}, which transaction isolation level prevents 'Non-Repeatable Reads' and 'Dirty Reads' but may still permit 'Phantom Reads' unless additional range locks or predicate locks are applied?",
                "options": [
                    "A) Read Uncommitted",
                    "B) Read Committed",
                    "C) Repeatable Read",
                    "D) Serializable"
                ],
                "correct_option": "C",
                "correct_answer_explanation": "Repeatable Read guarantees that data read within a transaction remains consistent across queries, preventing dirty reads and non-repeatable reads. In standard SQL-92, it may permit phantom reads (though Postgres Repeatable Read uses MVCC to prevent phantom reads as well).",
                "company_context": f"Financial ledger consistency at {company_name} requires precise transactional isolation controls."
            },
            {
                "turn_number": 14,
                "stage_title": "Round 2: Technical & Domain Architecture",
                "stage_category": "technical",
                "question_type": "mcq",
                "topic": "Database Indexing: Composite B-Tree Column Ordering",
                "question": f"You create a composite B-Tree index on a table with columns `(tenant_id, created_at, status)`. Which of the following SQL WHERE clauses will NOT be able to utilize this composite index efficiently?",
                "options": [
                    "A) `WHERE tenant_id = '123' AND created_at > '2026-01-01'`",
                    "B) `WHERE created_at > '2026-01-01' AND status = 'active'`",
                    "C) `WHERE tenant_id = '123' AND created_at = '2026-01-01' AND status = 'active'`",
                    "D) `WHERE tenant_id = '123'`"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "B-Tree composite indexes follow the left-to-right prefix rule. Because option B omits the leading indexed column (`tenant_id`), the database engine cannot traverse the index tree efficiently and defaults to a sequential scan.",
                "company_context": f"Multi-tenant database query performance at {company_name} relies on correctly ordered composite indexes."
            },
            {
                "turn_number": 15,
                "stage_title": "Round 2: Technical & Domain Architecture",
                "stage_category": "technical",
                "question_type": "mcq",
                "topic": "Event Streaming: Kafka Partition Ordering Guarantees",
                "question": f"When streaming event records through Apache Kafka at {company_name}, what determines strict FIFO message ordering guarantees across consumer groups?",
                "options": [
                    "A) Kafka guarantees global message ordering across all topics and partitions automatically",
                    "B) Messages are strictly ordered only within a single partition; all messages sharing the same partition key are delivered in exact order to the consumer assigned to that partition",
                    "C) Message ordering is governed solely by client-side browser timestamp sorting",
                    "D) Ordering is only preserved if the Kafka cluster runs on a single broker"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Kafka guarantees ordering only within an individual partition. Publishing messages with a common key (e.g., `user_id` or `order_id`) guarantees they route to the same partition and are consumed in sequence.",
                "company_context": f"Event-driven payment telemetry at {company_name} utilizes partition keys to preserve event order."
            },
            {
                "turn_number": 16,
                "stage_title": "Round 2: Technical & Domain Architecture",
                "stage_category": "technical",
                "question_type": "mcq",
                "topic": "Idempotent API Design & Payment Retry Safety",
                "question": f"At {company_name}, an external client charges a payment via POST `/v1/charges`. If a network timeout occurs between client and server, how does the system prevent accidental duplicate credit card charges during automated retries?",
                "options": [
                    "A) By rejecting all retried requests with HTTP 400 Bad Request",
                    "B) By requiring an `Idempotency-Key` header; storing the initial transaction result in Redis/SQL keyed by the idempotency key, and returning the cached response for identical replayed requests",
                    "C) By converting all POST requests into GET requests",
                    "D) By relying on the user's browser to detect and cancel duplicates"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Idempotency keys allow clients to safely retry requests without risk of creating duplicate transactions. The server records the key and returns the identical response if the request is retransmitted.",
                "company_context": f"Stripe-style idempotency keys are a core industry design pattern implemented across {company_name} APIs."
            },
            {
                "turn_number": 17,
                "stage_title": "Round 2: Technical & Domain Architecture",
                "stage_category": "technical",
                "question_type": "mcq",
                "topic": "Resilience: Circuit Breakers & Cascading Failure Prevention",
                "question": f"In a microservices mesh at {company_name}, an upstream payment gateway begins timing out on 80% of requests. Which resilience pattern should be implemented to protect downstream services from thread starvation and cascading system crashes?",
                "options": [
                    "A) Circuit Breaker pattern (tripping to Open state after error thresholds are breached to fail fast and shed load)",
                    "B) Increasing HTTP connection timeout to 60 seconds",
                    "C) Removing health check endpoints from the cluster",
                    "D) Retrying failed requests infinitely with zero backoff"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "A Circuit Breaker monitors failure rates. When the failure threshold is reached, it opens the circuit, failing fast immediately without holding server sockets, protecting upstream resources.",
                "company_context": f"Microservice resilience at {company_name} utilizes circuit breakers to maintain graceful degradation."
            },
            {
                "turn_number": 18,
                "stage_title": "Round 2: Technical & Domain Architecture",
                "stage_category": "technical",
                "question_type": "mcq",
                "topic": "Zero-Downtime Database Schema Migration",
                "question": f"To rename a column in a high-traffic SQL database table at {company_name} without incurring downtime or locking tables during rolling deployments, what architectural pattern should be followed?",
                "options": [
                    "A) Run `ALTER TABLE ... RENAME COLUMN` directly on the primary database during business hours",
                    "B) The Expand and Contract pattern: add the new column (Expand), dual-write to both columns, backfill legacy rows, update readers, and finally drop the old column (Contract)",
                    "C) Take the entire application offline for 6 hours on the weekend",
                    "D) Create a completely new database and manually copy data via CSV"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "The Expand and Contract (Parallel Run) pattern ensures backward compatibility during rolling deployments. The schema expands to support both versions before contracting once all code is migrated.",
                "company_context": f"Continuous delivery at {company_name} requires all schema migrations to execute with zero downtime."
            },
            {
                "turn_number": 19,
                "stage_title": "Round 2: Technical & Domain Architecture",
                "stage_category": "technical",
                "question_type": "mcq",
                "topic": "Authentication: JWT vs Server-Side Session Trade-offs",
                "question": f"When comparing stateless JSON Web Tokens (JWT) with server-side session stores (Redis) for a high-concurrency microservices platform at {company_name}, what is the primary architectural trade-off of stateless JWTs?",
                "options": [
                    "A) JWTs cannot contain any user identity information",
                    "B) Immediate revocation or invalidation of a compromised JWT before its expiration time requires a centralized revocation blacklist, negating pure statelessness",
                    "C) JWTs can only be transmitted over unencrypted HTTP",
                    "D) JWTs require database queries on every single HTTP request"
                ],
                "correct_option": "B",
                "correct_answer_explanation": "Because JWTs are self-contained and cryptographically verified, revoking an individual token prior to expiration requires checking a shared revocation list (e.g. in Redis), introducing state.",
                "company_context": f"Auth architecture at {company_name} balances stateless token performance with security revocation controls."
            },
            {
                "turn_number": 20,
                "stage_title": "Round 2: Technical & Domain Architecture",
                "stage_category": "technical",
                "question_type": "mcq",
                "topic": "Distributed Tracing & Tail Latency Diagnosis",
                "question": f"In a distributed microservices architecture at {company_name}, when diagnosing an intermittent p99 latency spike that affects 1% of transactions, what observability tool provides the highest causal fidelity?",
                "options": [
                    "A) Distributed request tracing using OpenTelemetry with unique Trace IDs and Span context propagation",
                    "B) Standard aggregated CPU percent gauges on the host VM",
                    "C) Checking the daily total request counter in Google Analytics",
                    "D) Reviewing git commit messages from the previous week"
                ],
                "correct_option": "A",
                "correct_answer_explanation": "OpenTelemetry distributed tracing injects a trace ID across RPC and HTTP boundaries, visualizing the exact timing waterfall of every child span to pinpoint the bottleneck service.",
                "company_context": f"Observability at {company_name} relies on OpenTelemetry distributed tracing across all production microservices."
            }
        ]

    result_questions = []
    for item in questions_pool[:total_planned]:
        t_num = item["turn_number"]
        existing = turns_by_num.get(t_num, {})
        question_entry = {
            **item,
            "difficulty": calibrated_diff,
            "user_answer": existing.get("user_answer"),
            "selected_option": existing.get("selected_option")
        }
        result_questions.append(question_entry)

    return result_questions

async def evaluate_batch_answers(
    session_data: Dict[str, Any],
    submitted_answers: List[Dict[str, Any]]
) -> List[Dict[str, Any]]:
    """
    Concurrently evaluate all submitted answers using asyncio.gather.
    Eliminates coding shells and validates choices objectively against rubrics.
    """
    role_data = session_data.get("role_analysis", {})
    all_questions = generate_all_questions_for_session(session_data)
    q_by_num = {q["turn_number"]: q for q in all_questions}

    eval_tasks = []
    answers_order = []

    for item in submitted_answers:
        t_num = item.get("turn_number")
        ans_text = item.get("answer", "").strip()
        q_info = q_by_num.get(t_num, {})
        question_text = q_info.get("question", f"Question {t_num}")

        answers_order.append((t_num, ans_text, item.get("selected_option"), q_info))
        eval_tasks.append(
            evaluate_candidate_answer(
                question_asked=question_text,
                raw_user_answer=ans_text,
                role_data=role_data
            )
        )

    eval_results = await asyncio.gather(*eval_tasks)

    evaluated_turns = []
    for (t_num, ans_text, sel_opt, q_info), ev_result in zip(answers_order, eval_results):
        turn_entry = {
            "turn_number": t_num,
            "question": q_info.get("question"),
            "topic": q_info.get("topic"),
            "difficulty": q_info.get("difficulty", 3),
            "stage_title": q_info.get("stage_title"),
            "stage_category": q_info.get("stage_category"),
            "question_type": q_info.get("question_type", "mcq"),
            "options": q_info.get("options"),
            "correct_option": q_info.get("correct_option"),
            "correct_answer_explanation": q_info.get("correct_answer_explanation"),
            "company_context": q_info.get("company_context"),
            "user_answer": ans_text,
            "selected_option": sel_opt,
            "evaluation": ev_result.model_dump()
        }
        evaluated_turns.append(turn_entry)

    return evaluated_turns

