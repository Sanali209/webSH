import { test, expect } from '@playwright/test';
import { readFileSync } from 'fs';
import { resolve } from 'path';

test.describe('Widget Isolation', () => {
  test('should load a widget and communicate via penpal', async ({ page }) => {
    // Read penpal source to inject
    // Assuming the test file is at shell/tests/e2e/widget_isolation.spec.ts
    // node_modules is at shell/node_modules
    const penpalPath = resolve(process.cwd(), 'node_modules/penpal/dist/penpal.min.js');
    console.log('Reading penpal from:', penpalPath);
    const penpalSource = readFileSync(penpalPath, 'utf-8');

    // 1. Mock the widget HTML
    await page.route('**/test_widget.html', async route => {
      await route.fulfill({
        status: 200,
        contentType: 'text/html',
        body: `
          <html>
            <body>
              <script>${penpalSource}</script>
              <script>
                const connection = window.Penpal.connect({
                    messenger: new window.Penpal.WindowMessenger({
                        remoteWindow: window.parent,
                        allowedOrigins: ['*'],
                    })
                });
                connection.promise.then(parent => {
                  parent.getApiToken().then(token => {
                    const div = document.createElement('div');
                    div.id = 'token';
                    div.textContent = token;
                    document.body.appendChild(div);
                  });
                });
              </script>
            </body>
          </html>
        `
      });
    });

    page.on('request', request => console.log('>>', request.method(), request.url()));

    // Mock plugins API
    await page.route((url) => url.pathname.includes('/api/v1/plugins'), async route => {
        await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify([])
        });
    });

    // 2. Mock the desktop state to include the widget
    await page.route((url) => url.pathname.includes('/api/v1/desktop/sync'), async route => {
      if (route.request().method() === 'GET') {
          await route.fulfill({
            status: 200,
            contentType: 'application/json',
            body: JSON.stringify([
                {
                    id: 'default',
                    widgets: [
                        {
                            id: 'test-widget',
                            x: 0,
                            y: 0,
                            w: 2,
                            h: 2,
                            type: 'widget',
                            label: 'Test Widget',
                            component: '/test_widget.html',
                            props: '{}'
                        }
                    ]
                }
            ])
          });
      } else {
          // If we continue, it will fail because backend is not running.
          // We should probably fulfill POST as well to avoid errors.
          await route.fulfill({ status: 200 });
      }
    });

    // 3. Navigate to the app
    await page.goto('/');

    // 4. Verify that the widget loaded and token is displayed
    // Switch to the iframe
    const iframe = page.frameLocator('iframe[title="Widget"]');
    await expect(iframe.locator('#token')).toHaveText('mock-api-token', { timeout: 10000 });

    await page.screenshot({ path: 'test-results/widget_isolation.png' });
  });
});
