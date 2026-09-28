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
from app.models.schemas import CompanyInfoResult
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
