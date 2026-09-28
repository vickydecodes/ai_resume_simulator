import re
from fastapi import HTTPException, UploadFile
from app.core.config import settings

ALLOWED_EXTENSIONS = {".pdf", ".docx"}

def validate_resume_file(file: UploadFile, content: bytes) -> None:
    """Validate uploaded resume file size and extension."""
    if len(content) > settings.MAX_FILE_SIZE_BYTES:
        raise HTTPException(
            status_code=400,
            detail=f"File size exceeds maximum allowed limit of {settings.MAX_FILE_SIZE_BYTES / (1024*1024):.1f} MB."
        )
    
    filename = file.filename or ""
    ext = "." + filename.split(".")[-1].lower() if "." in filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Invalid file format '{ext}'. Allowed file formats: PDF, DOCX."
        )

def sanitize_untrusted_input(text: str) -> str:
    """
    Sanitize raw text from resumes or scraped web pages to prevent prompt injection.
    Wraps text in explicit untrusted XML tags and strips potential breaking delimiters.
    """
    if not text:
        return ""
    
    # Remove system prompt override attempts or delimiter tricks
    clean = re.sub(r"</?untrusted_content>", "", text, flags=re.IGNORECASE)
    clean = re.sub(r"</?system>", "", clean, flags=re.IGNORECASE)
    
    return f"<untrusted_content>\n{clean.strip()}\n</untrusted_content>"

def sanitize_user_answer(text: str) -> str:
    """Sanitize user candidate chat answer text."""
    if not text:
        return ""
    # Strip potential prompt injection directives
    clean = re.sub(r"ignore (all )?previous instructions", "[redacted instruction]", text, flags=re.IGNORECASE)
    clean = re.sub(r"you are now an? ", "[redacted role change]", clean, flags=re.IGNORECASE)
    return clean.strip()
