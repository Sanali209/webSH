import { test, expect } from '@playwright/test';

test('App loads and shows skeleton', async ({ page }) => {
  await page.goto('/');

  // Check if skeleton demo is present
  const skeleton = page.locator('#skeleton-demo .skeleton');
  await expect(skeleton).toBeVisible();

  // Check if skeleton parts animate (basic visibility check)
  const header = skeleton.locator('.header');
  await expect(header).toBeVisible();

  const content = skeleton.locator('.content');
  await expect(content).toBeVisible();
});
