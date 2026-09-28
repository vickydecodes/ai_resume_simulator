SCORE_REPORT_SYSTEM_PROMPT = """You are a principal tech hiring panel chair compiling a comprehensive post-interview evaluation report.

Analyze the full candidate interview history, individual turn evaluations, resume fit, and target company requirements.
Provide objective, constructive feedback, identifying candidate strengths, key weaknesses, and actionable improvement tips.
"""

SCORE_REPORT_USER_PROMPT = """SESSION METRICS SUMMARY:
- Candidate: {candidate_name}
- Target Role: {role_title} ({seniority_level})
- Target Company: {company_name}
- Candidate Resume Skills: {candidate_skills}
- Role Required Skills: {required_skills}

INTERVIEW TURN EVALUATIONS HISTORY:
{turns_evaluations_summary}

CALCULATED CATEGORY SCORES:
- Resume-Role Fit: {resume_fit_score}
- Technical Knowledge: {technical_score}
- Communication: {communication_score}
- Problem Solving: {problem_solving_score}
- Company Awareness: {company_awareness_score}
- Calculated Overall Score: {overall_score}

Return JSON matching EvaluationReportResult schema containing top strengths (at least 3), top weaknesses (at least 2), and concrete actionable improvement tips (at least 3).
"""
