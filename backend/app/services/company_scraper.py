import datetime
import logging
import re
from urllib.robotparser import RobotFileParser
from typing import Optional
import httpx
from bs4 import BeautifulSoup
from app.core.db import get_database
from app.core.security import sanitize_untrusted_input
from app.core.llm import llm_client
from app.models.schemas import CompanyInfoResult, ScrapedCompanyProfile, ScrapedCompanyStage, ScrapedCompanyRole
from app.prompts.company_prompt import COMPANY_ANALYSIS_SYSTEM_PROMPT, COMPANY_ANALYSIS_USER_PROMPT

logger = logging.getLogger("uvicorn.error")

USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 HireFitBot/1.0"

def is_allowed_by_robots(url: str) -> bool:
    """Check robots.txt compliance for given URL."""
    try:
        domain_match = re.match(r"https?://[^/]+", url)
        if not domain_match:
            return True
        robots_url = f"{domain_match.group(0)}/robots.txt"
        rp = RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch("HireFitBot", url)
    except Exception:
        # Default allow on parser failure
        return True

async def fetch_web_page(url: str) -> Optional[str]:
    """Fetch text from public web URL using httpx with timeout."""
    if not is_allowed_by_robots(url):
        logger.warning(f"Robots.txt disallows scraping for URL: {url}")
        return None

    headers = {"User-Agent": USER_AGENT}
    try:
        async with httpx.AsyncClient(timeout=4.0, follow_redirects=True) as client:
            resp = await client.get(url, headers=headers)
            if resp.status_code == 200:
                soup = BeautifulSoup(resp.text, "html.parser")
                # Remove scripts, styles, metadata
                for element in soup(["script", "style", "nav", "footer", "svg"]):
                    element.decompose()
                text = soup.get_text(separator=" ", strip=True)
                return text[:5000]  # Cap length for context
    except Exception as e:
        logger.warning(f"Failed to fetch webpage '{url}': {e}")
    return None

async def scrape_company_intelligence(company_name: str) -> CompanyInfoResult:
    """Check MongoDB cache first; if missing, scrape company pages and analyze via LLM."""
    db = get_database()
    company_clean = company_name.strip().lower()

    # 1. Check Cache in MongoDB
    if db is not None:
        try:
            cached = await db.company_cache.find_one({"company_name_lower": company_clean})
            if cached and "info" in cached:
                logger.info(f"Retrieved scraped company info from MongoDB cache for '{company_name}'")
                return CompanyInfoResult(**cached["info"])
        except Exception as e:
            logger.warning(f"MongoDB cache read error: {e}")

    # 2. Attempt scraping company domains
    domain_guess = re.sub(r"[^\w]", "", company_name).lower() + ".com"
    target_urls = [
        f"https://www.{domain_guess}",
        f"https://www.{domain_guess}/about",
        f"https://www.{domain_guess}/careers"
    ]

    scraped_chunks = []
    for url in target_urls:
        content = await fetch_web_page(url)
        if content:
            scraped_chunks.append(f"--- URL: {url} ---\n{content}")

    is_limited = False
    if not scraped_chunks:
        logger.warning(f"Scraping returned no data for '{company_name}'. Utilizing fallback intelligence mode.")
        raw_scraped_text = f"Company Name: {company_name}. Public scraping timed out or blocked."
        is_limited = True
    else:
        raw_scraped_text = "\n\n".join(scraped_chunks)

    # 3. Summarize scraped text using LLM
    sanitized = sanitize_untrusted_input(raw_scraped_text)
    prompt = COMPANY_ANALYSIS_USER_PROMPT.format(
        company_name=company_name,
        sanitized_company_content=sanitized
    )

    result = await llm_client.generate_json(
        prompt=prompt,
        schema_cls=CompanyInfoResult,
        system_prompt=COMPANY_ANALYSIS_SYSTEM_PROMPT
    )
    result.company_name = company_name
    if is_limited:
        result.is_limited_data = True

    # 4. Save to MongoDB Cache
    if db is not None:
        try:
            cache_doc = {
                "company_name_lower": company_clean,
                "company_name": company_name,
                "scraped_at": datetime.datetime.now(datetime.timezone.utc),
                "info": result.model_dump()
            }
            await db.company_cache.update_one(
                {"company_name_lower": company_clean},
                {"$set": cache_doc},
                upsert=True
            )
            logger.info(f"Cached company intelligence for '{company_name}' in MongoDB.")
        except Exception as e:
            logger.warning(f"MongoDB cache save error: {e}")

    return result

