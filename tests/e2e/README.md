# E2E Tests - Playwright

End-to-end tests for PC Center using Playwright for browser automation.

## Overview

These tests verify the application works correctly from a user's perspective by:
- Testing the UI in a real browser
- Verifying plugin loading and APIs
- Testing navigation and interactions
- Checking dashboard and file explorer functionality

## Test Structure

```
tests/e2e/
├── setup.ts            # Test utilities and helpers
├── app.spec.ts         # Core application tests
├── dashboard.spec.ts   # Dashboard functionality tests
└── plugins.spec.ts     # Plugin loading and API tests
```

## Test Coverage

### Application Core (`app.spec.ts`)
- ✅ App loads successfully
- ✅ Navigation buttons are present
- ✅ Can navigate between views
- ✅ Status API works

### Dashboard (`dashboard.spec.ts`)
- ✅ Dashboard loads on app start
- ✅ Dashboard grid layout displays
- ✅ Empty state shown when no widgets
- ✅ File system widget displays (if available)
- ✅ Navigation between Dashboard and Files works

### Plugins (`plugins.spec.ts`)
- ✅ Plugins load on startup
- ✅ `/api/plugins` returns active plugins
- ✅ System LLM plugin API works
- ✅ System LLM embed endpoint works
- ✅ System Dashboard config endpoint works

## Running Tests

### Prerequisites

1. Install dependencies:
   ```bash
   npm install
   ```

2. Install Playwright browsers:
   ```bash
   npx playwright install chromium
   ```

3. Build the frontend:
   ```bash
   npm run build
   ```

4. Start the backend server:
   ```bash
   cd ..
   poetry run uvicorn core.main:app --host 0.0.0.0 --port 8000
   ```

### Run Tests

```bash
# Run all tests
npx playwright test

# Run specific test file
npx playwright test tests/e2e/dashboard.spec.ts

# Run with UI mode (interactive)
npx playwright test --ui

# Run in headed mode (see browser)
npx playwright test --headed

# Generate HTML report
npx playwright show-report
```

### Debug Tests

```bash
# Debug mode
npx playwright test --debug

# Trace viewer
npx playwright show-trace trace.zip
```

## Configuration

Tests are configured in `playwright.config.ts`:

- **Base URL:** `http://localhost:8000`
- **Timeout:** 30 seconds per test
- **Browser:** Chromium (can add Firefox, WebKit)
- **Screenshots:** On failure
- **Traces:** On first retry

## Test Utilities

### `setup.ts` Helpers

```typescript
// Navigate and wait for app to initialize
await navigateAndWait(page);

// Check if dashboard is visible
const visible = await isDashboardVisible(page);

// Check if file explorer is visible
const visible = await isFileExplorerVisible(page);
```

## CI/CD Integration

Add to GitHub Actions workflow:

```yaml
- name: Install Playwright
  run: npx playwright install chromium

- name: Run E2E Tests
  run: npx playwright test
  
- name: Upload test results
  if: always()
  uses: actions/upload-artifact@v3
  with:
    name: playwright-report
    path: playwright-report/
```

## Writing New Tests

### Basic Test Structure

```typescript
import { test, expect } from '@playwright/test';
import { navigateAndWait } from './setup';

test.describe('My Feature', () => {
  test('should do something', async ({ page }) => {
    await navigateAndWait(page);
    
    // Your test code here
    await expect(page.locator('selector')).toBeVisible();
  });
});
```

### Best Practices

1. **Use data-testid attributes** for reliable selectors
2. **Wait for elements** before interacting
3. **Use page.request** for API testing
4. **Group related tests** with describe blocks
5. **Clean up** after each test if needed

### Common Patterns

```typescript
// Click and wait
await page.click('button');
await page.waitForTimeout(500);

// Check visibility with fallback
const isVisible = await element.isVisible().catch(() => false);

// API testing
const response = await page.request.get('/api/endpoint');
expect(response.ok()).toBe(true);
const data = await response.json();
```

## Troubleshooting

### Server Not Running
Make sure both backend and frontend are accessible:
```bash
curl http://localhost:8000/api/status
```

### Timeouts
Increase timeout in test or config:
```typescript
test('slow test', async ({ page }) => {
  test.setTimeout(60000); // 60 seconds
  // ...
});
```

### Flaky Tests
- Add explicit waits: `await page.waitForSelector()`
- Use `waitForLoadState`: `await page.waitForLoadState('networkidle')`
- Increase retries in config

### Browser Issues
Reinstall browsers:
```bash
npx playwright install --force chromium
```

## Test Results

Tests can be viewed in:
- Terminal output (default)
- HTML report: `playwright-report/index.html`
- Trace viewer for debugging

## Future Enhancements

- [ ] Add tests for file upload/download
- [ ] Test WebSocket events
- [ ] Test plugin hot-reloading
- [ ] Add visual regression tests
- [ ] Test mobile responsiveness
- [ ] Add performance metrics

## Resources

- [Playwright Documentation](https://playwright.dev)
- [Best Practices](https://playwright.dev/docs/best-practices)
- [Debugging Guide](https://playwright.dev/docs/debug)
