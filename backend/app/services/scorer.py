import math
import logging
from typing import Dict, Any, List
from app.core.config import settings
from app.core.llm import llm_client
from app.models.schemas import EvaluationReportResult, CategoryScoreBreakdown, ATSResumeOptimization
from app.prompts.score_prompt import SCORE_REPORT_SYSTEM_PROMPT, SCORE_REPORT_USER_PROMPT

logger = logging.getLogger("uvicorn.error")

def calculate_resume_role_fit(resume_skills: List[str], role_skills: List[str]) -> float:
    """Calculate overlap score between candidate resume skills and role required skills."""
    if not role_skills:
        return 75.0
    
    resume_lower = {s.lower().strip() for s in resume_skills}
    matches = sum(1 for s in role_skills if s.lower().strip() in resume_lower or any(s.lower() in r for r in resume_lower))
    ratio = matches / max(1, len(role_skills))
    score = min(100.0, max(40.0, ratio * 100.0))
    return round(score, 1)

def compute_calibrated_selection_probability(overall_score: float, resume_fit_score: float) -> float:
    """
    Compute mathematically calibrated Estimated Selection Probability:
    P_selection = 1 / (1 + exp(-k * (S_effective - S_0)))
    Where S_effective = 0.85 * overall_score + 0.15 * resume_fit_score, S_0 = 70.0, k = 0.08.
    """
    s_effective = 0.85 * overall_score + 0.15 * resume_fit_score
    s_0 = 70.0
    k = 0.08
    prob_fraction = 1.0 / (1.0 + math.exp(-k * (s_effective - s_0)))
    percentage = prob_fraction * 100.0
    return round(min(98.5, max(5.0, percentage)), 1)

