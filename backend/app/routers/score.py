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
    report = await generate_evaluation_report(sess)

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
