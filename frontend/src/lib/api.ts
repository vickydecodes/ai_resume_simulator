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

export interface EvaluationReport {
  session_id: string;
  candidate_name: string;
  role_title: string;
  company_name: string;
  overall_score: number;
  estimated_selection_probability: number;
  category_scores: CategoryScores;
  top_strengths: string[];
  top_weaknesses: string[];
  improvement_tips: string[];
  disclaimer: string;
}

export async function createSession(resumeFile: File, company: string, role: string): Promise<SessionCreateResponse> {
  const formData = new FormData();
  formData.append('resume', resumeFile);
  formData.append('company', company);
  formData.append('role', role);

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

export async function submitAnswer(sessionId: string, answer: string): Promise<QuestionResponse> {
  const res = await fetch(`${API_BASE}/sessions/${sessionId}/answer`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ answer }),
  });

  if (!res.ok) {
    throw new Error('Failed to submit answer');
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