async def generate_evaluation_report(session_data: Dict[str, Any]) -> EvaluationReportResult:
    """Generate final comprehensive score report and feedback using rubric math and LLM."""
    session_id = session_data["session_id"]
    resume_data = session_data.get("resume_analysis", {})
    role_data = session_data.get("role_analysis", {})
    company_data = session_data.get("company_info", {})
    turns = session_data.get("turns", [])

    candidate_name = resume_data.get("candidate_name", "Candidate")
    role_title = role_data.get("role_title", "Target Role")
    seniority = role_data.get("seniority_level", "Mid")
    company_name = company_data.get("company_name", "Target Company")

    # 1. Compute Category Scores from Turn Evaluations
    resume_fit = calculate_resume_role_fit(
        resume_skills=resume_data.get("skills", []),
        role_skills=role_data.get("required_skills", [])
    )

    if turns:
        tech_scores = []
        depth_scores = []
        comm_scores = []
        rel_scores = []

        for t in turns:
            ev = t.get("evaluation")
            correct_opt = t.get("correct_option")
            sel_opt = t.get("selected_option")

            mcq_correctness = None
            if correct_opt and sel_opt:
                is_correct = sel_opt.strip().upper().startswith(correct_opt.upper())
                mcq_correctness = 95.0 if is_correct else 45.0

            if ev and isinstance(ev, dict):
                c_score = mcq_correctness if mcq_correctness is not None else ev.get("correctness_score", 75.0)
                tech_scores.append(c_score)
                depth_scores.append(ev.get("depth_score", 75.0))
                comm_scores.append(ev.get("communication_score", 80.0))
                rel_scores.append(ev.get("relevance_score", 75.0))
            else:
                c_score = mcq_correctness if mcq_correctness is not None else 75.0
                tech_scores.append(c_score)
                depth_scores.append(75.0)
                comm_scores.append(80.0)
                rel_scores.append(75.0)

        tech_knowledge = sum(tech_scores) / len(tech_scores)
        problem_solving = sum(depth_scores) / len(depth_scores)
        communication = sum(comm_scores) / len(comm_scores)
        company_awareness = (sum(rel_scores) / len(rel_scores)) * 0.9 + (10.0 if not company_data.get("is_limited_data") else 0.0)
        company_awareness = min(100.0, max(40.0, company_awareness))
    else:
        tech_knowledge = 75.0
        problem_solving = 75.0
        communication = 80.0
        company_awareness = 70.0

    # 2. Compute Weighted Overall Score
    w_rf = settings.WEIGHT_RESUME_FIT
    w_tk = settings.WEIGHT_TECHNICAL_KNOWLEDGE
    w_cm = settings.WEIGHT_COMMUNICATION
    w_ps = settings.WEIGHT_PROBLEM_SOLVING
    w_ca = settings.WEIGHT_COMPANY_AWARENESS

    overall_score = (
        w_rf * resume_fit +
        w_tk * tech_knowledge +
        w_cm * communication +
        w_ps * problem_solving +
        w_ca * company_awareness
    )
    overall_score = round(min(100.0, max(0.0, overall_score)), 1)

    # 3. Compute Calibrated Selection Probability
    p_selection = compute_calibrated_selection_probability(overall_score, resume_fit)

    category_scores = CategoryScoreBreakdown(
        resume_fit=round(resume_fit, 1),
        technical_knowledge=round(tech_knowledge, 1),
        communication=round(communication, 1),
        problem_solving=round(problem_solving, 1),
        company_awareness=round(company_awareness, 1)
    )

    # 4. Generate Qualitative Strengths, Weaknesses, and Actionable Tips via LLM
    turns_summary_lines = []
    for idx, t in enumerate(turns, 1):
        q = t.get("question", "")
        a = (t.get("user_answer") or "")[:200]
        ev = t.get("evaluation") or {}
        score = ev.get("turn_score", 75.0) if isinstance(ev, dict) else 75.0
        turns_summary_lines.append(f"Turn {idx}: Q: {q} | A: {a} | Turn Score: {score}")

    turns_summary_str = "\n".join(turns_summary_lines) if turns_summary_lines else "No interview turns recorded."

    prompt = SCORE_REPORT_USER_PROMPT.format(
        candidate_name=candidate_name,
        role_title=role_title,
        seniority_level=seniority,
        company_name=company_name,
        candidate_skills=", ".join(resume_data.get("skills", [])[:8]),
        required_skills=", ".join(role_data.get("required_skills", [])[:8]),
        turns_evaluations_summary=turns_summary_str,
        resume_fit_score=category_scores.resume_fit,
        technical_score=category_scores.technical_knowledge,
        communication_score=category_scores.communication,
        problem_solving_score=category_scores.problem_solving,
        company_awareness_score=category_scores.company_awareness,
        overall_score=overall_score
    )

    try:
        llm_report: EvaluationReportResult = await llm_client.generate_json(
            prompt=prompt,
            schema_cls=EvaluationReportResult,
            system_prompt=SCORE_REPORT_SYSTEM_PROMPT
        )
    except Exception as e:
        logger.warning(f"LLM score report generation fallback due to: {e}")
        llm_report = EvaluationReportResult(
            session_id=session_id,
            candidate_name=candidate_name,
            role_title=role_title,
            company_name=company_name,
            overall_score=overall_score,
            estimated_selection_probability=p_selection,
            category_scores=category_scores,
            top_strengths=[
                f"Strong technical alignment with {role_title} core proficiencies.",
                "Structured approach when articulating design decisions.",
                f"Clear motivation and alignment with {company_name}'s domain."
            ],
            top_weaknesses=[
                "Could provide more concrete quantitative benchmarks during architectural trade-off discussions.",
                "Opportunity to elaborate deeper on distributed failure modes and automated failover."
            ],
            improvement_tips=[
                "Structure technical responses using the STAR format (Situation, Task, Action, Result).",
                f"Review {company_name}'s architecture blogs to sharpen domain-specific insights.",
                "Always quantify latency bounds, throughput targets, and memory footprints in system challenges."
            ]
        )

    # Hydrate exact computed scores into final report model
    llm_report.session_id = session_id
    llm_report.candidate_name = candidate_name
    llm_report.role_title = role_title
    llm_report.company_name = company_name
    llm_report.overall_score = overall_score
    llm_report.estimated_selection_probability = p_selection
    llm_report.category_scores = category_scores

    if not llm_report.top_strengths:
        llm_report.top_strengths = [
            f"Strong alignment in core {role_title} competencies.",
            "Effective structure and clarity during response delivery.",
            f"Demonstrated domain problem-solving tailored to {company_name}."
        ]
    if not llm_report.top_weaknesses:
        llm_report.top_weaknesses = [
            "Could provide deeper quantitative metrics when discussing trade-offs.",
            "Opportunity to showcase more explicit target company product alignment."
        ]
    if not llm_report.improvement_tips:
        llm_report.improvement_tips = [
            "Frame technical past achievements using the STAR method (Situation, Task, Action, Result).",
            f"Deepen knowledge of {company_name}'s published tech stack and core products.",
            "Include explicit latency, throughput, or revenue metrics during scenario discussions."
        ]

    # 5. Compile Per-Question Review List
    q_review = []
    for t in turns:
        t_num = t.get("turn_number", 1)
        q_text = t.get("question", "")
        topic = t.get("topic", "")
        options = t.get("options", [])
        correct_opt = t.get("correct_option")
        explanation = t.get("correct_answer_explanation", "")
        user_sel = t.get("selected_option") or t.get("user_answer", "")
        is_corr = False
        if correct_opt and user_sel:
            is_corr = user_sel.strip().upper().startswith(correct_opt.upper())

        q_review.append({
            "turn_number": t_num,
            "question": q_text,
            "topic": topic,
            "stage_title": t.get("stage_title", ""),
            "options": options,
            "correct_option": correct_opt,
            "correct_answer_explanation": explanation,
            "user_selected": user_sel,
            "is_correct": is_corr,
        })

    # 6. Compile ATS Resume & Job Description Match Optimization
    resume_skills = [s.strip().lower() for s in resume_data.get("skills", [])]
    role_skills = role_data.get("required_skills", [])

    matched = []
    missing = []
    for s in role_skills:
        if any(s.lower() in rs or rs in s.lower() for rs in resume_skills):
            matched.append(s)
        else:
            missing.append(s)

    if not matched:
        matched = role_skills[:3] if role_skills else ["Domain Problem Solving", "Strategic Execution"]
    if not missing:
        missing = ["Scalable Systems Architecture", "Cross-functional KPI Alignment"]

    ats_score = round(min(96.0, max(48.0, (len(matched) / max(1, len(role_skills))) * 100.0)), 1) if role_skills else 80.0

    ats_bullets = [
        f"Accelerated {role_title} deliverables by 32% utilizing {matched[0] if matched else 'core methodologies'} to achieve cross-functional excellence.",
        f"Designed high-impact initiatives yielding a 26% efficiency increase, directly aligning with {company_name}'s high-standard workflows.",
        f"Championed implementation of {missing[0] if missing else 'best practices'}, reducing turnaround time and elevating team productivity."
    ]

    llm_report.questions_review = q_review
    llm_report.ats_optimization = ATSResumeOptimization(
        match_score=ats_score,
        matched_skills=matched[:8],
        missing_skills=missing[:6],
        optimized_bullet_points=ats_bullets
    )

    return llm_report
