/**
 * E2E Tests for Application Core
 * 
 * Tests basic app functionality and navigation
 */
import { test, expect } from '@playwright/test';
import { navigateAndWait } from './setup';

test.describe('Application Core', () => {
  test('app loads successfully', async ({ page }) => {
    await navigateAndWait(page);
    
    // Check for main header
    await expect(page.locator('h1:has-text("PC Center")')).toBeVisible();
    
    // Check that main content area exists
    await expect(page.locator('main')).toBeVisible();
  });
  
  test('navigation buttons are present', async ({ page }) => {
    await navigateAndWait(page);
    
    // Check for navigation buttons
    await expect(page.locator('button:has-text("Dashboard")')).toBeVisible();
    await expect(page.locator('button:has-text("Files")')).toBeVisible();
  });
  
  test('can navigate to Files view', async ({ page }) => {
    await navigateAndWait(page);
    
    // Click Files button
    await page.click('button:has-text("Files")');
    
    // Wait for content to load
    await page.waitForTimeout(1000);
    
    // Files button should be highlighted
    const filesButton = page.locator('button:has-text("Files")');
    const buttonClass = await filesButton.getAttribute('class');
    expect(buttonClass).toContain('variant-filled-primary');
  });
  
  test('can navigate back to Dashboard', async ({ page }) => {
    await navigateAndWait(page);
    
    // Go to Files
    await page.click('button:has-text("Files")');
    await page.waitForTimeout(500);
    
    // Go back to Dashboard
    await page.click('button:has-text("Dashboard")');
    await page.waitForTimeout(500);
    
    // Dashboard button should be highlighted
    const dashboardButton = page.locator('button:has-text("Dashboard")');
    const buttonClass = await dashboardButton.getAttribute('class');
    expect(buttonClass).toContain('variant-filled-primary');
  });
  
  test('status API endpoint returns OK', async ({ page }) => {
    const response = await page.request.get('/api/status');
    expect(response.ok()).toBe(true);
    
    const data = await response.json();
    expect(data.status).toBe('ok');
  });
});
