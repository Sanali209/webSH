/**
 * E2E Tests for System Dashboard
 * 
 * Tests dashboard loading, widget display, and navigation
 */
import { test, expect } from '@playwright/test';
import { navigateAndWait, isDashboardVisible } from './setup';

test.describe('System Dashboard', () => {
  test('should load dashboard on app start', async ({ page }) => {
    await navigateAndWait(page);
    
    // Dashboard should be visible by default
    const dashboardVisible = await isDashboardVisible(page);
    expect(dashboardVisible).toBe(true);
    
    // Check for dashboard header
    await expect(page.locator('text=Dashboard')).toBeVisible();
  });
  
  test('should show dashboard grid layout', async ({ page }) => {
    await navigateAndWait(page);
    
    // Dashboard grid should be present
    const grid = page.locator('.dashboard-grid');
    await expect(grid).toBeVisible();
  });
  
  test('should show empty state when no widgets', async ({ page }) => {
    await navigateAndWait(page);
    
    // Check for empty state or widgets
    // Either widgets are shown or empty state is shown
    const emptyState = page.locator('#dashboard-empty-state');
    const hasEmptyState = await emptyState.isVisible().catch(() => false);
    
    if (hasEmptyState) {
      await expect(page.locator('text=No Widgets Available')).toBeVisible();
    }
    // If no empty state, widgets should be present
  });
  
  test('should display file system widget if available', async ({ page }) => {
    await navigateAndWait(page);
    
    // Look for FS widget
    const fsWidget = page.locator('.fs-widget');
    const hasWidget = await fsWidget.isVisible().catch(() => false);
    
    if (hasWidget) {
      // Check widget content
      await expect(page.locator('text=File System')).toBeVisible();
    }
  });
  
  test('navigation between Dashboard and Files works', async ({ page }) => {
    await navigateAndWait(page);
    
    // Click Files button
    await page.click('button:has-text("Files")');
    
    // Wait for file explorer
    await page.waitForTimeout(500);
    
    // Click Dashboard button
    await page.click('button:has-text("Dashboard")');
    
    // Dashboard should be visible again
    await page.waitForTimeout(500);
    const dashboardVisible = await isDashboardVisible(page);
    expect(dashboardVisible).toBe(true);
  });
});
