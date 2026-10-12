export interface PreloadedRoleConfig {
  id: string;
  company: string;
  role: string;
  department: string;
  badge: string;
  track: 'tech' | 'sales' | 'pm' | 'data' | 'finance';
  difficulty: 'low' | 'medium' | 'hard';
  description: string;
  jobDescription: string;
  sampleResumeFilename: string;
  sampleResumeContent: string;
}

export const PRELOADED_ROLE_CONFIGS: PreloadedRoleConfig[] = [
  {
    id: 'google-sde2',
    company: 'Google',
    role: 'Software Engineer II (SDE-2)',
    department: 'Cloud & Infrastructure',
    badge: 'Distributed Systems & Scale',
    track: 'tech',
    difficulty: 'medium',
    description: 'Core microservices, distributed concurrency, asynchronous I/O, and platform reliability.',
    sampleResumeFilename: 'Google_SDE2_Sample_Resume.txt',
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
    sampleResumeContent: `ALEX RIVERA
Email: alex.rivera@example.com | San Francisco, CA | GitHub: github.com/alexrivera-tech

SUMMARY
Software Engineer with 4+ years of experience architecting high-throughput backend services. Expertise in Python, FastAPI, PostgreSQL, Redis, Docker, and AWS distributed microservices. Led database optimization projects reducing p99 latency by 42%.

EXPERIENCE
Backend Engineer | CloudScale Systems | 2022 – Present
- Built and maintained distributed orchestration services handling 15M monthly requests with 99.98% availability.
- Implemented asynchronous event streaming with Kafka for automated retry handling, eliminating message loss.
- Decreased API p99 response times from 320ms to 85ms via Redis distributed caching and SQL query indexing.

TECHNICAL SKILLS
- Languages: Python, Go, TypeScript, SQL
- Frameworks & Tools: FastAPI, Docker, Kubernetes, Redis, PostgreSQL, Kafka, AWS ECS`,
  },
  {
    id: 'stripe-senior-backend',
    company: 'Stripe',
    role: 'Senior Backend Engineer (Payments)',
    department: 'Payment Intelligence',
    badge: 'Idempotency & Zero-Downtime',
    track: 'tech',
    difficulty: 'hard',
    description: 'High-availability financial pipelines, payment gateways, strict idempotency, and ledger consistency.',
    sampleResumeFilename: 'Stripe_Senior_Backend_Resume.txt',
    jobDescription: `Job Title: Senior Software Engineer (Payment Infrastructure)
Company: Stripe
Location: San Francisco, CA / Remote

About the Role:
At Stripe, we build financial infrastructure that powers global commerce. We are looking for an experienced Senior Software Engineer to join our Core Payment Routing & Reliability team, handling billions of dollars in transaction volume with strict zero-downtime tolerance.

Key Responsibilities:
- Design and operate high-throughput payment routing services with 99.999% reliability.
- Build fault-tolerant distributed systems capable of handling unexpected upstream banking gateway failures with automated idempotent retries.
- Implement database connection pooling, distributed locks (Redlock), and zero-downtime schema migrations (Expand & Contract).

Requirements:
- 5+ years of software engineering experience delivering production backend systems at scale.
- Deep hands-on experience with SQL databases, distributed caching (Redis), and message brokers.`,
    sampleResumeContent: `ELENA ROSTOVA
Email: elena.rostova@example.com | San Francisco, CA | LinkedIn: linkedin.com/in/elena-rostova-dev

SUMMARY
Senior Backend Architect with 6+ years of experience building mission-critical financial software. Specialized in idempotent API design, distributed locking, and zero-downtime schema migrations.

EXPERIENCE
Senior Software Engineer | PayFlow Global | 2021 – Present
- Architected payment gateway integration processing $800M in annual transactions with zero ledger discrepancies.
- Implemented distributed idempotency keys via Redis and SQL transactions, preventing double-billing during network retries.
- Led migration of 40M database records with zero service interruption using the expand-and-contract pattern.

SKILLS
- Distributed Systems, High Availability, Idempotency, Python, Go, PostgreSQL, Redis, AWS`,
  },
  {
    id: 'amazon-lead-ml',
    company: 'Amazon',
    role: 'Lead Machine Learning Engineer',
    department: 'Personalization & Search',
    badge: 'Vector Search & Deep Learning',
    track: 'data',
    difficulty: 'hard',
    description: 'Real-time recommendation systems, vector retrieval, feature stores, and low-latency inference.',
    sampleResumeFilename: 'Amazon_ML_Engineer_Resume.txt',
    jobDescription: `Job Title: Lead Machine Learning Engineer (Personalization & Search)
Company: Amazon
Location: Seattle, WA / Remote

Role Overview:
We are seeking an experienced Lead Machine Learning Engineer to design and deploy large-scale deep learning models and real-time retrieval architectures powering discovery across hundreds of millions of catalog items.

Responsibilities:
- Build high-scale recommendation and semantic vector search systems handling tens of thousands of requests per second.
- Mitigate data leakage, covariate shift, and training-serving skew through centralized feature stores.
- Partner with product teams to optimize offline metrics (ROC-AUC, NDCG) and online business metrics (CTR, Conversion).

Requirements:
- 5+ years of production machine learning engineering experience with PyTorch, distributed computing (Spark/Ray), and low-latency serving.`,
    sampleResumeContent: `DR. MARCUS CHEN
Email: marcus.chen@example.com | San Francisco, CA | GitHub: github.com/marcuschen-ml

SUMMARY
Lead Machine Learning Engineer with 6+ years of experience building production recommendation engines, vector embeddings, and real-time fraud models at scale. Expert in PyTorch, Ray, and Triton Inference Server.

EXPERIENCE
Lead ML Engineer | RetailAI Systems | 2021 – Present
- Architected vector search and recommendation retrieval service indexing 40M items using HNSW in Pinecone and PyTorch.
- Deployed real-time classification pipeline processing 35,000 queries per second with p99 latency under 18ms.
- Eliminated training-serving skew by implementing Feast centralized feature store.

SKILLS
- PyTorch, Scikit-learn, Ray, Spark, Python, Vector DBs, Model Drift Monitoring, AWS SageMaker`,
  },
  {
    id: 'salesforce-enterprise-ae',
    company: 'Salesforce',
    role: 'Enterprise Account Executive',
    department: 'Sales Cloud Strategic',
    badge: 'MEDDPICC & $150K+ ACV Deals',
    track: 'sales',
    difficulty: 'medium',
    description: 'B2B enterprise SaaS closing, multi-threaded stakeholder alignment, MEDDPICC qualification, and contract negotiation.',
    sampleResumeFilename: 'Salesforce_AE_Resume.txt',
    jobDescription: `Job Title: Enterprise Account Executive (Sales Cloud)
Company: Salesforce
Location: New York, NY / Remote

Role Overview:
As an Enterprise Account Executive on our Strategic Accounts team, you will drive new business revenue across enterprise organizations. You will own the full sales lifecycle from prospecting to C-level presentation, contract negotiation, and closing large-scale multi-year contracts.

Responsibilities:
- Lead multi-threaded enterprise sales cycles, managing relationships from VP to C-level decision makers (CIO, CFO, CEO).
- Apply rigorous qualification frameworks (MEDDPICC) to forecast revenue accurately and maintain a 4x+ rolling pipeline.
- Negotiate complex commercial and master services agreements (MSAs) closing deals over $150K ACV.

Requirements:
- 5+ years of direct quota-carrying experience in enterprise B2B SaaS software sales.
- Proven track record of consistently exceeding annual quota targets ($1.5M+ ARR targets).`,
    sampleResumeContent: `JORDAN MILLER
Email: jordan.miller@example.com | New York, NY | LinkedIn: linkedin.com/in/jordanmiller-sales

EXECUTIVE SUMMARY
Enterprise Account Executive with 6+ years of experience leading multi-threaded B2B SaaS sales cycles. Consistent quota overachiever (124% average quota attainment across past 3 years). Expert in MEDDPICC qualification and C-level value selling.

EXPERIENCE
Senior Enterprise AE | CloudCRM Solutions | 2022 – Present
- Exceeded annual quota at 128% in 2023 and 121% in 2024, generating $3.4M in new Net ARR across Fortune 500 accounts.
- Mastered MEDDPICC qualification frameworks to reduce average sales cycle length from 180 to 115 days.
- Closed 24 enterprise contracts with average deal sizes exceeding $175,000 ARR.

SKILLS
- MEDDPICC, Challenger Sale, Multi-Threaded Negotiations, Pipeline Management, Salesforce CRM`,
  },
  {
    id: 'goldman-ib-associate',
    company: 'Goldman Sachs',
    role: 'Investment Banking Associate',
    department: 'Global TMT Group',
    badge: 'M&A Valuation & LBO Modeling',
    track: 'finance',
    difficulty: 'hard',
    description: 'Corporate M&A advisory, DCF valuations, leveraged buyout modeling, and board fairness opinions.',
    sampleResumeFilename: 'Goldman_IB_Resume.txt',
    jobDescription: `Job Title: Investment Banking Associate (Technology, Media & Telecom)
Company: Goldman Sachs
Location: New York, NY

Role Overview:
As an Investment Banking Associate in our Global TMT Group, you will play an integral role in advising leading technology enterprises on mergers and acquisitions (M&A), equity and debt financings, and corporate restructuring.

Responsibilities:
- Build, audit, and manage complex financial models including DCF, LBO, three-statement operating models, and merger consequence analyses.
- Synthesize industry market trends, valuation multiples, and competitive benchmarking into executive pitch books.
- Lead due diligence streams, coordinating directly with client C-suite executives, legal counsel, and accounting teams.

Requirements:
- 3+ years of investment banking, private equity, or top-tier financial advisory experience.
- Mastery of financial accounting, corporate valuation frameworks (DCF, comps, precedent transactions, LBO), and M&A dynamics.`,
    sampleResumeContent: `ELIZABETH VANCE
Email: elizabeth.vance@example.com | New York, NY | LinkedIn: linkedin.com/in/elizabethvance-finance

EXECUTIVE SUMMARY
Corporate Finance & M&A Associate with 5+ years of experience in discounted cash flow (DCF) valuation, LBO modeling, and operational restructuring. Executed $2.8B+ in aggregate transaction volume across technology and financial services sectors.

EXPERIENCE
Investment Banking Associate | Morgan Capital Partners | 2022 – Present
- Built dynamic three-statement operating models, DCF valuations, and LBO models for 8 closed M&A transactions.
- Conducted sensitivity analysis across terminal growth rates, WACC discount rates, and EBITDA exit multiples.
- Drafted confidential information memoranda (CIMs), fairness opinions, and board presentations.

SKILLS
- DCF, LBO, Merger Consequences, WACC/CAPM, Enterprise Value vs Equity Value, Advanced Excel`,
  },
  {
    id: 'meta-senior-pm',
    company: 'Meta',
    role: 'Senior Product Manager',
    department: 'Core User Experience',
    badge: 'Growth Funnels & A/B Testing',
    track: 'pm',
    difficulty: 'medium',
    description: 'Product sense, cohort retention, North Star metric trade-offs, TAM sizing, and statistical experimentation.',
    sampleResumeFilename: 'Meta_PM_Sample_Resume.txt',
    jobDescription: `Job Title: Senior Product Manager (Core Experience)
Company: Meta
Location: Menlo Park, CA / Remote

Role Overview:
Drive product vision, strategic roadmap, and execution for core user engagement experiences touching billions of users daily. You will work closely with engineering leaders, data scientists, and UX researchers.

Responsibilities:
- Define product strategy and measurable North Star metrics for user-facing features.
- Formulate testable hypotheses, design quantitative A/B experiments, and analyze cohort retention.
- Balance consumer usability with privacy compliance and business monetization goals.

Requirements:
- 5+ years of product management experience shipping digital products at scale.
- Strong analytical and quantitative skills (A/B testing, cohort retention, SQL, statistical significance).`,
    sampleResumeContent: `PRIYA SHARMA
Email: priya.sharma@example.com | Seattle, WA | LinkedIn: linkedin.com/in/priyasharma-pm

SUMMARY
Data-driven Senior Product Manager with 6+ years of experience leading cross-functional teams in zero-to-one product discovery, growth metrics, and high-scale consumer platform features.

EXPERIENCE
Senior Product Manager | StreamPlatform | 2022 – Present
- Owned consumer engagement roadmap across web and mobile apps, increasing 30-day retention from 42% to 56%.
- Managed quarterly prioritization using RICE and OKR frameworks across 18 engineers and 3 designers.
- Partnered with Data Science to execute 40+ rigorous A/B experiments with statistically significant sample sizes.

SKILLS
- RICE, OKRs, Product Discovery, Customer Journey Mapping, A/B Testing, Amplitude, SQL`,
  },
  {
    id: 'mckinsey-strategy-consultant',
    company: 'McKinsey & Company',
    role: 'Corporate Strategy Consultant',
    department: 'Management Consulting',
    badge: 'MECE Case Structuring & ROI',
    track: 'finance',
    difficulty: 'hard',
    description: 'Structured strategic problem solving, market sizing, profit tree decomposition, and executive transformation.',
    sampleResumeFilename: 'McKinsey_Consultant_Resume.txt',
    jobDescription: `Job Title: Corporate Strategy Consultant
Company: McKinsey & Company
Location: Chicago, IL / New York, NY

Role Overview:
Partner with Fortune 500 CEOs and executive teams to address critical business issues including growth strategy, digital transformation, operational turnarounds, and organizational redesign.

Responsibilities:
- Structure complex, ambiguous business problems using MECE (Mutually Exclusive, Collectively Exhaustive) issue trees.
- Quantify market sizing, cost optimization opportunities, and capital allocation priorities.
- Synthesize quantitative data into compelling executive recommendations.

Requirements:
- 3+ years of management consulting or corporate strategy experience.
- Exceptional analytical problem-solving skills and executive communication capabilities.`,
    sampleResumeContent: `DAVID KANG
Email: david.kang@example.com | Chicago, IL | LinkedIn: linkedin.com/in/davidkang-consulting

SUMMARY
Management Consultant with 4+ years of experience advising Fortune 500 enterprises on revenue turnaround, zero-based budgeting, and supply chain restructuring.

EXPERIENCE
Strategy Consultant | Apex Advisory Group | 2021 – Present
- Structured growth strategy for a global retail client, identifying $55M in cost-saving operational efficiencies.
- Built profit tree models decomposing revenue variance across pricing, volume, and customer segment mix.

SKILLS
- MECE Structuring, Profit Trees, TAM Analysis, Financial Due Diligence, Executive Presentations`,
  },
  {
    id: 'apple-systems-engineer',
    company: 'Apple',
    role: 'Systems Software Engineer',
    department: 'Core OS & Hardware Systems',
    badge: 'Memory Safety & Concurrency',
    track: 'tech',
    difficulty: 'hard',
    description: 'Low-latency operating systems, thread synchronization, memory management, and hardware-software performance.',
    sampleResumeFilename: 'Apple_Systems_Resume.txt',
    jobDescription: `Job Title: Systems Software Engineer (Core OS)
Company: Apple
Location: Cupertino, CA

Role Overview:
Join the team developing foundational operating system services and platform runtimes powering Apple devices. You will work on low-level system performance, synchronization primitives, and resource management.

Responsibilities:
- Implement robust, low-latency system services with strict memory safety and deterministic latency.
- Diagnose thread contention, priority inversions, and hardware cache bottlenecks.
- Build automated stress testing suites simulating peak I/O conditions.

Requirements:
- 4+ years of systems programming experience in C, C++, Rust, or Swift.
- Deep understanding of OS internals, virtual memory, paging, and lock-free data structures.`,
    sampleResumeContent: `LIAM O'CONNOR
Email: liam.oconnor@example.com | Cupertino, CA | GitHub: github.com/liamoconnor-systems

SUMMARY
Systems Software Engineer with 5+ years of experience in low-level concurrency, memory allocators, and operating system runtimes.

EXPERIENCE
Systems Engineer | NexaOS Labs | 2021 – Present
- Designed lock-free ring buffer for audio/telemetry streaming reducing inter-process latency by 35%.
- Diagnosed thread deadlocks and priority inversions using kernel tracing and profiling tools.

SKILLS
- C, C++, Rust, POSIX Threads, Virtual Memory, Cache Optimization, LLDB`,
  },
];

export function createSampleResumeForConfig(config: PreloadedRoleConfig): File {
  const blob = new Blob([config.sampleResumeContent], { type: 'text/plain' });
  return new File([blob], config.sampleResumeFilename, { type: 'text/plain' });
}
