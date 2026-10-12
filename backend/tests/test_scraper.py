import pytest
from app.services.company_scraper import scrape_company_intelligence

@pytest.mark.asyncio
async def test_company_scraper_fallback():
    # Test fallback scraping for hypothetical company name
    res = await scrape_company_intelligence("Acme Cloud Systems")
    assert res is not None
    assert res.company_name == "Acme Cloud Systems"
    assert isinstance(res.products, list)
    assert isinstance(res.tech_stack, list)

@pytest.mark.asyncio
async def test_scrape_and_generate_company_profile():
    from app.services.company_scraper import scrape_and_generate_company_profile
    profile = await scrape_and_generate_company_profile("Netflix")
    assert profile is not None
    assert profile.name == "Netflix"
    assert profile.estimatedWorth != ""
    assert profile.worthBreakdown != ""
    assert len(profile.competencies) > 0
    assert len(profile.roles) >= 1
    assert len(profile.hiringStages) == 2
