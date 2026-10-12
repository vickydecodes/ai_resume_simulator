const API_BASE = '/api';

export interface SessionCreateResponse {
  session_id: string;
  status: string;
  message: string;
  candidate_name: string;
  role_title: string;
  company_name: string;
  seniority_level: string;
  total_questions_planned: number;
}

export interface QuestionResponse {
  session_id: string;
  turn_number: number;
  total_questions: number;
  question: string;
  topic: string;
  difficulty: number;
  stage_title?: string;
  stage_category?: string;
  question_type?: 'mcq' | 'aptitude' | 'communication' | 'email_writing' | 'coding' | 'open_text';
  options?: string[];
  coding_starter_code?: string;
  coding_language?: string;
  email_context?: {
    recipient?: string;
    scenario?: string;
    required_tone?: string;
  };
  is_final: boolean;
  reason?: string;
}

export interface CategoryScores {
  resume_fit: number;
  technical_knowledge: number;
  communication: number;
  problem_solving: number;
  company_awareness: number;
}

export interface QuestionReviewItem {
  turn_number: number;
  stage_title: string;
  question: string;
  topic: string;
  difficulty: number;
  candidate_answer: string;
  candidate_selected_option?: string;
  correct_option: string;
  is_correct: boolean;
  explanation: string;
}

export interface ATSResumeOptimization {
  match_score: number;
  matched_skills: string[];
  missing_skills: string[];
  optimized_bullet_points: string[];
}

export interface EvaluationReport {
  session_id: string;
  candidate_name: string;
  role_title: string;
  company_name: string;
  overall_score: number;
  estimated_selection_probability: number;
  hiring_recommendation?: string;
  category_scores: CategoryScores;
  top_strengths: string[];
  top_weaknesses: string[];
  improvement_tips: string[];
  questions_review?: QuestionReviewItem[];
  ats_optimization?: ATSResumeOptimization;
  disclaimer: string;
}

export async function createSession(
  resumeFile: File, 
  company: string, 
  role: string,
  jobDescription?: string,
  difficulty?: string
): Promise<SessionCreateResponse> {
  const formData = new FormData();
  formData.append('resume', resumeFile);
  formData.append('company', company);
  formData.append('role', role);
  if (jobDescription && jobDescription.trim()) {
    formData.append('job_description', jobDescription.trim());
  }
  if (difficulty) {
    formData.append('difficulty', difficulty);
  }

  const res = await fetch(`${API_BASE}/sessions`, {
    method: 'POST',
    body: formData,
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Failed to create session' }));
    throw new Error(errorData.detail || 'Failed to create session');
  }

  return res.json();
}

export async function getSession(sessionId: string) {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}`);
  if (!res.ok) {
    throw new Error('Failed to fetch session detail');
  }
  return res.json();
}

export async function startInterview(sessionId: string): Promise<QuestionResponse> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/start`, {
    method: 'POST',
  });

  if (!res.ok) {
    throw new Error('Failed to start interview');
  }

  return res.json();
}

export async function submitAnswer(
  sessionId: string,
  answer: string,
  selectedOption?: string,
  questionType?: string
): Promise<QuestionResponse> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/answer`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      answer,
      selected_option: selectedOption,
      question_type: questionType,
    }),
  });

  if (!res.ok) {
    throw new Error('Failed to submit answer');
  }

  return res.json();
}

export interface QuestionItem {
  turn_number: number;
  stage_title: string;
  stage_category: string;
  question_type: 'mcq' | 'aptitude' | 'technical' | 'domain' | 'scenario' | 'open_text';
  topic: string;
  question: string;
  options?: string[];
  correct_option?: string;
  correct_answer_explanation?: string;
  company_context?: string;
  user_answer?: string;
  selected_option?: string;
}

export interface FullInterviewResponse {
  session_id: string;
  candidate_name: string;
  role_title: string;
  company_name: string;
  role_category?: string;
  difficulty_level?: string;
  total_questions: number;
  company_profile?: {
    company_name?: string;
    what_they_do?: string;
    products?: string[];
    tech_stack?: string[];
    culture?: string[];
    recent_news?: string[];
    interview_style_hints?: string;
  };
  job_description?: string;
  questions: QuestionItem[];
}

export interface BatchAnswerItem {
  turn_number: number;
  answer: string;
  selected_option?: string;
}

export async function getFullInterview(sessionId: string): Promise<FullInterviewResponse> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/questions`);
  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Failed to load interview questions' }));
    throw new Error(errorData.detail || 'Failed to load interview questions');
  }
  return res.json();
}

export async function submitAllAnswers(
  sessionId: string,
  answers: BatchAnswerItem[]
): Promise<EvaluationReport> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/submit-all`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ answers }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Failed to submit interview answers' }));
    throw new Error(errorData.detail || 'Failed to submit interview answers');
  }

  return res.json();
}

export async function getInterviewResult(sessionId: string): Promise<EvaluationReport> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/result`);
  if (!res.ok) {
    throw new Error('Failed to fetch interview evaluation report');
  }
  return res.json();
}

export interface ScrapedCompanyProfile {
  id: string;
  name: string;
  ticker?: string;
  estimatedWorth: string;
  worthBreakdown: string;
  industry: string;
  headquarters: string;
  description: string;
  culture: string;
  competencies: string[];
  hiringStages: {
    title: string;
    questionCount: number;
    format: string;
    focus: string;
  }[];
  roles: {
    id: string;
    title: string;
    track: 'tech' | 'sales' | 'pm' | 'data' | 'finance';
    level: string;
    difficulty: 'low' | 'medium' | 'hard';
    requiredSkills: string[];
    jobDescription: string;
  }[];
  isCustomScraped?: boolean;
}

export async function scrapeCompanyProfile(
  companyName: string,
  websiteUrl?: string
): Promise<ScrapedCompanyProfile> {
  const res = await fetch(`${API_BASE}/companies/scrape`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      company_name: companyName,
      website_url: websiteUrl,
    }),
  });

  if (!res.ok) {
    const errorData = await res.json().catch(() => ({ detail: 'Failed to scrape company' }));
    throw new Error(errorData.detail || 'Failed to scrape company');
  }

  return res.json();
}

export async function getCustomCompanies(): Promise<ScrapedCompanyProfile[]> {
  const res = await fetch(`${API_BASE}/companies/custom`);
  if (!res.ok) {
    return [];
  }
  return res.json();
}

