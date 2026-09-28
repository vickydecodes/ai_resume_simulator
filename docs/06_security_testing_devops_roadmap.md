# HireFit AI: Section 14, 15, 16, 17 & 18 - Security, Testing, DevOps, Ethics & Roadmap

---

## 14. SECURITY, PRIVACY & COMPLIANCE

### 14.1 PII Scrubbing & Prompt Injection Defense

1. **Resume PII Redaction:** Pre-processing pipelines automatically identify and redact candidate phone numbers, physical addresses, and social security numbers prior to LLM submission.
2. **Untrusted Input Delimiters:** All untrusted user content (resume text, scraped web DOMs, candidate answers) is wrapped inside `<untrusted_content>` tags in LLM prompts. System instructions explicitly direct the LLM to ignore any command overrides embedded inside untrusted blocks.
3. **File Size & Format Constraints:** Uploads are strictly capped at 5 MB and checked against `.pdf` and `.docx` magic byte headers.

---

## 15. TESTING & QUALITY ASSURANCE

### 15.1 Backend Test Automation (`pytest`)

The backend includes automated test coverage spanning:
- `test_health.py`: Verifies FastAPI ASGI transport and health check JSON response.
- `test_resume_parser.py`: Tests `pdfplumber` and `python-docx` text extraction and LLM schema validation.
- `test_scraper.py`: Validates `httpx`/`BS4` scraping fallback and caching mechanisms.
- `test_interview_engine.py`: Tests state machine adaptation rules, difficulty scaling (1-5), and seniority question total calculations.
- `test_scorer.py`: Validates category weighting formulas and calibrated sigmoid selection probability math.

---

## 16. DEVOPS, DEPLOYMENT & COST ESTIMATION

### 16.1 Infrastructure Cost Estimate (Monthly MVP Scale)

| Resource Layer | Infrastructure Provider | Specifications | Monthly Cost (USD) |
| :--- | :--- | :--- | :--- |
| **API Application Server** | AWS ECS / Render / Fly.io | 2 x 1-vCPU / 2GB RAM container instances | ~$25.00 |
| **Database** | MongoDB Atlas | M10 Cluster (10GB Storage, Shared Tier) | ~$30.00 |
| **LLM Inference API** | Anthropic / OpenAI API | ~1000 simulated interview sessions / month | ~$45.00 |
| **Frontend CDN** | Vercel / Cloudflare Pages | Global Edge CDN hosting | $0.00 (Free Tier) |
| **TOTAL ESTIMATED COST** | | | **~$100.00 / month** |

---

## 17. ETHICAL CONSIDERATIONS & ALGORITHMIC BIAS MITIGATION

- **Empirical Probability Disclaimer:** Selection probability is explicitly labeled as a mock prep estimation, preventing candidate over-reliance.
- **Objective Rubrics:** LLM evaluation prompts enforce objective criteria (technical correctness, depth, STAR structure) to eliminate subjective style or cultural bias.

---

## 18. PRODUCT ROADMAP & FUTURE ENHANCEMENTS

- **Phase 1 (Current MVP):** Single-question text interview engine, resume parsing, company scraping, MongoDB caching, calibrated probability scoring report.
- **Phase 2:** Multi-candidate comparative benchmark analytics, PDF report download exporter.
- **Phase 3:** IDE integration extension for practicing system architecture diagrams.
