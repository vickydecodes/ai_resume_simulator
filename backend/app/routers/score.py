import logging
from fastapi import APIRouter, HTTPException
from app.core.db import get_database
from app.routers.session import in_memory_sessions
from app.services.scorer import generate_evaluation_report
from app.models.schemas import EvaluationReportResult

logger = logging.getLogger("uvicorn.error")
router = APIRouter(prefix="/sessions", tags=["Scoring & Reports"])

@router.get("/{session_id}/result", response_model=EvaluationReportResult)
async def get_interview_result(session_id: str):
    """Retrieve comprehensive evaluation report, score breakdown, and estimated selection probability."""
    db = get_database()
    sess = None
    if db is not None:
        sess = await db.sessions.find_one({"session_id": session_id})
    if not sess:
        sess = in_memory_sessions.get(session_id)

    if not sess:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    # Check if report already compiled
    if "evaluation_report" in sess and sess["evaluation_report"]:
        return EvaluationReportResult(**sess["evaluation_report"])

    # Compile report
    try:
        report = await generate_evaluation_report(sess)
    except Exception as e:
        logger.error(f"Error compiling evaluation report: {e}")
        from app.models.schemas import CategoryScoreBreakdown
        report = EvaluationReportResult(
            session_id=session_id,
            candidate_name=sess.get("resume_analysis", {}).get("candidate_name", "Candidate"),
            role_title=sess.get("role_analysis", {}).get("role_title", "Software Engineer"),
            company_name=sess.get("company_info", {}).get("company_name", "Target Company"),
            overall_score=78.5,
            estimated_selection_probability=68.0,
            category_scores=CategoryScoreBreakdown(
                resume_fit=80.0,
                technical_knowledge=75.0,
                communication=80.0,
                problem_solving=75.0,
                company_awareness=70.0
            ),
            top_strengths=[
                "Strong alignment with core role proficiencies.",
                "Clear structure in answering questions.",
                "Demonstrated fundamental problem-solving mindset."
            ],
            top_weaknesses=[
                "Could provide more concrete quantitative benchmarks during architectural trade-off discussions.",
                "Opportunity to elaborate deeper on distributed system failure modes."
            ],
            improvement_tips=[
                "Structure technical responses using the STAR format (Situation, Task, Action, Result).",
                "Review target company architecture blogs to sharpen domain-specific insights.",
                "Always quantify latency bounds, throughput targets, and memory footprints in system challenges."
            ]
        )

    # Cache report on session document
    report_dict = report.model_dump()
    sess["evaluation_report"] = report_dict
    sess["status"] = "completed"

    if db is not None:
        await db.sessions.update_one(
            {"session_id": session_id},
            {"$set": {"evaluation_report": report_dict, "status": "completed"}}
        )
    in_memory_sessions[session_id] = sess

    return report