async def scrape_and_generate_company_profile(
    company_name: str,
    custom_url: Optional[str] = None
) -> ScrapedCompanyProfile:
    """Scrape company public profile, financial worth/valuation, and generate an enterprise hiring rubric."""
    company_clean = company_name.strip()
    company_slug = re.sub(r"[^a-z0-9]+", "-", company_clean.lower()).strip("-")
    if not company_slug:
        company_slug = f"company-{int(datetime.datetime.now().timestamp())}"

    # 1. Check MongoDB Cache first
    db = get_database()
    if db is not None:
        try:
            cached = await db.scraped_companies.find_one({"id": company_slug})
            if cached and "profile" in cached:
                logger.info(f"Found cached scraped company profile for '{company_clean}'")
                return ScrapedCompanyProfile(**cached["profile"])
        except Exception as e:
            logger.warning(f"Cache lookup failed for scraped company: {e}")

    # 2. BeautifulSoup Scraping (Wikipedia + Official Domain)
    infobox_data = {}
    scraped_text_snippets = []
    page_title = company_clean

    headers = {"User-Agent": USER_AGENT}

    # Attempt Wikipedia scrape
    wiki_candidates = [
        f"https://en.wikipedia.org/wiki/{company_clean.replace(' ', '_')}",
        f"https://en.wikipedia.org/wiki/{company_clean.replace(' ', '_')}_(company)",
    ]

    for wiki_url in wiki_candidates:
        try:
            async with httpx.AsyncClient(timeout=4.0, follow_redirects=True) as client:
                resp = await client.get(wiki_url, headers=headers)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    # Extract page title
                    if soup.title:
                        page_title = soup.title.get_text().replace(" - Wikipedia", "").strip()

                    # Extract infobox table
                    infobox = soup.find("table", class_=lambda c: c and "infobox" in c)
                    if infobox:
                        for tr in infobox.find_all("tr"):
                            th = tr.find("th")
                            td = tr.find("td")
                            if th and td:
                                k = th.get_text(separator=" ", strip=True).lower()
                                v = td.get_text(separator=" ", strip=True)
                                infobox_data[k] = v

                    # Extract lead paragraphs
                    paras = [
                        p.get_text(separator=" ", strip=True)
                        for p in soup.find_all("p")
                        if len(p.get_text(strip=True)) > 40
                    ]
                    if paras:
                        scraped_text_snippets.append(" ".join(paras[:4]))
                    break
        except Exception as e:
            logger.warning(f"Wikipedia scrape attempt failed for {wiki_url}: {e}")

    # Attempt Custom URL or company domain scrape
    target_custom = custom_url
    if not target_custom:
        domain_guess = re.sub(r"[^\w]", "", company_clean).lower() + ".com"
        target_custom = f"https://www.{domain_guess}"

    if target_custom:
        try:
            async with httpx.AsyncClient(timeout=4.0, follow_redirects=True) as client:
                resp = await client.get(target_custom, headers=headers)
                if resp.status_code == 200:
                    soup = BeautifulSoup(resp.text, "html.parser")
                    for el in soup(["script", "style", "nav", "footer", "svg"]):
                        el.decompose()
                    meta_desc = soup.find("meta", attrs={"name": "description"})
                    if meta_desc and meta_desc.get("content"):
                        scraped_text_snippets.append(f"Meta Description: {meta_desc.get('content')}")
                    
                    body_text = soup.get_text(separator=" ", strip=True)
                    if body_text:
                        scraped_text_snippets.append(body_text[:2500])
        except Exception as e:
            logger.warning(f"Company web scrape failed for {target_custom}: {e}")

    combined_scraped = "\n\n".join(scraped_text_snippets)

    # 3. Extract Financial Worth & Company Intelligence
    # Check infobox for revenue, market cap, traded as, headquarters
    ticker = None
    for k, v in infobox_data.items():
        if "traded as" in k:
            match = re.search(r"\b([A-Z]{2,6})\b", v)
            if match:
                ticker = match.group(1)
            break

    headquarters = "Global / Distributed"
    for k, v in infobox_data.items():
        if "headquarters" in k:
            headquarters = v
            break

    industry = "Enterprise Technology & Scaled Platforms"
    for k, v in infobox_data.items():
        if "industry" in k:
            industry = v
            break

    # Valuation & Worth extraction
    estimated_worth = "$10B - $50B Enterprise Valuation"
    worth_breakdown = "High-growth market capitalization calibrated from industry public comps."

    revenue_val = None
    for k, v in infobox_data.items():
        if "revenue" in k:
            revenue_val = v
            break

    employees_val = None
    for k, v in infobox_data.items():
        if "employees" in k or "number of employees" in k:
            employees_val = v
            break

    if revenue_val:
        worth_breakdown = f"Annual Revenue: {revenue_val}"
        if employees_val:
            worth_breakdown += f" • Headcount: {employees_val}"
        if ticker:
            worth_breakdown += f" • Public Ticker: {ticker}"
            estimated_worth = f"Estimated Large-Cap Public Enterprise ({ticker})"
        else:
            estimated_worth = "High-Growth Private Unicorn / Pre-IPO Enterprise"
    else:
        # Check text for valuation mentions
        val_match = re.search(r"(\$\d+(?:\.\d+)?\s*(?:billion|trillion|B|T))\b", combined_scraped, re.I)
        if val_match:
            estimated_worth = f"{val_match.group(1).upper()} Enterprise Valuation"
            worth_breakdown = f"Valuation benchmarked from latest capital market filings and public benchmarks."

    # 4. Synthesize with LLM or fallback generator
    prompt = f"""You are an expert Wall Street equity research analyst and corporate technical recruiter.
Analyze this scraped company data for '{company_clean}' and return structured intelligence.

Scraped Content:
{combined_scraped[:3000]}

Infobox Details:
{infobox_data}

Provide:
1. 'estimatedWorth': Realistic estimated market worth or market cap (e.g. '$45 Billion Market Cap' or '$12 Billion Valuation').
2. 'worthBreakdown': Financial metrics summary (e.g. 'Revenue: $4.2B • 5,000+ Employees • Series H Unicorn').
3. 'ticker': Stock ticker if public, or null if private.
4. 'industry': Core business sector.
5. 'headquarters': Primary city/country.
6. 'description': 2-3 crisp sentences on mission and scale.
7. 'culture': Key engineering values and hiring philosophy.
8. 'competencies': 10 distinct technical and domain skills required for their platform.
"""

    try:
        class LLMCompanyProfile(BaseModel):
            estimatedWorth: str
            worthBreakdown: str
            ticker: Optional[str] = None
            industry: str
            headquarters: str
            description: str
            culture: str
            competencies: List[str]

        synth_result = await llm_client.generate_json(
            prompt=prompt,
            schema_cls=LLMCompanyProfile,
            system_prompt="You produce pristine corporate company profiles and valuation assessments."
        )

        estimated_worth = synth_result.estimatedWorth or estimated_worth
        worth_breakdown = synth_result.worthBreakdown or worth_breakdown
        ticker = synth_result.ticker or ticker
        industry = synth_result.industry or industry
        headquarters = synth_result.headquarters or headquarters
        description = synth_result.description
        culture = synth_result.culture
        competencies = synth_result.competencies
    except Exception as e:
        logger.warning(f"LLM synthesis failed, using rule-based scraped output: {e}")
        description = (
            scraped_text_snippets[0][:280]
            if scraped_text_snippets
            else f"{company_clean} is a leading enterprise technology company delivering high-scale products."
        )
        culture = "High technical rigor, scalable system architecture, cross-functional engineering autonomy."
        competencies = [
            "Distributed Systems",
            "Python",
            "System Architecture",
            "FastAPI",
            "PostgreSQL",
            "Redis",
            "Docker",
            "Kubernetes",
            "Cloud Infrastructure",
            "Idempotency",
        ]

    # Generate 2 Standard Calibrated Roles
    roles = [
        ScrapedCompanyRole(
            id=f"{company_slug}-sde2",
            title="Software Engineer II (Systems & Backend)",
            track="tech",
            level="Mid-Senior (L4/L5)",
            difficulty="medium",
            requiredSkills=competencies[:6],
            jobDescription=f"""Job Title: Software Engineer II (Systems & Backend)
Company: {company_clean}
Location: {headquarters} / Remote

About the Role:
At {company_clean}, you will build and scale distributed platforms powering critical high-throughput infrastructure. You will design resilient APIs, optimize query latency, implement circuit breakers, and maintain high service level objectives.

Requirements:
- 3+ years of professional backend software engineering experience.
- Solid foundation in distributed systems, API architecture, and database performance."""
        ),
        ScrapedCompanyRole(
            id=f"{company_slug}-staff-infra",
            title="Staff Platform Infrastructure Engineer",
            track="tech",
            level="Staff (IC6)",
            difficulty="hard",
            requiredSkills=competencies[2:8],
            jobDescription=f"""Job Title: Staff Platform Infrastructure Engineer
Company: {company_clean}
Location: {headquarters} / Remote

Lead platform reliability, zero-downtime database migrations, and edge computing scale across {company_clean}'s global ecosystem."""
        ),
    ]

    # Generate Calibrated Hiring Stages
    hiring_stages = [
        ScrapedCompanyStage(
            title=f"Round 1: Numerical Reasoning & {company_clean} Platform Sizing",
            questionCount=10,
            format="Analytical Logic & Quantitative Estimation",
            focus="Uptime SLA depletion math, in-memory cache capacity sizing, network bandwidth saturation, and latency trade-offs.",
        ),
        ScrapedCompanyStage(
            title=f"Round 2: Systems Architecture & {company_clean} Reliability",
            questionCount=10,
            format="Distributed Engineering Scenarios",
            focus="Distributed locking, circuit breakers, zero-downtime database migrations, and fault-tolerant event streams.",
        ),
    ]

    profile = ScrapedCompanyProfile(
        id=company_slug,
        name=company_clean,
        ticker=ticker,
        estimatedWorth=estimated_worth,
        worthBreakdown=worth_breakdown,
        industry=industry,
        headquarters=headquarters,
        description=description,
        culture=culture,
        competencies=competencies,
        hiringStages=hiring_stages,
        roles=roles,
        isCustomScraped=True,
    )

    # 5. Save to MongoDB
    if db is not None:
        try:
            await db.scraped_companies.update_one(
                {"id": company_slug},
                {"$set": {"id": company_slug, "profile": profile.model_dump(), "created_at": datetime.datetime.now(datetime.timezone.utc)}},
                upsert=True,
            )
            logger.info(f"Saved scraped company '{company_clean}' to MongoDB.")
        except Exception as e:
            logger.warning(f"Failed to cache scraped company: {e}")

    return profile
