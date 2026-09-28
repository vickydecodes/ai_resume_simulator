import math
import logging
from typing import Dict, Any, List
from app.core.config import settings
from app.core.llm import llm_client
from app.models.schemas import EvaluationReportResult, CategoryScoreBreakdown
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
        tech_scores = [t.get("evaluation", {}).get("correctness_score", 75.0) for t in turns]
        depth_scores = [t.get("evaluation", {}).get("depth_score", 75.0) for t in turns]
        comm_scores = [t.get("evaluation", {}).get("communication_score", 80.0) for t in turns]
        rel_scores = [t.get("evaluation", {}).get("relevance_score", 75.0) for t in turns]

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
        a = t.get("user_answer", "")[:200]
        score = t.get("evaluation", {}).get("turn_score", 75.0)
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

    llm_report: EvaluationReportResult = await llm_client.generate_json(
        prompt=prompt,
        schema_cls=EvaluationReportResult,
        system_prompt=SCORE_REPORT_SYSTEM_PROMPT
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
            f"Strong technical alignment in core {role_title} competencies.",
            "Effective structure and clarity during response delivery.",
            "Good understanding of fundamental computer science principles."
        ]
    if not llm_report.top_weaknesses:
        llm_report.top_weaknesses = [
            "Could provide deeper quantitative metrics when discussing architectural trade-offs.",
            "Opportunity to showcase more explicit target company product alignment."
        ]
    if not llm_report.improvement_tips:
        llm_report.improvement_tips = [
            "Frame technical past achievements using the STAR method (Situation, Task, Action, Result).",
            f"Deepen knowledge of {company_name}'s published tech stack and core products.",
            "Include explicit latency, throughput, and error boundary numbers during system design questions."
        ]

    return llm_report
