import { test, expect } from '@playwright/test';

test.describe('Desktop Grid', () => {
    test('renders grid and widgets', async ({ page }) => {
        await page.goto('/');

        // Check if grid exists
        const grid = page.locator('.grid-container');
        await expect(grid).toBeVisible();

        // Check for items
        const items = page.locator('.grid-item-wrapper');
        await expect(items).toHaveCount(2);

        // Check content
        await expect(items.first()).toContainText('Test Icon');
        await expect(items.nth(1)).toContainText('Test Widget');
    });

    test('can drag and reorder items', async ({ page }) => {
        await page.goto('/');

        // Need to wait for svelte-dnd-action to initialize
        await page.waitForTimeout(1000);

        const items = page.locator('.grid-item-wrapper');
        const firstItem = items.first();
        const secondItem = items.nth(1);

        const firstBox = await firstItem.boundingBox();
        const secondBox = await secondItem.boundingBox();

        if (firstBox && secondBox) {
            // Drag first item to the position of the second item (and a bit further)
            // Note: svelte-dnd-action requires move events to trigger reordering

            await page.mouse.move(firstBox.x + firstBox.width / 2, firstBox.y + firstBox.height / 2);
            await page.mouse.down();

            // Move slowly
            await page.mouse.move(secondBox.x + secondBox.width / 2, secondBox.y + secondBox.height / 2, { steps: 20 });

            // Move a bit more to ensure swap
            await page.mouse.move(secondBox.x + secondBox.width + 20, secondBox.y + secondBox.height / 2, { steps: 10 });

            await page.mouse.up();

            // Wait for reordering
            await page.waitForTimeout(1000);

            // Verify order changed
            // The first element in DOM should now be the widget
            await expect(items.first()).toContainText('Test Widget');
            await expect(items.nth(1)).toContainText('Test Icon');
        }
    });
});
