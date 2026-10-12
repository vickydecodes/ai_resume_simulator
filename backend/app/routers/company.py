import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, Query
from app.models.schemas import ScrapeCompanyRequest, ScrapedCompanyProfile
from app.services.company_scraper import scrape_and_generate_company_profile
from app.core.db import get_database

logger = logging.getLogger("uvicorn.error")
router = APIRouter(prefix="/companies", tags=["Companies"])

# In-memory backup store for custom scraped companies
in_memory_scraped_companies: dict[str, dict] = {}

@router.post("/scrape", response_model=ScrapedCompanyProfile)
async def scrape_company_endpoint(payload: ScrapeCompanyRequest):
    """Scrape company public profile, financial valuation / worth, and generate an enterprise hiring rubric."""
    company_name = payload.company_name.strip()
    if not company_name:
        raise HTTPException(status_code=400, detail="Company name is required.")

    try:
        profile = await scrape_and_generate_company_profile(
            company_name=company_name,
            custom_url=payload.website_url
        )
        in_memory_scraped_companies[profile.id] = profile.model_dump()
        return profile
    except Exception as e:
        logger.error(f"Failed to scrape company profile for '{company_name}': {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to scrape and synthesize company profile: {str(e)}"
        )

@router.get("/custom", response_model=List[ScrapedCompanyProfile])
async def list_custom_companies():
    """Retrieve all custom scraped companies."""
    db = get_database()
    results = []

    if db is not None:
        try:
            cursor = db.scraped_companies.find({}).sort("created_at", -1)
            async for doc in cursor:
                if "profile" in doc:
                    results.append(ScrapedCompanyProfile(**doc["profile"]))
        except Exception as e:
            logger.warning(f"Error fetching custom companies from MongoDB: {e}")

    # Fallback to in-memory if MongoDB empty or unavailable
    if not results and in_memory_scraped_companies:
        for p in in_memory_scraped_companies.values():
            results.append(ScrapedCompanyProfile(**p))

    return results
