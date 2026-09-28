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
