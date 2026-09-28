# HireFit AI: Section 11, 12 & 13 - Database, API & Frontend Design

---

## 11. DATABASE DESIGN (MONGODB)

### 11.1 Document Collections & JSON Schemas

HireFit AI utilizes MongoDB for document persistence. Below are the core collections:

#### Collection 1: `sessions`
```json
{
  "_id": "ObjectId",
  "session_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "company_name": "Stripe",
  "role_title": "Senior Backend Engineer",
  "status": "in_progress",
  "current_turn": 3,
  "total_questions_planned": 8,
  "current_difficulty": 4,
  "resume_analysis": {
    "candidate_name": "Alex Rivera",
    "experience_years": 6.5,
    "skills": ["Python", "FastAPI", "Go", "PostgreSQL", "Redis"],
    "key_strengths": ["High-throughput API design", "Database query optimization"],
    "identified_gaps": ["Limited Kubernetes cluster management"]
  },
  "role_analysis": {
    "role_title": "Senior Backend Engineer",
    "seniority_level": "Senior",
    "required_skills": ["Go", "Distributed Systems", "SQL", "gRPC"],
    "likely_topics": ["Idempotency", "Database Locking", "Distributed Transactions"]
  },
  "company_info": {
    "company_name": "Stripe",
    "what_they_do": "Financial infrastructure platform for online business.",
    "tech_stack": ["Ruby", "Go", "Java", "Mongo", "Redis"],
    "culture": ["Rigorous technical writing", "User obsession"]
  },
  "turns": [
    {
      "turn_number": 1,
      "question": "Welcome! Can you describe an architectural trade-off you made in a recent payment system?",
      "topic": "Background & System Architecture",
      "difficulty": 3,
      "user_answer": "In my previous project, we chose PostgreSQL with Redis read-through caching instead of Mongo...",
      "evaluation": {
        "relevance_score": 90,
        "depth_score": 85,
        "correctness_score": 88,
        "communication_score": 92,
        "turn_score": 88.5,
        "feedback": "Excellent technical breakdown using concrete system trade-offs."
      }
    }
  ],
  "created_at": "ISODate('2026-09-29T00:00:00Z')",
  "updated_at": "ISODate('2026-09-29T00:05:00Z')"
}
```

#### Collection 2: `company_cache` (TTL Index = 7 Days)
```json
{
  "_id": "ObjectId",
  "company_name_lower": "stripe",
  "company_name": "Stripe",
  "scraped_at": "ISODate('2026-09-29T00:00:00Z')",
  "info": {
    "company_name": "Stripe",
    "what_they_do": "Global payment processing platform",
    "tech_stack": ["Go", "Ruby", "Redis", "Kafka"],
    "products": ["Stripe Connect", "Stripe Billing"],
    "is_limited_data": false
  }
}
```

### 11.2 Indexing Strategy & Retention

- `company_cache`: `{ "scraped_at": 1 }` with `expireAfterSeconds: 604800` (7 days TTL).
- `company_cache`: `{ "company_name_lower": 1 }` with `unique: true`.
- `sessions`: `{ "created_at": -1 }`.
- `sessions`: `{ "session_id": 1 }` with `unique: true`.

---

## 12. API DESIGN & FASTAPI CONTRACT SPECIFICATIONS

### 12.1 Endpoint Summary Table

| HTTP Method | Route Endpoint | Request Payload | Response Model | Description |
| :--- | :--- | :--- | :--- | :--- |
| `POST` | `/api/sessions` | Multipart (`resume`, `company`, `role`) | `SessionCreateResponse` | Upload resume, trigger background context analysis, initialize session. |
| `GET` | `/api/sessions/{id}` | Path param `id` | `SessionDetailResponse` | Get status, parsed resume, role profile, and company info summary. |
| `POST` | `/api/sessions/{id}/start` | None | `InterviewQuestionResponse` | Start interview loop and return Turn 1 question. |
| `POST` | `/api/sessions/{id}/answer` | `{ "answer": "..." }` | `InterviewQuestionResponse` | Submit text answer, run turn evaluation & adaptation, return next question or final flag. |
| `GET` | `/api/sessions/{id}/result` | Path param `id` | `EvaluationReportResult` | Generate & retrieve full evaluation report with selection probability. |
| `GET` | `/api/health` | None | `{ "status": "healthy" }` | Health check endpoint. |

---

## 13. FRONTEND ARCHITECTURE & SHADCN COMPONENTS

### 13.1 Screen Specifications & Component Mapping

The frontend is constructed exclusively using standard **shadcn/ui** components without custom design libraries or heavy animations:

1. **Setup Page (`/setup`):**
   - Built with `Card`, `CardHeader`, `CardTitle`, `CardContent`, `Input`, `Label`, `Button`, `Alert`, `Sonner toast`.
   - Allows drop/file upload of PDF/DOCX resume, text inputs for company name and target role.
2. **Interview Page (`/interview/:id`):**
   - Built with `Card`, `ScrollArea`, `Textarea`, `Button`, `Badge`, `Progress`, `Separator`, `Skeleton`.
   - Displays real-time progress bar (Turn X of Y), topic badge, difficulty indicator (1-5), active single question box, scrollable turn history, and text answer submission box (`Cmd + Enter`).
3. **Result Page (`/result/:id`):**
   - Built with `Card`, `Tabs`, `TabsList`, `TabsTrigger`, `TabsContent`, `Progress`, `Badge`, `Alert`, `AlertTitle`, `AlertDescription`, `Separator`.
   - Displays overall score (0-100), estimated selection probability (%), category score breakdown progress bars, top strengths, top weaknesses, actionable improvement tips, and full interview transcript log.
