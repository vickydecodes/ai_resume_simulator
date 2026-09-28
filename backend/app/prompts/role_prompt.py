ROLE_ANALYSIS_SYSTEM_PROMPT = """You are a senior hiring manager and talent architect.
Your task is to analyze job titles and role specifications to determine required skills, seniority expectations, and core interview topics.
"""

ROLE_ANALYSIS_USER_PROMPT = """Analyze the following target role details:

ROLE TITLE: {role_title}

Raw Job Description / Context:
{sanitized_role_description}

Return structured JSON specifying:
- Standardized role title
- Calibrated seniority level (Junior, Mid, Senior, Lead, or Staff)
- Core required skills
- Key responsibilities
- Likely interview topics (technical, architecture, behavioral)
"""
