/**
 * E2E Test Setup Utilities
 * 
 * Common utilities and helpers for E2E tests
 */

export const TEST_CONFIG = {
  baseURL: 'http://localhost:8000',
  timeout: 30000,
};

/**
 * Wait for the app to be initialized
 */
export async function waitForAppInit(page: any) {
  // Wait for ModuleLoader to initialize
  await page.waitForSelector('main', { timeout: 10000 });
  // Wait a bit for plugins to load
  await page.waitForTimeout(1000);
}

/**
 * Navigate and wait for page to be ready
 */
export async function navigateAndWait(page: any, path: string = '/') {
  await page.goto(path);
  await waitForAppInit(page);
}

/**
 * Check if dashboard is visible
 */
export async function isDashboardVisible(page: any) {
  try {
    await page.waitForSelector('.dashboard-container', { timeout: 5000 });
    return true;
  } catch {
    return false;
  }
}

/**
 * Check if file explorer is visible
 */
export async function isFileExplorerVisible(page: any) {
  try {
    await page.waitForSelector('[data-testid="file-explorer"], .dashboard-grid', { timeout: 5000 });
    return true;
  } catch {
    return false;
  }
}
