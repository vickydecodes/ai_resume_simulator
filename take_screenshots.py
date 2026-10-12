import os
import time
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:5173"
SCREENSHOT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "screenshots")
os.makedirs(SCREENSHOT_DIR, exist_ok=True)

def run():
    print(f"Saving screenshots to: {SCREENSHOT_DIR}")
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 850})
        page = context.new_page()

        # 1. Login Page
        print("1. Capturing Login Page...")
        page.goto(f"{BASE_URL}/login")
        page.wait_for_selector("text=Welcome to HireFit", timeout=10000)
        time.sleep(1)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "01_login_page.png"), full_page=True)

        # 2. Target Companies Directory (Home)
        print("2. Capturing Target Companies Directory (Home)...")
        page.goto(f"{BASE_URL}/")
        page.wait_for_selector("text=Benchmark Your Candidacy Against Top Companies", timeout=10000)
        time.sleep(1)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "02_companies_directory.png"), full_page=True)

        # 3. Candidate Profile & Multi-Resume Portfolio
        print("3. Capturing Profile & Resumes...")
        page.goto(f"{BASE_URL}/profile")
        page.wait_for_selector("text=Multi-Resume Portfolio", timeout=10000)
        time.sleep(1)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "03_candidate_profile_resumes.png"), full_page=True)

        # 4. Company Detail - Google SDE-2
        print("4. Capturing Google Company Rubric & Readiness...")
        page.goto(f"{BASE_URL}/company/google")
        page.wait_for_selector("text=Google", timeout=10000)
        time.sleep(1)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "04_company_google_rubric.png"), full_page=True)

        # 5. Company Detail - Stripe
        print("5. Capturing Stripe Company Rubric...")
        page.goto(f"{BASE_URL}/company/stripe")
        page.wait_for_selector("text=Stripe", timeout=10000)
        time.sleep(1)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "05_company_stripe_rubric.png"), full_page=True)

        # 6. Start Simulation Test from Company Page
        print("6. Launching simulation test from Google rubric...")
        page.goto(f"{BASE_URL}/company/google")
        page.wait_for_selector("text=Attend Interview / Start 20-Question Test", timeout=10000)
        # Click start test button
        page.click("text=Attend Interview / Start 20-Question Test")
        
        # Wait for navigation to /interview/
        print("Waiting for interview simulation engine...")
        page.wait_for_url("**/interview/**", timeout=25000)
        page.wait_for_selector("text=Round 1:", timeout=15000)
        time.sleep(1.5)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "06_interview_simulation.png"), full_page=True)

        # Answer question 1 and flag it to show active test state
        try:
            # Select first option
            options = page.query_selector_all("text=Option")
            if options:
                options[0].click()
                time.sleep(0.5)
            # Take screenshot with selected answer
            page.screenshot(path=os.path.join(SCREENSHOT_DIR, "07_interview_question_answered.png"), full_page=True)
        except Exception as e:
            print(f"Note on options: {e}")

        # 7. Past Scorecards modal
        print("8. Capturing Past Scorecards dialog...")
        page.goto(f"{BASE_URL}/")
        page.wait_for_selector("text=Past Scorecards", timeout=10000)
        page.click("text=Past Scorecards")
        time.sleep(1)
        page.screenshot(path=os.path.join(SCREENSHOT_DIR, "08_past_scorecards_modal.png"))

        browser.close()
        print("All screenshots successfully captured!")

if __name__ == "__main__":
    run()
