from playwright.sync_api import sync_playwright, expect
import time
import os
import requests
import sys

def verify_desktop_crud():
    print("Starting Desktop CRUD Verification")

    # Check backend
    try:
        r = requests.get("http://localhost:8000/health", timeout=2)
        print(f"Backend status: {r.status_code}")
    except Exception as e:
        print(f"Backend not reachable: {e}")
        pass

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page()

        # Capture console logs
        page.on("console", lambda msg: print(f"BROWSER CONSOLE: {msg.text}"))

        try:
            # 1. Load Shell
            print("Navigating to Shell...")
            page.goto("http://localhost:5173")

            # Wait for sidebar
            page.wait_for_selector(".sidebar", timeout=10000)

            # 2. Check initial state
            print("Checking initial state...")

            # Count initial desktops
            initial_count = page.locator(".desktop-btn").count()
            print(f"Initial desktop count: {initial_count}")

            # 3. Add Desktop
            print("Adding Desktop...")
            add_btn = page.locator(".add-btn")
            if add_btn.is_visible():
                add_btn.click()
            else:
                print("Add button not visible. Trying force click.")
                add_btn.click(force=True)

            # Wait for count to increase
            expect(page.locator(".desktop-btn")).to_have_count(initial_count + 1)
            print(f"Desktop added. Count: {initial_count + 1}")

            # 4. Switch Desktop
            print("Switching to last desktop...")
            desktops = page.locator(".desktop-btn")
            last_desktop = desktops.last
            last_desktop_text = last_desktop.inner_text().strip()
            print(f"Clicking {last_desktop_text}")
            last_desktop.click()

            # Verify active state in TopBar
            expect(page.locator(".topbar h3")).to_contain_text(last_desktop_text)
            print(f"Topbar verified: {last_desktop_text}")

            # 5. Reload to test persistence
            print("Reloading page...")
            page.reload()
            page.wait_for_selector(".sidebar", timeout=10000)

            # Verify count matches
            expect(page.locator(".desktop-btn")).to_have_count(initial_count + 1)
            print("Persistence verified. Count matches.")

            # 6. Delete Desktop
            # We delete the last desktop
            print("Deleting last desktop...")
            rows = page.locator(".desktop-row")
            last_row = rows.last
            # Hover to show button (for visual debug mainly, Playwright force click ignores visibility)
            last_row.hover()

            delete_btn = last_row.locator(".delete-btn")
            print("Clicking delete...")
            delete_btn.click(force=True)

            # Wait for count to decrease
            expect(page.locator(".desktop-btn")).to_have_count(initial_count)
            print(f"Desktop deleted. Count: {initial_count}")

            print("Verification Successful")

        except Exception as e:
            print(f"Verification Failed: {e}")
            page.screenshot(path="verification/error_screenshot.png")
            raise e
        finally:
            browser.close()

if __name__ == "__main__":
    verify_desktop_crud()
