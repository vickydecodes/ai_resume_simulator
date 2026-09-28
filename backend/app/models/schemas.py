from typing import List, Dict, Optional, Any
from pydantic import BaseModel, Field

# --- RESUME SCHEMAS ---
class ProjectSummary(BaseModel):
    name: str = Field(description="Name or title of project")
    description: str = Field(description="Summary of project achievements and technical tools used")

class ResumeAnalysisResult(BaseModel):
    candidate_name: str = Field(default="Candidate", description="Extracted candidate name")
    experience_years: float = Field(default=0.0, description="Total estimated professional experience in years")
    skills: List[str] = Field(default_factory=list, description="Extracted technical and professional skills")
    projects: List[ProjectSummary] = Field(default_factory=list, description="Key projects mentioned")
    education: str = Field(default="", description="Education background summary")
    key_strengths: List[str] = Field(default_factory=list, description="Top candidate technical/career strengths")
    identified_gaps: List[str] = Field(default_factory=list, description="Skill or experience gaps relative to industry standards")

# --- ROLE SCHEMAS ---
class RoleAnalysisResult(BaseModel):
    role_title: str = Field(description="Parsed role title")
    seniority_level: str = Field(default="Mid", description="Seniority calibration (Junior, Mid, Senior, Lead, Staff)")
    required_skills: List[str] = Field(default_factory=list, description="Core required skills for the role")
    responsibilities: List[str] = Field(default_factory=list, description="Primary duties and responsibilities")
    likely_topics: List[str] = Field(default_factory=list, description="Key technical and behavioral interview topics")

# --- COMPANY SCHEMAS ---
class CompanyInfoResult(BaseModel):
    company_name: str = Field(description="Name of the company")
    what_they_do: str = Field(default="N/A", description="Overview of company business and mission")
    products: List[str] = Field(default_factory=list, description="Primary products or platform services")
    tech_stack: List[str] = Field(default_factory=list, description="Technologies, languages, and frameworks used")
    culture: List[str] = Field(default_factory=list, description="Core company values and work culture aspects")
    recent_news: List[str] = Field(default_factory=list, description="Recent headlines, funding, or product updates")
    interview_style_hints: str = Field(default="Standard technical and cultural alignment loop.", description="Interview style hints")
    is_limited_data: bool = Field(default=False, description="True if company scraping had limited data and used fallbacks")

# --- SESSION SCHEMAS ---
class SessionCreateResponse(BaseModel):
    session_id: str
    status: str = "initialized"
    message: str = "Session successfully created and context analysis complete."
    candidate_name: str
    role_title: str
    company_name: str
    seniority_level: str
    total_questions_planned: int = 8

class SessionDetailResponse(BaseModel):
    session_id: str
    company_name: str
    role_title: str
    status: str
    current_turn: int
    total_questions_planned: int
    resume_analysis: ResumeAnalysisResult
    role_analysis: RoleAnalysisResult
    company_info: CompanyInfoResult

# --- INTERVIEW SCHEMAS ---
class InterviewQuestionResponse(BaseModel):
    session_id: str
    turn_number: int
    total_questions: int
    question: str
    topic: str
    difficulty: int  # 1 to 5
    is_final: bool = False
    reason: Optional[str] = None

class AnswerSubmitRequest(BaseModel):
    answer: str = Field(..., min_length=2, description="Candidate text answer response")

class AnswerEvaluationResult(BaseModel):
    relevance_score: int = Field(..., ge=0, le=100)
    depth_score: int = Field(..., ge=0, le=100)
    correctness_score: int = Field(..., ge=0, le=100)
    communication_score: int = Field(..., ge=0, le=100)
    feedback: str
    turn_score: float

class StepNextQuestionResponse(BaseModel):
    next_question: str
    topic: str = "Technical Depth"
    difficulty: int = 3
    is_final: bool = False
    reason: str = "Next question in interview loop"

# --- RESULT SCHEMAS ---
class CategoryScoreBreakdown(BaseModel):
    resume_fit: float = Field(..., ge=0, le=100)
    technical_knowledge: float = Field(..., ge=0, le=100)
    communication: float = Field(..., ge=0, le=100)
    problem_solving: float = Field(..., ge=0, le=100)
    company_awareness: float = Field(..., ge=0, le=100)

class EvaluationReportResult(BaseModel):
    session_id: str
    candidate_name: str
    role_title: str
    company_name: str
    overall_score: float = Field(..., ge=0, le=100)
    estimated_selection_probability: float = Field(..., ge=0, le=100)
    category_scores: CategoryScoreBreakdown
    top_strengths: List[str]
    top_weaknesses: List[str]
    improvement_tips: List[str]
    disclaimer: str = "Estimated Selection Probability is an algorithmic preparation metric derived from candidate profile alignment and interview response depth. It does NOT guarantee hiring decisions by the target company."
