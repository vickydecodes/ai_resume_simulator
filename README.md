# HireFit AI: Adaptive Target-Company & Role-Specific Interview Simulator

**HireFit AI** is a web application designed to simulate real-world, company-specific technical mock interviews. By analyzing candidate resumes (PDF/DOCX), target job roles, and live scraped target company intelligence (tech stack, products, culture), the system conducts a text-only, single-question interview that dynamically adapts in topic, difficulty, and length.

---

## Technical Stack

- **Backend:** Python 3.10+, FastAPI, Pydantic v2, Motor (async MongoDB driver), `httpx`, `BeautifulSoup4`, `pdfplumber`, `python-docx`, `pytest`.
- **Database:** MongoDB (with TTL indexes for cached company intelligence).
- **Frontend:** React 19 + Vite + TypeScript, Tailwind CSS v4, styled exclusively using standard `shadcn/ui` components (`Card`, `Input`, `Textarea`, `Button`, `Progress`, `Badge`, `Tabs`, `Label`, `Skeleton`, `Alert`, `Separator`, `ScrollArea`, `Sonner toast`).
- **LLM Integration:** Provider-agnostic `LLMClient` wrapper supporting Anthropic Claude, OpenAI GPT, Google Gemini, and a robust mock fallback for keyless local testing.

---

## Core Features

1. **5 Pre-Configured Role Tracks & Company Presets:**
   - **Software Engineering (Tech):** Calibrated for Stripe, Google, and Amazon payment & distributed architecture.
   - **Enterprise Sales & GTM:** Calibrated for Salesforce and B2B SaaS MEDDPICC enterprise closing.
   - **Product Management (PM):** Metrics, TAM sizing, cohort retention, and user experimentation.
   - **Data Science & Machine Learning:** Feature stores, training-serving skew, latency, and vector search.
   - **Investment Banking & Corporate Strategy:** DCF, LBO, three-statement models, and M&A advisory.
2. **Interactive Learning & Realistic Testing Modes:**
   - **Practice Mode:** Instant feedback on option selection with concept rationale & explanation.
   - **Exam Mode:** Strict test conditions without revealing answers upfront.
   - **30-Minute Countdown Timer:** Real-time clock with pause/resume and visual urgency indicators (<5 min warning, <2 min alert).
   - **Flag for Review / Bookmarking:** Bookmark questions with visual indicators in the 1..20 question navigator.
3. **Candidate Auth & Past Session History:**
   - Candidate profile switcher / login (Name, Email, Initials) stored in `localStorage`.
   - Past Interviews scorecard drawer tracking historical scores, companies, roles, and report links.
4. **Per-Question Detailed Review:**
   - Evaluates all 20 questions upfront with candidate selection vs verified key, topic, difficulty, and concept rationale.
5. **ATS Resume Optimizer:**
   - ATS match percentage, matched core competencies, high-priority missing keyword gaps, and 3 AI-optimized copyable bullet points tailored to the target JD.
6. **One-Click Download / Print PDF:**
   - Clean `@media print` styling generating professional multi-page scorecards.

---

## Mathematical Scoring & Selection Probability Formula

The overall weighted score $S_{\text{overall}}$ is calculated across five dimensions:

$$S_{\text{overall}} = 0.25 S_{\text{resume\_fit}} + 0.35 S_{\text{technical}} + 0.15 S_{\text{communication}} + 0.15 S_{\text{problem\_solving}} + 0.10 S_{\text{company}}$$

The **Estimated Selection Probability ($P_{\text{selection}}$)** is computed via a statistically calibrated logistic sigmoid function:

$$P_{\text{selection}} = \frac{1}{1 + e^{-k (S_{\text{effective}} - S_0)}}$$

Where:
- $S_{\text{effective}} = 0.85 S_{\text{overall}} + 0.15 S_{\text{resume\_fit}}$
- $S_0 = 70.0$ (baseline threshold score expected for a competitive hiring loop)
- $k = 0.08$ (logistic curve steepness calibration constant)

> **Disclaimer:** The Estimated Selection Probability is an algorithmic preparation metric to highlight candidate strengths and skill gaps. It does NOT constitute a hiring guarantee by the target company.

---

## Quickstart & Setup Instructions

### 1. One-Click Launchers (Automated Check & Run in Separate Terminals)

Both scripts automatically verify Python `venv` and frontend `node_modules` (installing them if missing), and launch backend and frontend in separate dedicated `cmd` terminals:

- **Windows:** Double-click [`run.bat`](file:///d:/Studies/projects/my_projects/ai_resume_simulator/run.bat) or execute:
  ```cmd
  run.bat
  ```
- **Linux / macOS / Git Bash:** Execute [`run.sh`](file:///d:/Studies/projects/my_projects/ai_resume_simulator/run.sh):
  ```bash
  chmod +x run.sh
  ./run.sh
  ```

---

### 2. Prerequisites
- Python 3.10+
- Node.js 18+ & npm 9+
- MongoDB instance (Local running at `mongodb://localhost:27017` or MongoDB Atlas URI)

### 3. Manual Backend Setup & Run

```bash
# Navigate to backend directory
cd backend

# Create virtual environment (optional but recommended)
python -m venv venv
# On Windows: venv\Scripts\activate
# On Linux/macOS: source venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Create .env file from example
cp .env.example .env

# Run automated test suite
python -m pytest tests

# Start FastAPI development server
uvicorn app.main:app --reload --port 8000
```
Backend API interactive OpenAPI docs available at `http://127.0.0.1:8000/docs`.

### 3. Frontend Setup & Run

```bash
# Navigate to frontend directory
cd frontend

# Install npm dependencies
npm install

# Run Vite dev server
npm run dev
```
Open `http://localhost:5173` in your browser.

---

## Project Structure

```
.
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI application entry point
│   │   ├── core/                    # Config, DB client, LLM wrapper, Security
│   │   ├── models/                  # Pydantic v2 schemas
│   │   ├── routers/                 # Session, Interview, Score endpoints
│   │   ├── services/                # Resume, Role, Scraper, Engine, Scorer
│   │   └── prompts/                 # Modular LLM prompt templates
│   ├── tests/                       # Pytest automated test suite
│   ├── requirements.txt
│   └── .env.example
├── frontend/
│   ├── src/
│   │   ├── pages/                   # Setup, Interview, Result screens
│   │   ├── components/ui/           # shadcn/ui components
│   │   ├── lib/                     # API client & utility functions
│   │   ├── App.tsx                  # React router setup
│   │   └── main.tsx
│   ├── package.json
│   └── vite.config.ts
├── docs/                            # 60-page Master Technical Documentation
└── README.md
```

---

## Known Limitations & Future Scope

1. **Text-Only Interface:** MVP excludes voice audio synthesis, webcam video analysis, and real-time speech cadence metrics.
2. **Code Execution Sandbox:** Technical system design and algorithm questions are evaluated via prose and conceptual trade-off descriptions rather than an automated LeetCode unit-test runner.
3. **Scraping Fallback:** Web scraping relies on public HTML availability. Domains enforcing strict Cloudflare bot protection fall back to synthetic LLM company intelligence profiles marked as `is_limited_data`.
