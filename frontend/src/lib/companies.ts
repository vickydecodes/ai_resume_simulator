export interface HiringStage {
  title: string;
  questionCount: number;
  format: string;
  focus: string;
}

export interface CompanyRole {
  id: string;
  title: string;
  track: 'tech' | 'sales' | 'pm' | 'data' | 'finance';
  level: string;
  difficulty: 'low' | 'medium' | 'hard';
  requiredSkills: string[];
  jobDescription: string;
}

export interface CompanyProfile {
  id: string;
  name: string;
  ticker?: string;
  industry: string;
  headquarters: string;
  description: string;
  culture: string;
  competencies: string[];
  hiringStages: HiringStage[];
  roles: CompanyRole[];
  estimatedWorth?: string;
  worthBreakdown?: string;
  isCustomScraped?: boolean;
}

export const COMPANIES_DIRECTORY: CompanyProfile[] = [
  {
    id: 'google',
    name: 'Google',
    ticker: 'GOOGL',
    industry: 'Cloud Infrastructure & Scaled Computing',
    headquarters: 'Mountain View, CA',
    description: 'Powers global search, Android, YouTube, and Google Cloud with strict zero-downtime distributed systems.',
    culture: 'High technical rigor, collaborative cross-functional impact, and focus on scalable engineering practices.',
    competencies: ['Distributed Systems', 'FastAPI', 'Python', 'Go', 'System Architecture', 'Redis', 'Kafka', 'PostgreSQL', 'Docker', 'Kubernetes', 'Idempotency'],
    hiringStages: [
      {
        title: 'Round 1: Numerical Reasoning & Platform Aptitude',
        questionCount: 10,
        format: 'Analytical Logic & Quantitative Estimation',
        focus: 'Uptime SLA depletion math, in-memory cache capacity sizing, network bandwidth saturation, and error budgets.',
      },
      {
        title: 'Round 2: Systems Architecture & Domain Reliability',
        questionCount: 10,
        format: 'Distributed Engineering Scenarios',
        focus: 'Distributed locking (Redlock), circuit breakers, zero-downtime database migrations, and OpenTelemetry tracing.',
      },
    ],
    roles: [
      {
        id: 'google-sde2',
        title: 'Software Engineer II (SDE-2)',
        track: 'tech',
        level: 'L4 / Mid-Level',
        difficulty: 'medium',
        requiredSkills: ['Python', 'Distributed Systems', 'Redis', 'Kafka', 'PostgreSQL', 'Docker'],
        jobDescription: `Job Title: Software Engineer II (SDE-2)
Company: Google
Location: Mountain View, CA / Remote

About the Role:
As an SDE-2 at Google, you will build and scale distributed platforms powering millions of queries per second. You will design resilient APIs, optimize database queries, prevent cascading failures with circuit breakers, and uphold 99.99% service level objectives.

Responsibilities:
- Build high-scale backend services in Python, Go, Java, or C++.
- Optimize distributed storage, caching (Redis/Memcached), and asynchronous event streaming (Kafka/PubSub).
- Troubleshoot tail latency (p99/p999) and conduct post-incident root cause analyses (RCAs).
- Implement idempotent endpoints and zero-downtime database migrations.

Requirements:
- 3+ years of professional backend software engineering experience.
- Strong knowledge of data structures, algorithms, concurrency, and distributed system design.`,
      },
      {
        id: 'google-staff-infra',
        title: 'Staff Platform Infrastructure Engineer',
        track: 'tech',
        level: 'L6 / Staff',
        difficulty: 'hard',
        requiredSkills: ['Distributed Systems', 'System Architecture', 'High Availability', 'Kubernetes', 'Kafka'],
        jobDescription: `Job Title: Staff Platform Infrastructure Engineer
Company: Google Cloud
Location: Sunnyvale, CA / Remote

Lead architectural decisions across core cloud compute and container orchestration clusters, maintaining 99.999% availability under multi-region failovers.`,
      },
    ],
  },
  {
    id: 'stripe',
    name: 'Stripe',
    industry: 'Financial Infrastructure & Payments API',
    headquarters: 'San Francisco, CA / Dublin',
    description: 'Builds economic infrastructure for the internet, processing hundreds of billions in annual transaction volume.',
    culture: 'Extreme attention to API craft, strict idempotent design, and operational excellence under zero-loss requirements.',
    competencies: ['Idempotency', 'Python', 'FastAPI', 'Redis', 'PostgreSQL', 'Kafka', 'System Architecture', 'High Availability', 'Distributed Systems'],
    hiringStages: [
      {
        title: 'Round 1: Payment Sizing & Financial Systems Logic',
        questionCount: 10,
        format: 'Quantitative Sizing & Ledger Logic',
        focus: 'Peak transaction volume sizing, error budget depletion, API throughput, and rate limit bucket sizing.',
      },
      {
        title: 'Round 2: Payment Gateway Reliability & Idempotency',
        questionCount: 10,
        format: 'Mission-Critical Architecture Scenarios',
        focus: 'Idempotency keys, dual-writes, banking network timeouts, circuit breakers, and parallel schema migrations.',
      },
    ],
    roles: [
      {
        id: 'stripe-backend-lead',
        title: 'Senior Backend Engineer (Payment Infrastructure)',
        track: 'tech',
        level: 'Senior (L5)',
        difficulty: 'hard',
        requiredSkills: ['Python', 'FastAPI', 'PostgreSQL', 'Redis', 'Kafka', 'Distributed Systems', 'Idempotency'],
        jobDescription: `Job Title: Senior Software Engineer (Payment Infrastructure)
Company: Stripe
Location: San Francisco, CA / Remote

About the Role:
At Stripe, we build financial infrastructure that powers global commerce. We are looking for an experienced Senior Software Engineer to join our Core Payment Routing & Reliability team, handling billions of dollars in transaction volume with strict zero-downtime tolerance.

Key Responsibilities:
- Design and operate high-throughput payment routing services with 99.999% reliability.
- Build fault-tolerant distributed systems capable of handling unexpected upstream banking gateway failures with automated idempotent retries.
- Implement database connection pooling, distributed locks (Redlock), and zero-downtime schema migrations.

Requirements:
- 5+ years of software engineering experience delivering production backend systems at scale.
- Deep hands-on experience with SQL databases, distributed caching (Redis), and message brokers.`,
      },
    ],
  },
  {
    id: 'amazon',
    name: 'Amazon',
    ticker: 'AMZN',
    industry: 'E-Commerce & AWS Cloud Services',
    headquarters: 'Seattle, WA',
    description: 'Earth’s most customer-centric enterprise, powering world-class e-commerce, cloud infrastructure, and AI recommendations.',
    culture: 'Leadership Principles (Customer Obsession, Ownership, Bias for Action, Frugality, High Standards).',
    competencies: ['Python', 'PyTorch', 'Vector Search', 'Distributed Systems', 'AWS ECS', 'System Architecture', 'Scikit-Learn', 'Ray', 'Feature Stores'],
    hiringStages: [
      {
        title: 'Round 1: Analytical Logic & High-Volume Estimation',
        questionCount: 10,
        format: 'Scale & Metric Estimation',
        focus: 'Prime Day queue depths, cache hit ratio math, network egress cost estimation, and pipeline latency.',
      },
      {
        title: 'Round 2: Applied Architecture & Production Systems',
        questionCount: 10,
        format: 'Production Architecture Scenarios',
        focus: 'Vector retrieval with HNSW, mitigating training-serving skew, multi-region database replication, and fault tolerance.',
      },
    ],
    roles: [
      {
        id: 'amazon-lead-ml',
        title: 'Lead Machine Learning Engineer',
        track: 'data',
        level: 'L6 / Lead',
        difficulty: 'hard',
        requiredSkills: ['PyTorch', 'Python', 'Vector Search', 'Feature Stores', 'Distributed Systems', 'Scikit-Learn'],
        jobDescription: `Job Title: Lead Machine Learning Engineer (Personalization & Search)
Company: Amazon
Location: Seattle, WA / Remote

Design and deploy large-scale deep learning models and real-time retrieval architectures powering discovery across hundreds of millions of catalog items.`,
      },
      {
        id: 'amazon-sde2',
        title: 'Software Development Engineer II (SDE-2)',
        track: 'tech',
        level: 'L5 / SDE-2',
        difficulty: 'medium',
        requiredSkills: ['Python', 'Distributed Systems', 'AWS ECS', 'PostgreSQL', 'Redis', 'Docker'],
        jobDescription: `Job Title: Software Development Engineer II
Company: Amazon AWS
Location: Seattle, WA / Remote

Scale core AWS cloud orchestration services handling millions of concurrent tenant operations.`,
      },
    ],
  },
  {
    id: 'salesforce',
    name: 'Salesforce',
    ticker: 'CRM',
    industry: 'Enterprise CRM & Cloud Business Applications',
    headquarters: 'San Francisco, CA',
    description: 'Global leader in enterprise customer relationship management, sales enablement, and enterprise SaaS platforms.',
    culture: 'Customer success, stakeholder alignment, rigorous MEDDPICC sales execution, and long-term trust.',
    competencies: ['MEDDPICC', 'Sales Methodologies', 'Pipeline Management', 'Enterprise Deal Closing', 'Executive Discovery', 'Negotiation', 'CRM'],
    hiringStages: [
      {
        title: 'Round 1: Business Reasoning & Numerical Quota Aptitude',
        questionCount: 10,
        format: 'Commercial Math & Financial Estimation',
        focus: 'Annual quota coverage ratios, Net Revenue Retention (NRR) calculations, CAC payback period, and ACV deal sizing.',
      },
      {
        title: 'Round 2: Enterprise Strategy & Commercial Execution',
        questionCount: 10,
        format: 'Complex B2B Negotiation Scenarios',
        focus: 'Multi-threaded C-suite stakeholder alignment, MEDDPICC qualification, economic buyers, and contract redlining.',
      },
    ],
    roles: [
      {
        id: 'salesforce-ae',
        title: 'Enterprise Account Executive (Sales Cloud)',
        track: 'sales',
        level: 'Senior Strategic AE',
        difficulty: 'medium',
        requiredSkills: ['MEDDPICC', 'Enterprise Deal Closing', 'Executive Discovery', 'Pipeline Management', 'Negotiation'],
        jobDescription: `Job Title: Enterprise Account Executive (Sales Cloud)
Company: Salesforce
Location: New York, NY / Remote

Drive new business revenue across Fortune 500 enterprise organizations. Own the full sales lifecycle from prospecting to C-level presentation, contract negotiation, and closing multi-year contracts over $150K ACV.`,
      },
    ],
  },
  {
    id: 'goldman-sachs',
    name: 'Goldman Sachs',
    ticker: 'GS',
    industry: 'Investment Banking & Global Securities',
    headquarters: 'New York, NY',
    description: 'Premier global financial institution advising corporations, financial sponsors, and governments on major transactions.',
    culture: 'Fiduciary excellence, precision in financial valuation, client integrity, and institutional teamwork.',
    competencies: ['DCF', 'LBO', 'M&A Valuation', 'Three-Statement Modeling', 'WACC', 'Enterprise Value', 'Financial Accounting'],
    hiringStages: [
      {
        title: 'Round 1: Quantitative Finance & Valuation Logic',
        questionCount: 10,
        format: 'Valuation & Accounting Math',
        focus: 'WACC calculation, DCF terminal growth rates, working capital adjustments, and EV-to-EBITDA multiples.',
      },
      {
        title: 'Round 2: Strategic M&A Advisory & Board Advisory',
        questionCount: 10,
        format: 'Corporate Transaction Scenarios',
        focus: 'LBO debt sizing, carve-outs vs spin-offs, defensive shareholder rights plans (poison pills), and fairness opinions.',
      },
    ],
    roles: [
      {
        id: 'goldman-ib-assoc',
        title: 'Investment Banking Associate (Global TMT)',
        track: 'finance',
        level: 'Associate (2nd/3rd Year)',
        difficulty: 'hard',
        requiredSkills: ['DCF', 'LBO', 'M&A Valuation', 'Three-Statement Modeling', 'WACC'],
        jobDescription: `Job Title: Investment Banking Associate (Technology, Media & Telecom)
Company: Goldman Sachs
Location: New York, NY

Advise leading technology enterprises on mergers and acquisitions (M&A), equity and debt financings, and corporate restructuring. Manage complex dynamic DCF, LBO, and three-statement financial models.`,
      },
    ],
  },
  {
    id: 'meta',
    name: 'Meta',
    ticker: 'META',
    industry: 'Social Platforms & Consumer Technology',
    headquarters: 'Menlo Park, CA',
    description: 'Connects over 3 billion people through Facebook, Instagram, WhatsApp, and advances cutting-edge AI research.',
    culture: 'Fast release velocity, focus on North Star metrics, rapid user experimentation, and deep product sense.',
    competencies: ['Product Discovery', 'A/B Testing', 'Cohort Retention', 'SQL', 'RICE', 'OKRs', 'Unit Economics', 'Product Management'],
    hiringStages: [
      {
        title: 'Round 1: Product Metrics & Quantitative Estimation',
        questionCount: 10,
        format: 'Metric Calculations & Funnel Math',
        focus: 'TAM estimation, onboarding drop-off funnel math, virality coefficient, and statistical power in A/B testing.',
      },
      {
        title: 'Round 2: Strategic Product Sense & Execution',
        questionCount: 10,
        format: 'User Scenarios & Product Prioritization',
        focus: 'Cannibalization trade-offs, RICE scoring, privacy vs engagement balancing, and crisis user incident response.',
      },
    ],
    roles: [
      {
        id: 'meta-pm',
        title: 'Senior Product Manager (Core Experience)',
        track: 'pm',
        level: 'IC6 / Senior PM',
        difficulty: 'medium',
        requiredSkills: ['Product Discovery', 'A/B Testing', 'Cohort Retention', 'SQL', 'Product Management'],
        jobDescription: `Job Title: Senior Product Manager (Core Experience)
Company: Meta
Location: Menlo Park, CA / Remote

Drive product vision, strategic roadmap, and execution for core user engagement experiences touching billions of users daily. Partner with engineering and data science on rapid A/B experimentation.`,
      },
    ],
  },
  {
    id: 'mckinsey',
    name: 'McKinsey & Company',
    industry: 'Global Management Consulting',
    headquarters: 'New York, NY / Global',
    description: 'Trusted advisor to the world’s leading businesses, governments, and non-profits on strategic transformation.',
    culture: 'Fact-based problem solving, MECE logic, structured communication (Pyramid Principle), and client leadership.',
    competencies: ['MECE Structuring', 'Profit Trees', 'Market Sizing', 'Financial Due Diligence', 'Executive Presentations', 'Corporate Strategy'],
    hiringStages: [
      {
        title: 'Round 1: Quantitative Logic & Business Estimation',
        questionCount: 10,
        format: 'Case Math & Mental Sizing',
        focus: 'Market sizing, break-even unit sales, profit tree variance decomposition, and synergy valuation.',
      },
      {
        title: 'Round 2: Structured Problem Solving & Transformation',
        questionCount: 10,
        format: 'Strategic Executive Scenarios',
        focus: 'MECE issue tree construction, turnaround prioritization, change management, and C-suite recommendations.',
      },
    ],
    roles: [
      {
        id: 'mckinsey-consultant',
        title: 'Corporate Strategy Consultant',
        track: 'finance',
        level: 'Associate Consultant',
        difficulty: 'hard',
        requiredSkills: ['MECE Structuring', 'Profit Trees', 'Market Sizing', 'Corporate Strategy'],
        jobDescription: `Job Title: Corporate Strategy Consultant
Company: McKinsey & Company
Location: Chicago, IL / New York, NY

Partner with Fortune 500 CEOs and executive teams to address critical business issues including growth strategy, digital transformation, operational turnarounds, and organizational redesign.`,
      },
    ],
  },
  {
    id: 'apple',
    name: 'Apple',
    ticker: 'AAPL',
    industry: 'Consumer Hardware, OS & Silicon Systems',
    headquarters: 'Cupertino, CA',
    description: 'Creates iPhone, Mac, Apple Silicon, and foundational operating systems with uncompromising quality.',
    culture: 'Attention to detail, perfectionism in user experience, privacy as a human right, and deep engineering craftsmanship.',
    competencies: ['Python', 'System Architecture', 'Distributed Systems', 'PostgreSQL', 'High Availability', 'Concurrency', 'Docker'],
    hiringStages: [
      {
        title: 'Round 1: Systems Concurrency & Analytical Logic',
        questionCount: 10,
        format: 'Analytical Logic & Estimation',
        focus: 'Cache memory sizing, thread synchronization overhead, I/O bandwidth estimation, and latency budgets.',
      },
      {
        title: 'Round 2: Core Platform Architecture & Reliability',
        questionCount: 10,
        format: 'Platform Reliability Scenarios',
        focus: 'Thread contention, deadlock prevention, idempotent synchronization, and resilience under network degradation.',
      },
    ],
    roles: [
      {
        id: 'apple-systems-eng',
        title: 'Platform Software Engineer (Core OS & Services)',
        track: 'tech',
        level: 'ICT4 / Senior',
        difficulty: 'hard',
        requiredSkills: ['Python', 'Distributed Systems', 'System Architecture', 'PostgreSQL', 'Concurrency'],
        jobDescription: `Job Title: Platform Software Engineer (Core OS & Services)
Company: Apple
Location: Cupertino, CA

Build and scale foundational cloud services and operating system runtimes supporting hundreds of millions of active devices.`,
      },
    ],
  },
];

