export interface CandidateResume {
  id: string;
  filename: string;
  label: string;
  uploadedAt: string;
  sizeKb: number;
  content: string;
  isActive: boolean;
  skills: string[];
}

export interface CandidateUser {
  id: string;
  name: string;
  email: string;
  title: string;
  targetSeniority: string;
  resumes: CandidateResume[];
}

export interface SessionHistoryItem {
  sessionId: string;
  candidateEmail: string;
  candidateName: string;
  companyName: string;
  roleTitle: string;
  overallScore?: number;
  recommendation?: string;
  createdAt: string;
}

const STORAGE_KEY_AUTH = 'hirefit_candidate_auth_v3';
const STORAGE_KEY_HISTORY = 'hirefit_session_history_v3';

const DEFAULT_SAMPLE_RESUMES: CandidateResume[] = [
  {
    id: 'res-1',
    filename: 'Alex_Rivera_Backend_Systems.txt',
    label: 'Primary Backend & Distributed Systems Resume',
    uploadedAt: '2026-03-15',
    sizeKb: 14.2,
    isActive: true,
    skills: ['Python', 'FastAPI', 'Distributed Systems', 'Redis', 'PostgreSQL', 'Kafka', 'Docker', 'AWS ECS', 'System Architecture', 'Idempotency'],
    content: `ALEX RIVERA
Email: alex.rivera@example.com | San Francisco, CA | GitHub: github.com/alexrivera-tech

SUMMARY
Software Engineer with 5+ years of experience architecting high-throughput backend services. Proven expertise in Python, FastAPI, PostgreSQL, Redis, Docker, and AWS distributed microservices. Led database optimization projects reducing p99 latency by 42%.

EXPERIENCE
Senior Backend Engineer | PayStream Systems | 2022 – Present
- Built and maintained distributed orchestration services handling 15M monthly requests with 99.98% availability.
- Implemented asynchronous event streaming with Kafka for automated retry handling, eliminating message loss.
- Decreased API p99 response times from 320ms to 85ms via Redis distributed caching and SQL query indexing.

TECHNICAL SKILLS
- Languages: Python, Go, TypeScript, SQL
- Frameworks & Tools: FastAPI, Docker, Kubernetes, Redis, PostgreSQL, Kafka, AWS ECS`,
  },
  {
    id: 'res-2',
    filename: 'Alex_Rivera_Machine_Learning.txt',
    label: 'Machine Learning & Applied AI Resume',
    uploadedAt: '2026-03-20',
    sizeKb: 16.8,
    isActive: false,
    skills: ['PyTorch', 'Vector Search', 'Feature Stores', 'Ray', 'Scikit-Learn', 'Python', 'Model Monitoring', 'Triton', 'Deep Learning'],
    content: `ALEX RIVERA (ML FOCUS)
Email: alex.rivera@example.com | San Francisco, CA

SUMMARY
Senior ML Engineer with expertise in production recommendation engines, vector embeddings, and real-time fraud models at scale. Expert in PyTorch, Ray, and Triton Inference Server.

EXPERIENCE
Lead ML Engineer | RetailAI Systems | 2022 – Present
- Architected vector search and recommendation retrieval service indexing 40M items using HNSW in Pinecone and PyTorch.
- Deployed real-time classification pipeline processing 35,000 queries per second with p99 latency under 18ms.
- Eliminated training-serving skew by implementing Feast centralized feature store.

SKILLS
- PyTorch, Scikit-learn, Ray, Spark, Python, Vector DBs, Model Drift Monitoring, AWS SageMaker`,
  },
  {
    id: 'res-3',
    filename: 'Alex_Rivera_General_SDE.txt',
    label: 'Full Stack & Product Engineering Resume',
    uploadedAt: '2026-03-28',
    sizeKb: 12.5,
    isActive: false,
    skills: ['React', 'TypeScript', 'Node.js', 'Next.js', 'PostgreSQL', 'Tailwind CSS', 'REST APIs', 'UI/UX'],
    content: `ALEX RIVERA (FULL STACK)
Email: alex.rivera@example.com | San Francisco, CA

SUMMARY
Full Stack Engineer with 4+ years building high-impact web applications in React, TypeScript, and Python. Experience managing product development from design specs to deployment.

EXPERIENCE
Full Stack Engineer | CloudHub Systems | 2021 – 2024
- Built responsive internal and customer-facing dashboards used by 45,000 daily active users.
- Designed RESTful APIs in Node.js and FastAPI with comprehensive integration test suites.`,
  },
];

