import uuid
import datetime
import logging
from typing import Dict, Any, Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from app.core.db import get_database
from app.core.security import validate_resume_file
from app.services.resume_parser import parse_resume_bytes
from app.services.role_analyzer import analyze_role
from app.services.company_scraper import scrape_company_intelligence
from app.models.schemas import SessionCreateResponse, SessionDetailResponse
from app.services.question_bank import detect_role_category, is_non_tech_role

logger = logging.getLogger("uvicorn.error")
router = APIRouter(prefix="/sessions", tags=["Sessions"])

# In-memory session store fallback if MongoDB is unavailable
in_memory_sessions: Dict[str, Dict[str, Any]] = {}

async def run_context_analysis(
    session_id: str,
    file_name: str,
    file_bytes: bytes,
    company_name: str,
    role_title: str,
    job_description: Optional[str] = None
):
    """Execute background processing for resume parsing, role profiling, and company scraping."""
    logger.info(f"Starting background context analysis for session {session_id}...")
    try:
        resume_res = await parse_resume_bytes(file_name, file_bytes)
        role_res = await analyze_role(role_title, job_description or "")
        company_res = await scrape_company_intelligence(company_name)

        session_update = {
            "status": "ready",
            "resume_analysis": resume_res.model_dump(),
            "role_analysis": role_res.model_dump(),
            "company_info": company_res.model_dump(),
            "updated_at": datetime.datetime.now(datetime.timezone.utc)
        }

        db = get_database()
        if db is not None:
            await db.sessions.update_one({"session_id": session_id}, {"$set": session_update})
        
        # Always sync to in-memory store as backup
        if session_id in in_memory_sessions:
            in_memory_sessions[session_id].update(session_update)

        logger.info(f"Completed context analysis for session {session_id}.")
    except Exception as e:
        logger.error(f"Failed background context analysis for session {session_id}: {e}")
        err_update = {"status": "error", "error_message": str(e)}
        db = get_database()
        if db is not None:
            await db.sessions.update_one({"session_id": session_id}, {"$set": err_update})
        if session_id in in_memory_sessions:
            in_memory_sessions[session_id].update(err_update)

@router.post("", response_model=SessionCreateResponse)
async def create_session(
    resume: UploadFile = File(...),
    company: str = Form(...),
    role: str = Form(...),
    job_description: Optional[str] = Form(None),
    difficulty: Optional[str] = Form("medium")
):
    """Create a new mock interview session and kick off resume, role, and company analysis."""
    if not company or not company.strip():
        raise HTTPException(status_code=400, detail="Target company name is required.")
    if not role or not role.strip():
        raise HTTPException(status_code=400, detail="Target role title is required.")

    file_bytes = await resume.read()
    validate_resume_file(resume, file_bytes)

    session_id = str(uuid.uuid4())
    now = datetime.datetime.now(datetime.timezone.utc)

    role_category = "sales" if is_non_tech_role(role.strip()) else "tech"
    diff_level = (difficulty or "medium").lower().strip()
    if diff_level not in ["easy", "low", "medium", "hard"]:
        diff_level = "medium"

    calc_difficulty = 4 if diff_level == "hard" else (2 if diff_level in ["easy", "low"] else 3)

    session_doc = {
        "session_id": session_id,
        "company_name": company.strip(),
        "role_title": role.strip(),
        "job_description": job_description.strip() if job_description else None,
        "difficulty_level": diff_level,
        "role_category": role_category,
        "status": "analyzing",
        "current_turn": 0,
        "total_questions_planned": 20,
        "current_difficulty": calc_difficulty,
        "turns": [],
        "created_at": now,
        "updated_at": now
    }

    db = get_database()
    if db is not None:
        try:
            await db.sessions.insert_one(session_doc)
        except Exception as e:
            logger.warning(f"MongoDB session insert error: {e}")

    in_memory_sessions[session_id] = session_doc

    # Kick off background context analysis synchronously or as async task
    await run_context_analysis(
        session_id=session_id,
        file_name=resume.filename or "resume.pdf",
        file_bytes=file_bytes,
        company_name=company.strip(),
        role_title=role.strip(),
        job_description=job_description.strip() if job_description else None
    )

    updated_sess = in_memory_sessions.get(session_id, session_doc)

    return SessionCreateResponse(
        session_id=session_id,
        status=updated_sess.get("status", "ready"),
        message="Session created and context analysis complete.",
        candidate_name=updated_sess.get("resume_analysis", {}).get("candidate_name", "Candidate"),
        role_title=role.strip(),
        company_name=company.strip(),
        seniority_level=updated_sess.get("role_analysis", {}).get("seniority_level", "Mid"),
        total_questions_planned=20,
        difficulty_level=diff_level,
        role_category=role_category
    )

@router.get("/{session_id}", response_model=SessionDetailResponse)
async def get_session_detail(session_id: str):
    """Retrieve current session details and analysis status."""
    db = get_database()
    sess = None
    if db is not None:
        sess = await db.sessions.find_one({"session_id": session_id})
    if not sess:
        sess = in_memory_sessions.get(session_id)

    if not sess:
        raise HTTPException(status_code=404, detail="Interview session not found.")

    return SessionDetailResponse(
        session_id=session_id,
        company_name=sess["company_name"],
        role_title=sess["role_title"],
        status=sess.get("status", "ready"),
        current_turn=sess.get("current_turn", 0),
        total_questions_planned=sess.get("total_questions_planned", 8),
        resume_analysis=sess.get("resume_analysis", {}),
        role_analysis=sess.get("role_analysis", {}),
        company_info=sess.get("company_info", {})
    )
