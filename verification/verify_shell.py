from playwright.sync_api import sync_playwright
import time
import os

def verify_shell():
    print(f"Current working directory: {os.getcwd()}")
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()
        try:
            page.goto("http://localhost:5173")
            print("Navigated to localhost:5173")
            # Wait for skeleton to be visible
            page.wait_for_selector("#skeleton-demo .skeleton", timeout=5000)
            # Wait a bit for animation or rendering
            time.sleep(1)
            # Take screenshot
            output_path = "/app/verification/shell_screenshot.png"
            page.screenshot(path=output_path)
            print(f"Screenshot taken at {output_path}")
        except Exception as e:
            print(f"Error: {e}")
            page.screenshot(path="/app/verification/error_screenshot.png")
            print("Error screenshot taken at /app/verification/error_screenshot.png")
        finally:
            browser.close()

if __name__ == "__main__":
    verify_shell()