export const DEMO_USER: CandidateUser = {
  id: 'cand-001',
  name: 'Alex Johnson',
  email: 'alex.johnson@example.com',
  title: 'Senior Software Engineer',
  targetSeniority: 'Mid-Senior (IC4 / L5)',
  resumes: DEFAULT_SAMPLE_RESUMES,
};

export interface CandidateProfile {
  name: string;
  email: string;
  resumeFileName?: string;
  isLoggedIn?: boolean;
}

export function getCurrentUser(): CandidateUser | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_AUTH);
    if (raw) {
      return JSON.parse(raw);
    }
    // Auto-seed initial demo candidate if not explicitly logged out
    if (localStorage.getItem('hirefit_logged_out') !== 'true') {
      localStorage.setItem(STORAGE_KEY_AUTH, JSON.stringify(DEMO_USER));
      return DEMO_USER;
    }
  } catch (e) {
    console.error('Failed to parse current user session:', e);
  }
  return null;
}

export function loginUser(email: string, name?: string): CandidateUser {
  localStorage.removeItem('hirefit_logged_out');
  const existing = getCurrentUser();
  const userName = name?.trim() || (email.split('@')[0].replace(/[._]/g, ' ').replace(/\b\w/g, (c) => c.toUpperCase()) || 'Candidate');
  
  const user: CandidateUser = {
    id: existing?.id || `cand-${Date.now()}`,
    name: existing?.email.toLowerCase() === email.toLowerCase() ? existing.name : userName,
    email: email.trim().toLowerCase(),
    title: existing?.title || 'Software Engineer',
    targetSeniority: existing?.targetSeniority || 'Senior (IC5 / L5)',
    resumes: existing?.resumes && existing.resumes.length > 0 ? existing.resumes : DEFAULT_SAMPLE_RESUMES,
  };

  try {
    localStorage.setItem(STORAGE_KEY_AUTH, JSON.stringify(user));
  } catch (e) {
    console.error('Failed to save user session:', e);
  }
  return user;
}

export function getCandidateProfile(): CandidateProfile | null {
  const u = getCurrentUser();
  if (!u) return null;
  const active = getActiveResume(u);
  return {
    name: u.name,
    email: u.email,
    resumeFileName: active ? active.filename : undefined,
  };
}

export function loginCandidate(name: string, email: string, resumeFileName?: string): CandidateProfile {
  const user = loginUser(email, name);
  const active = getActiveResume(user);
  return {
    name: user.name,
    email: user.email,
    resumeFileName: active ? active.filename : resumeFileName,
  };
}

export function logoutCandidate(): void {
  logoutUser();
}

export function registerUser(name: string, email: string, title?: string, seniority?: string): CandidateUser {
  const user: CandidateUser = {
    id: `cand-${Date.now()}`,
    name: name.trim() || 'Candidate',
    email: email.trim().toLowerCase(),
    title: title?.trim() || 'Software Engineer',
    targetSeniority: seniority?.trim() || 'Senior (IC5 / L5)',
    resumes: DEFAULT_SAMPLE_RESUMES,
  };

  try {
    localStorage.setItem(STORAGE_KEY_AUTH, JSON.stringify(user));
  } catch (e) {
    console.error('Failed to register user:', e);
  }
  return user;
}

