import logging
from app.core.security import sanitize_untrusted_input
from app.core.llm import llm_client
from app.models.schemas import RoleAnalysisResult
from app.prompts.role_prompt import ROLE_ANALYSIS_SYSTEM_PROMPT, ROLE_ANALYSIS_USER_PROMPT

logger = logging.getLogger("uvicorn.error")

async def analyze_role(role_title: str, role_description: str = "") -> RoleAnalysisResult:
    """Analyze target role title and description using LLM."""
    sanitized_desc = sanitize_untrusted_input(role_description) if role_description else "No raw job description provided."
    prompt = ROLE_ANALYSIS_USER_PROMPT.format(
        role_title=role_title,
        sanitized_role_description=sanitized_desc
    )

    result = await llm_client.generate_json(
        prompt=prompt,
        schema_cls=RoleAnalysisResult,
        system_prompt=ROLE_ANALYSIS_SYSTEM_PROMPT
    )
    # Ensure role title is set
    if not result.role_title:
        result.role_title = role_title
    return result
