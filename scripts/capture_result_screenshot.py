import os
import time
from playwright.sync_api import sync_playwright

BASE_URL = "http://127.0.0.1:5173"
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SCREENSHOT_DIR = os.path.join(ROOT_DIR, "screenshots")

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1366, "height": 900})
        page = context.new_page()

        # Handle any browser confirmation dialogs automatically
        page.on("dialog", lambda dialog: dialog.accept())

        print("Navigating to Google rubric to launch test...")
        page.goto(f"{BASE_URL}/company/google")
        page.wait_for_selector("text=Attend Interview / Start 20-Question Test")
        page.click("text=Attend Interview / Start 20-Question Test")
        
        page.wait_for_url("**/interview/**", timeout=25000)
        page.wait_for_selector("text=Round 1:", timeout=15000)
        time.sleep(1)

        # Answer the first question
        print("Selecting option for Question 1...")
        buttons = page.query_selector_all("button")
        for b in buttons:
            txt = b.inner_text()
            if "Option A" in txt or "A)" in txt or "A." in txt or ("A" in txt and len(txt) > 20):
                b.click()
                break
        time.sleep(1)

        # Click submit button
        print("Submitting Final Interview...")
        page.click("button:has-text('Submit Final Interview')")

        print("Waiting for evaluation and navigation to scorecard...")
        page.wait_for_url("**/result/**", timeout=45000)
        page.wait_for_selector("text=Interview Performance", timeout=30000)
        time.sleep(2)

        result_path = os.path.join(SCREENSHOT_DIR, "09_result_scorecard.png")
        page.screenshot(path=result_path, full_page=True)
        print(f"Captured scorecard successfully at: {result_path}")

        # Also capture question review tab on Result page
        try:
            review_tab = page.query_selector("button:has-text('Detailed Question Review')") or page.query_selector("text=Question Review")
            if review_tab:
                review_tab.click()
                time.sleep(1)
                page.screenshot(path=os.path.join(SCREENSHOT_DIR, "10_result_question_review.png"), full_page=True)
                print("Captured detailed question review tab!")
        except Exception as e:
            print(f"Review tab note: {e}")

        browser.close()

if __name__ == "__main__":
    run()