export function logoutUser(): void {
  try {
    localStorage.removeItem(STORAGE_KEY_AUTH);
    localStorage.setItem('hirefit_logged_out', 'true');
  } catch (e) {
    console.error('Failed to logout user:', e);
  }
}

export function updateCandidateDetails(name: string, title: string, seniority: string): CandidateUser | null {
  const user = getCurrentUser();
  if (!user) return null;
  user.name = name.trim();
  user.title = title.trim();
  user.targetSeniority = seniority.trim();
  localStorage.setItem(STORAGE_KEY_AUTH, JSON.stringify(user));
  return user;
}

export function getActiveResume(user?: CandidateUser | null): CandidateResume | null {
  const u = user || getCurrentUser();
  if (!u || !u.resumes || u.resumes.length === 0) return null;
  return u.resumes.find((r) => r.isActive) || u.resumes[0];
}

export function setActiveResume(resumeId: string): CandidateUser | null {
  const user = getCurrentUser();
  if (!user) return null;
  user.resumes = user.resumes.map((r) => ({
    ...r,
    isActive: r.id === resumeId,
  }));
  localStorage.setItem(STORAGE_KEY_AUTH, JSON.stringify(user));
  return user;
}

export function addCandidateResume(
  filename: string,
  content: string,
  label: string,
  sizeKb: number,
  skills: string[]
): CandidateUser | null {
  const user = getCurrentUser();
  if (!user) return null;

  const newResume: CandidateResume = {
    id: `res-${Date.now()}`,
    filename,
    label: label.trim() || filename,
    uploadedAt: new Date().toISOString().split('T')[0],
    sizeKb: Math.max(1, Math.round(sizeKb)),
    content,
    isActive: true, // newly uploaded resume becomes active by default
    skills: skills.length > 0 ? skills : ['General Competencies', 'Industry Experience'],
  };

  // Mark all other resumes inactive
  user.resumes = [newResume, ...user.resumes.map((r) => ({ ...r, isActive: false }))];
  localStorage.setItem(STORAGE_KEY_AUTH, JSON.stringify(user));
  return user;
}

export function deleteCandidateResume(resumeId: string): CandidateUser | null {
  const user = getCurrentUser();
  if (!user) return null;
  if (user.resumes.length <= 1) {
    throw new Error('At least one resume must remain in your candidate profile.');
  }
  const wasActive = user.resumes.find((r) => r.id === resumeId)?.isActive;
  user.resumes = user.resumes.filter((r) => r.id !== resumeId);
  if (wasActive && user.resumes.length > 0) {
    user.resumes[0].isActive = true;
  }
  localStorage.setItem(STORAGE_KEY_AUTH, JSON.stringify(user));
  return user;
}

export function getCandidateActiveResumeFile(user?: CandidateUser | null): File | null {
  const resume = getActiveResume(user);
  if (!resume) return null;
  const blob = new Blob([resume.content], { type: 'text/plain' });
  return new File([blob], resume.filename, { type: 'text/plain' });
}

// Session History Persistence
export function saveSessionHistory(item: SessionHistoryItem): void {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_HISTORY);
    const history: SessionHistoryItem[] = raw ? JSON.parse(raw) : [];
    const filtered = history.filter((h) => h.sessionId !== item.sessionId);
    const updated = [item, ...filtered];
    localStorage.setItem(STORAGE_KEY_HISTORY, JSON.stringify(updated.slice(0, 30)));
  } catch (e) {
    console.error('Failed to save session history:', e);
  }
}

export function getSessionHistory(): SessionHistoryItem[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_HISTORY);
    if (!raw) return [];
    return JSON.parse(raw);
  } catch (e) {
    console.error('Failed to get session history:', e);
    return [];
  }
}

export function clearSessionHistory(): void {
  try {
    localStorage.removeItem(STORAGE_KEY_HISTORY);
  } catch (e) {
    console.error('Failed to clear session history:', e);
  }
}
