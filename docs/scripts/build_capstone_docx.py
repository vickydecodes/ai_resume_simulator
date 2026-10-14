import os
from docx import Document
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for margin_name, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{margin_name}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def set_cell_background(cell, hex_color):
    shading_elm = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    cell._tc.get_or_add_tcPr().append(shading_elm)

def set_table_borders(table, color="D3D3D3", sz="4", val="single"):
    tblPr = table._tbl.tblPr
    borders = parse_xml(
        f'<w:tblBorders {nsdecls("w")}>'
        f'  <w:top w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:bottom w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:left w:val="none"/>'
        f'  <w:right w:val="none"/>'
        f'  <w:insideH w:val="{val}" w:sz="{sz}" w:space="0" w:color="{color}"/>'
        f'  <w:insideV w:val="none"/>'
        f'</w:tblBorders>'
    )
    tblPr.append(borders)

def build_report_docx():
    doc = Document()

    # Page setup - Standard 1 inch margins
    sections = doc.sections
    for section in sections:
        section.top_margin = Inches(1)
        section.bottom_margin = Inches(1)
        section.left_margin = Inches(1.25)
        section.right_margin = Inches(1)

    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)

    # -------------------------------------------------------------
    # PAGE 1: TITLE PAGE
    # -------------------------------------------------------------
    p = doc.add_paragraph()
    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run("CAPSTONE PROJECT REPORT\nON\n")
    r.font.size = Pt(16)
    r.font.bold = True

    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_title = p_title.add_run("AI INTERVIEW SIMULATOR: ADAPTIVE TARGET-COMPANY & ROLE-SPECIFIC INTERVIEW PLATFORM\n\n")
    r_title.font.size = Pt(18)
    r_title.font.bold = True

    p_author = doc.add_paragraph()
    p_author.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_author = p_author.add_run("DEVELOPER / CANDIDATE\nRA2532014020095\n\nSubmitted to the\nDEPARTMENT OF DATA SCIENCE\n\nUnder the guidance of\nDr. Gayathiri A, MSc., M.Phil., MCA, Ph.D\nAssistant Professor\n\nMASTER OF SCIENCE IN APPLIED DATA SCIENCE\n\n")
    r_author.font.size = Pt(12)
    r_author.font.bold = True

    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_inst = p_inst.add_run("SRM INSTITUTE OF SCIENCE AND TECHNOLOGY\nRamapuram, Chennai - 89\n\nOCTOBER 2026")
    r_inst.font.size = Pt(14)
    r_inst.font.bold = True

    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 2: BONAFIDE CERTIFICATE
    # -------------------------------------------------------------
    p_cert_head = doc.add_paragraph()
    p_cert_head.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_cert_head = p_cert_head.add_run("SRM INSTITUTE OF SCIENCE AND TECHNOLOGY\nFACULTY OF LIBERAL ARTS AND BUSINESS STUDIES\nRamapuram, Chennai\n\nDEPARTMENT OF DATA SCIENCE\n\n")
    r_cert_head.font.size = Pt(13)
    r_cert_head.font.bold = True

    p_bonafide = doc.add_paragraph()
    p_bonafide.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_bonafide = p_bonafide.add_run("BONAFIDE CERTIFICATE\n\n")
    r_bonafide.font.size = Pt(15)
    r_bonafide.font.bold = True
    r_bonafide.font.underline = True

    p_cert_body = doc.add_paragraph()
    p_cert_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    r_cert_body = p_cert_body.add_run(
        "Certified that this Capstone Project report titled AI INTERVIEW SIMULATOR: ADAPTIVE TARGET-COMPANY & ROLE-SPECIFIC INTERVIEW PLATFORM is the bonafide work of CANDIDATE [RA2532014020095] who carried out the Capstone Project work under my supervision.\n\n\n\n"
    )
    r_cert_body.font.size = Pt(12)

    # Signatures table
    table_sig = doc.add_table(rows=2, cols=2)
    table_sig.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_sig.autofit = False

    cell_00 = table_sig.cell(0, 0)
    cell_00.paragraphs[0].add_run("Signature of Internal Guide").font.bold = True
    cell_01 = table_sig.cell(0, 1)
    cell_01.paragraphs[0].add_run("Signature of Head of the Department").font.bold = True

    cell_10 = table_sig.cell(1, 0)
    cell_10.paragraphs[0].add_run("\n\nSignature of Internal Examiner").font.bold = True
    cell_11 = table_sig.cell(1, 1)
    cell_11.paragraphs[0].add_run("\n\nSignature of External Examiner").font.bold = True

    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 3: ABSTRACT
    # -------------------------------------------------------------
    p_abs_title = doc.add_paragraph()
    p_abs_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_abs_title = p_abs_title.add_run("ABSTRACT\n\n")
    r_abs_title.font.size = Pt(14)
    r_abs_title.font.bold = True

    abstract_text = (
        "AI Interview Simulator (HireFit AI) is an advanced data-driven web application designed to prepare job seekers for technical selection loops through company-specific and role-tailored mock interviews. Traditional candidate preparation relies on generic static problem sets or uncalibrated feedback loops. The proposed system synthesizes candidate resume profiles (PDF/DOCX), target role descriptions, and real-time scraped company intelligence (tech stack, core products, corporate values) to conduct interactive, text-only mock interviews.\n\n"
        "The system executes a single-question-at-a-time state machine where question topics, difficulty levels (1 to 5), and interview length (min 5, default 8, max 15 questions) adapt dynamically based on candidate performance. Post-interview evaluations utilize a multi-metric rubric (Resume Fit 25%, Technical Knowledge 35%, Communication 15%, Problem Solving 15%, Company Awareness 10%) combined with a mathematically calibrated logistic sigmoid function to estimate candidate selection probability.\n\n"
        "Keywords: AI Mock Interview, Adaptive Assessment, Resume Parsing, Web Scraping, Pydantic V2, FastAPI, React, shadcn/ui, MongoDB, OpenRouter, Machine Learning Evaluation."
    )
    p_abs = doc.add_paragraph(abstract_text)
    p_abs.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    doc.add_page_break()

    # -------------------------------------------------------------
    # PAGE 4: ACKNOWLEDGEMENT
    # -------------------------------------------------------------
    p_ack_title = doc.add_paragraph()
    p_ack_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r_ack_title = p_ack_title.add_run("ACKNOWLEDGEMENT\n\n")
    r_ack_title.font.size = Pt(14)
    r_ack_title.font.bold = True

    ack_text = (
        "I extend my sincere gratitude to the Chancellor, Dr. T. R. PACHAMUTHU and to Chairman Dr. R. SHIVAKUMAR of SRM Institute of Science and Technology for providing me the opportunity to pursue the MASTER OF SCIENCE IN APPLIED DATA SCIENCE degree.\n\n"
        "I express my sincere gratitude to Dr. GANESH V. RADHAKRISHNAN, Dean (FLABS), SRM IST, Ramapuram for his support and encouragement.\n\n"
        "I record my heartfelt gratitude to Dr. R. BALABHASKAR, Deputy Dean-Admin, Dr. V. SARAVANAN, Deputy Dean – Academics, and Dr. D. SIVANESAN, Deputy Dean – Research for their valuable guidance.\n\n"
        "I extend my sincere thanks to Dr. N VIJAYALAKSHMI, Associate Professor and Head, Department of Data Science, and my guide Dr. Gayathiri A, Assistant Professor, for their continuous guidance and encouragement throughout this capstone project work."
    )
    p_ack = doc.add_paragraph(ack_text)
    p_ack.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    doc.add_page_break()

    # -------------------------------------------------------------
    # CHAPTERS 1 TO 9
    # -------------------------------------------------------------
    chapters = [
        ("1. INTRODUCTION", [
            ("1.1 PROJECT INTRODUCTION", "AI Interview Simulator (HireFit AI) is an end-to-end web application that simulates real-world corporate interview loops. By combining candidate resume extraction, target job title profiling, and real-time scraped target company intelligence, the platform generates tailored, single-question technical interviews that adapt dynamically in difficulty and topic."),
            ("1.2 BACKGROUND", "Recruitment loops for technical software engineering and data science roles are highly specialized across organizations. A candidate applying for a backend role at Stripe is evaluated on idempotency, database locking, and microservices resilience, whereas the same title at a consumer e-commerce startup focuses on rapid prototyping and search indexing. Generic mock platforms fail to capture company operational context."),
            ("1.3 PROBLEM STATEMENT", "Traditional interview prep tools suffer from context blindness, static question ordering, and uncalibrated pass/fail feedback. Candidates lack empirical feedback on whether performance bottlenecks stem from resume misalignment, shallow technical depth, or lack of target company awareness."),
            ("1.4 DATA-ORIENTED VIEW OF THE PROBLEM", "The system transforms candidate resume data R, role specification J, and scraped company intelligence C into an active conversation context state. Each candidate response A is evaluated across relevance, depth, correctness, and communication structure to determine subsequent state transitions."),
            ("1.5 ORGANIZATION OF THE REPORT", "This report is structured into nine chapters covering working environment, system analysis, architectural design, implementation details, testing strategy, evaluation conclusions, code appendices, and bibliography."),
            ("1.6 SIGNIFICANCE OF THE PROJECT", "HireFit AI democratizes access to company-tailored interview coaching, equipping candidates with actionable sub-score rubrics, concrete remediation recommendations, and an empirical estimated selection probability.")
        ]),
        ("2. WORKING ENVIRONMENT", [
            ("2.1 HARDWARE REQUIREMENT", "Development and runtime require standard computing resources: Intel Core i5 / AMD Ryzen 5 CPU, 8 GB RAM (16 GB recommended), 256 GB SSD storage, and a stable broadband internet connection."),
            ("2.2 SOFTWARE REQUIREMENT", "The system utilizes Python 3.10+ (FastAPI, Pydantic V2, Motor, httpx, BeautifulSoup4, pdfplumber, python-docx), Node.js 18+ (React 19, Vite, TypeScript, Tailwind CSS v4, shadcn/ui), and MongoDB 6.0+."),
            ("2.3 SYSTEM SOFTWARE", "Operating System: Windows 11 / Linux / macOS. Package Manager: pip & npm. Runtime: Python 3.10 ASGI Uvicorn server."),
            ("2.4 DEVELOPMENT ENVIRONMENT", "Structured workspace organized into /backend (FastAPI services, models, routers, prompts, tests) and /frontend (React pages, components/ui, api layer)."),
            ("2.5 TECHNOLOGY STACK", "Data Layer: MongoDB with 7-day TTL index on company cache. Processing Layer: Async Python httpx/Playwright scraper + pdfplumber resume parser. Engine Layer: Adaptive Interview State Machine. Interface Layer: React + shadcn/ui components.")
        ]),
        ("3. SYSTEM ANALYSIS", [
            ("3.1 FEASIBILITY STUDY", "Technical, economic, operational, schedule, and ethical feasibility evaluations confirm that open-source frameworks (FastAPI, React, MongoDB) and provider-agnostic LLM integration make the system highly practical, performant, and cost-effective (~$100/mo cloud operating cost)."),
            ("3.2 EXISTING SYSTEM", "Traditional preparation platforms rely on static question banks (e.g., LeetCode), generic ChatGPT prompts, or video avatar simulators with high response latency and zero company intelligence integration."),
            ("3.3 DRAWBACKS OF EXISTING SYSTEM", "Context blindness, static 5-question linear sequence, uncalibrated subjective feedback, high visual latency, and lack of target company operational alignment."),
            ("3.4 PROPOSED SYSTEM", "HireFit AI introduces a text-only, single-question adaptive state machine powered by real-time scraped company context, automated resume parsing, dynamic difficulty scaling (1-5), adaptive session length (5-15 turns), and mathematically calibrated selection probability."),
            ("3.5 BENEFITS OF PROPOSED SYSTEM", "High personalization, realistic single-question interview flow, zero visual distraction, immediate feedback, and privacy-first candidate data safeguards."),
            ("3.6 SCOPE OF THE PROJECT", "Targeted at software engineers, data scientists, product managers, and technical applicants practicing for corporate selection loops."),
            ("3.7 SYSTEM REQUIREMENT SPECIFICATION", "Includes functional requirements (FR-01 through FR-18) for parsing, scraping, adaptive control, and report rendering, alongside non-functional requirements (NFR-01 through NFR-08) for latency (<200ms non-LLM), scale, and PII privacy.")
        ]),
        ("4. SYSTEM DESIGN", [
            ("4.1 SYSTEM ARCHITECTURE", "5-layer architecture: Presentation Layer (React + shadcn/ui) -> Gateway & Security Layer (FastAPI + PII Scrubber) -> Ingestion Layer (Parser + Scraper) -> Adaptive Engine Layer (State Machine + Evaluator) -> Data Storage Layer (MongoDB)."),
            ("4.2 USE CASES", "Primary use cases: Session Setup & Upload, Context Ingestion, Interactive Single-Question Mock Loop, Response Submission, Adaptive State Update, and Performance Report Generation."),
            ("4.3 DATA FLOW", "Resume Upload -> Parsing -> Company Scraping -> Session Document Creation -> Question 1 Generation -> User Answer -> Turn Evaluator -> Adaptation Rule Check -> Next Question or Final Report."),
            ("4.4 PREPROCESSING DESIGN", "PDF/DOCX layout text extraction, PII redaction (email/phone), untrusted content XML wrapping (<untrusted_content>), and section segmentation."),
            ("4.5 MODEL & ENGINE DESIGN", "State machine with dynamic difficulty scaling rules (D_{t+1} = min(D_t+1, 5) if score >= 80, max(D_t-1, 1) if score <= 45), topic rotation matrix, and early completion / extension triggers."),
            ("4.6 ERROR HANDLING", "Graceful fallback to synthetic domain intelligence when company web scraping is blocked or times out, and Pydantic schema auto-retry on LLM JSON validation errors."),
            ("4.7 PERFORMANCE & INPUT/OUTPUT DESIGN", "Asynchronous non-blocking HTTP handlers, minimal shadcn UI layout, and clear multi-metric score breakdown.")
        ]),
        ("5. PROJECT DESCRIPTION", [
            ("5.1 OBJECTIVE", "To provide an objective, automated, company-tailored mock interview platform that evaluates candidates across technical depth, communication, and background fit."),
            ("5.2 MODULE DESCRIPTION", "Modules: Session Router, Resume Ingestion Service, Role Analyzer, Company Scraper Service (with MongoDB TTL caching), Adaptive Interview Engine, and Calibrated Scoring Service."),
            ("5.3 IMPLEMENTATION", "Built in Python 3.10+ (FastAPI) and TypeScript (React 19 + Tailwind CSS v4). Integrated with OpenRouter API (inclusionai/ling-3.0-flash-sante:free) and local mock fallback."),
            ("5.4 MODEL TRAINING & ADAPTATION", "Zero-shot / few-shot system prompt engineering enforcing strict single-question delivery and objective 4-metric turn evaluation."),
            ("5.5 MODEL EVALUATION & SCORING", "Weighted Rubric: Overall Score = 0.25*ResumeFit + 0.35*Technical + 0.15*Communication + 0.15*ProblemSolving + 0.10*CompanyAwareness. Estimated Selection Probability P_selection = 1 / (1 + exp(-0.08 * (S_effective - 70.0)))."),
            ("5.6 PREDICTION & INTERVIEW WORKFLOW", "Step-by-step turn execution from setup upload through interactive chat loop to score report visualization."),
            ("5.7 MAINTENANCE", "Regular dependency security updates, scraping selector maintenance, and index optimization.")
        ]),
        ("6. SYSTEM TESTING", [
            ("6.1 TESTING DEFINITION & OBJECTIVE", "Systematic verification of backend unit services, API routing, Pydantic data validation, and frontend component building."),
            ("6.2 TYPES OF TESTING", "Unit Testing (pytest), Integration Testing (httpx ASGI transport), Data Validation Testing (Pydantic V2), UI Component Testing, and End-to-End Build Verification."),
            ("6.3 TEST CASES", "Includes TC01 through TC07 covering health check, DOCX parsing, scraper fallback, seniority question planning, adaptation rules, and selection probability calibration. All 7 tests passed in 1.79s.")
        ]),
        ("7. CONCLUSION", [
            ("7.1 SUMMARY", "HireFit AI successfully provides an end-to-end adaptive interview preparation environment tailored to candidate background and target company culture."),
            ("7.2 LIMITATIONS", "MVP is text-only (no voice/video), relies on public web content accessibility, and evaluates architecture conceptually rather than executing live code sandboxes."),
            ("7.3 FUTURE ENHANCEMENT", "Phase 2 extensions include multi-candidate comparative analytics, downloadable PDF score reports, IDE system design plugin, and voice synthesis support.")
        ]),
        ("8. APPENDIX", [
            ("8.1 CODE & PROMPT TEMPLATES", "Production LLM prompts for resume analysis, role profiling, company scraping, single-question interview generation, turn evaluation, and score report compiling."),
            ("8.2 DATA DICTIONARY & SCHEMAS", "Detailed collection schema definitions for sessions, company_cache, resume_analysis, role_analysis, turns, and evaluation_report.")
        ]),
        ("9. BIBLIOGRAPHY AND REFERENCES", [
            ("9.1 REFERENCES", "1. FastAPI Documentation (2026). https://fastapi.tiangolo.com/\n2. React 19 & Vite Documentation (2026). https://vite.dev/\n3. MongoDB Motor Async Driver (2026). https://motor.readthedocs.io/\n4. OpenRouter Unified API (2026). https://openrouter.ai/\n5. Scikit-learn & Pydantic V2 Specifications.")
        ])
    ]

    for title, subsections in chapters:
        p_ch = doc.add_paragraph()
        r_ch = p_ch.add_run(f"\n{title}\n")
        r_ch.font.size = Pt(14)
        r_ch.font.bold = True
        p_ch.paragraph_format.space_before = Pt(12)
        p_ch.paragraph_format.space_after = Pt(6)

        for sub_title, text in subsections:
            p_sub = doc.add_paragraph()
            r_sub = p_sub.add_run(f"{sub_title}\n")
            r_sub.font.size = Pt(12)
            r_sub.font.bold = True
            p_sub.paragraph_format.space_before = Pt(6)
            p_sub.paragraph_format.space_after = Pt(2)

            p_body = doc.add_paragraph(text)
            p_body.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p_body.paragraph_format.space_after = Pt(6)

    # Save to docs folder
    docs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_docs = os.path.join(docs_dir, "HireFit_AI_Capstone_Project_Report.docx")

    doc.save(out_docs)
    print(f"[OK] Generated master Capstone Project Report DOCX at:\n - {out_docs}")

if __name__ == "__main__":
    build_report_docx()
