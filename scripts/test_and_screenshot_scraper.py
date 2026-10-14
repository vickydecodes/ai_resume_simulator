import os
import time
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:5173"
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCREENSHOT_DIR = os.path.join(ROOT_DIR, "screenshots")

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 850})
        page = context.new_page()

        # 1. Open Home page
        print("Navigating to Home...")
        page.goto(f"{BASE_URL}/")
        page.wait_for_selector("text=Benchmark Your Candidacy Against Top Companies", timeout=10000)

        # 2. Click Scrape & Add Any Company button
        print("Opening Scrape Modal...")
        page.click("button:has-text('Scrape & Add Any Company')")
        page.wait_for_selector("text=Scrape & Load Any Target Company", timeout=5000)
        time.sleep(0.5)

        # Take screenshot of the Scrape modal
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "11_scrape_company_modal.png"))
        print("Captured 11_scrape_company_modal.png")

        # 3. Enter Netflix and submit
        print("Entering Netflix into scraper...")
        page.fill("input[placeholder*='Netflix']", "Netflix")
        time.sleep(0.5)
        page.click("button:has-text('Scrape Profile & Calculate Worth')")

        # Wait for navigation to /company/netflix
        print("Waiting for BeautifulSoup scraping & navigation to /company/netflix...")
        page.wait_for_url("**/company/netflix**", timeout=45000)
        page.wait_for_selector("text=Netflix", timeout=15000)
        time.sleep(2)

        # Take screenshot of the newly scraped company profile with Enterprise Worth
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "12_scraped_company_netflix_worth.png"), full_page=True)
        print("Captured 12_scraped_company_netflix_worth.png")

        # 4. Return to home to see Netflix in the directory with its valuation badge
        page.goto(f"{BASE_URL}/")
        page.wait_for_selector("text=Netflix", timeout=10000)
        time.sleep(1)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "13_companies_directory_with_netflix.png"), full_page=True)
        print("Captured 13_companies_directory_with_netflix.png")

        browser.close()
        print("Scraper test and screenshots complete!")

if __name__ == "__main__":
    run()