const STORAGE_KEY_CUSTOM_COMPANIES = 'hirefit_custom_scraped_companies_v1';

export function getCustomCompaniesFromStorage(): CompanyProfile[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY_CUSTOM_COMPANIES);
    if (raw) {
      return JSON.parse(raw);
    }
  } catch (e) {
    console.error('Failed to parse custom companies from storage', e);
  }
  return [];
}

export function saveCustomCompanyToStorage(company: CompanyProfile): CompanyProfile[] {
  try {
    const existing = getCustomCompaniesFromStorage();
    const filtered = existing.filter((c) => c.id.toLowerCase() !== company.id.toLowerCase());
    const updated = [company, ...filtered];
    localStorage.setItem(STORAGE_KEY_CUSTOM_COMPANIES, JSON.stringify(updated));
    return updated;
  } catch (e) {
    console.error('Failed to save custom company to storage', e);
    return [];
  }
}

export function getAllCompanies(): CompanyProfile[] {
  const custom = getCustomCompaniesFromStorage();
  const baseIds = new Set(COMPANIES_DIRECTORY.map((c) => c.id.toLowerCase()));
  const filteredCustom = custom.filter((c) => !baseIds.has(c.id.toLowerCase()));
  return [...filteredCustom, ...COMPANIES_DIRECTORY];
}

export function getCompanyById(companyId: string): CompanyProfile | undefined {
  const all = getAllCompanies();
  return all.find((c) => c.id.toLowerCase() === companyId.toLowerCase());
}

export function calculateResumeReadiness(
  candidateSkills: string[],
  companyCompetencies: string[]
): {
  score: number;
  matchedSkills: string[];
  missingSkills: string[];
} {
  const normCand = candidateSkills.map((s) => s.toLowerCase());
  const matched: string[] = [];
  const missing: string[] = [];

  companyCompetencies.forEach((comp) => {
    const isMatch = normCand.some((c) => c.includes(comp.toLowerCase()) || comp.toLowerCase().includes(c));
    if (isMatch) {
      matched.push(comp);
    } else {
      missing.push(comp);
    }
  });

  const total = companyCompetencies.length || 1;
  const ratio = matched.length / total;
  // Calibrated score range: 50% to 96%
  const score = Math.round(50 + ratio * 46);

  return {
    score,
    matchedSkills: matched,
    missingSkills: missing,
  };
}
