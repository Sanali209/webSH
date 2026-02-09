# Phase 3: System Plugins Implementation - Detailed Task Descriptions

This document provides a comprehensive overview of all Phase 3 tasks based on the detailed instructions in `tasks/phase3_system_plugins/`.

## Overview

Phase 3 focuses on implementing the core system plugins that bring the PC Center application to life. These plugins demonstrate the power of the plugin architecture built in Phases 1 and 2.

### Current Status: 40% Complete (2 of 5 tasks done)

- ✅ **01_system_fs** - File System Plugin
- ⏳ **02_system_llm** - LLM Provider Plugin
- ✅ **03_frontend_core_integration** - ModuleLoader & SlotManager  
- ⏳ **04_e2e_tests** - End-to-End Testing
- ⏳ **05_system_dashboard** - Main Dashboard UI

---

## ✅ Task 01: System File System Plugin (COMPLETE)

**Location:** `tasks/phase3_system_plugins/01_system_fs/INSTRUCTIONS.md`

### Goal
Implement the file system browser and synchronization logic as a system plugin.

### What Was Implemented

#### 1. Plugin Structure ✅
- **Location:** `plugins/system_fs/`
- **Files:**
  - `manifest.json` - Plugin metadata with capabilities: `["fs.scan", "fs.watch", "opener:directory"]`
  - `backend.py` - File system operations and watchdog integration
  - `config.py` - Plugin configuration
  - `ui/index.js` - UI module entry point

#### 2. Backend Implementation ✅
- **File Watching:** Uses `watchdog` library to monitor file system changes
- **File Operations:**
  - `on_load()` - Starts file watcher on configured path
  - `/scan` endpoint - Lists directory contents with metadata
  - File event handlers for create/modify/delete/move operations

#### 3. CoreTable Synchronization ✅
- **On Create/Modify:**
  - Calculates file hash (SHA256)
  - Extracts metadata (size, mime_type, filename)
  - Updates LanceDB Core Metadata Table
- **On Delete:**
  - Removes entry from Core Metadata Table
- **On Move:**
  - Deletes old entry, creates new entry

#### 4. Frontend Component ✅
- **Location:** `web/src/lib/components/system_fs/FileExplorer.svelte`
- **Features:**
  - Grid and List view toggle
  - Directory navigation with breadcrumbs
  - File size and modification time display
  - Context menu slot for extensibility
  - Error handling and loading states

#### 5. Testing ✅
- **Location:** `tests/plugins/test_system_fs.py`
- Tests for scanning, watching, and sync operations

---

## ⏳ Task 02: System LLM Provider Plugin (PENDING)

**Location:** `tasks/phase3_system_plugins/02_system_llm/INSTRUCTIONS.md`

### Goal
Provide LLM capabilities (embeddings, generation) to other plugins through the capability system.

### Required Implementation

#### 1. Plugin Structure
Create `plugins/system_llm/` with:
- **manifest.json**
  ```json
  {
    "id": "system_llm",
    "name": "LLM Provider",
    "capabilities": ["llm.embed", "llm.generate"],
    "type": "system"
  }
  ```
- **backend.py** - Main plugin logic
- **config.py** - Configuration (model selection, API keys, etc.)

#### 2. LLM Integration
Initialize connection to local LLM:
- **Option A:** Ollama (recommended for local deployment)
  - Lightweight, easy to set up
  - Supports multiple models
  - REST API interface
- **Option B:** HuggingFace Transformers
  - More control over models
  - Requires more setup
  - Local inference

#### 3. EmbeddingsService Implementation
```python
class EmbeddingsService:
    def embed_text(self, text: str) -> list[float]:
        """
        Generate text embeddings.
        Returns: List of floats (typically 384-768 dimensions)
        """
        pass
    
    def embed_image(self, path: str) -> list[float]:
        """
        Generate image embeddings (optional).
        Uses CLIP or similar vision-language model.
        """
        pass
```

#### 4. Capability Exposure
Expose services via Core SDK:
```python
class SystemLLMPlugin(PluginBase):
    def on_load(self, context: PluginContext):
        self.embeddings = EmbeddingsService()
        # Register capabilities
        context.capabilities.register("llm.embed", self.embeddings.embed_text)
        context.capabilities.register("llm.generate", self.generate_text)
```

#### 5. Testing
**Location:** `tests/plugins/test_system_llm.py`
- **Unit Tests:**
  - Mock LLM provider responses
  - Test `embed_text()` returns correct dimension
  - Test `embed_image()` if implemented
- **Integration Tests:**
  - Verify another plugin can access the capability
  - Test capability registration and discovery

### Use Cases
Once implemented, other plugins can use embeddings:
- **Web Parser Plugin** - Generate embeddings for web pages
- **File System Plugin** - Semantic search over file content
- **Deduplicator Plugin** - Find semantically similar content

### Estimated Effort
**4-6 hours** (Medium complexity)

---

## ✅ Task 03: Frontend Core Integration (COMPLETE)

**Location:** `tasks/phase3_system_plugins/03_frontend_core_integration/INSTRUCTIONS.md`

### Goal
Enable dynamic loading of plugin UI components.

### What Was Implemented

#### 1. ModuleLoader ✅
- **Location:** `web/src/lib/core/module_loader.ts`
- **Functionality:**
  - Fetches active plugins from `/api/plugins`
  - Dynamically imports plugin UI from `/plugins/{plugin_id}/ui/index.js`
  - Manages plugin lifecycle (init, reload)
  - Provides singleton access to loaded plugins

#### 2. SlotManager ✅
- **Location:** `web/src/lib/core/SlotManager.svelte`
- **Functionality:**
  - Renders plugin components in named slots
  - Supports: `system_tray`, `context_menu`, custom slots
  - Passes context data to components
  - Handles loading and error states

#### 3. Integration ✅
- **App.svelte** updated to use ModuleLoader
- **Backend** serves plugin UI files at `/plugins`
- **Example** plugin UI structure in `plugins/system_fs/ui/index.js`

#### 4. Documentation ✅
- **Location:** `docs/frontend_core_integration.md`
- Complete API reference and usage examples

---

## ⏳ Task 04: End-to-End Tests (PENDING)

**Location:** `tasks/phase3_system_plugins/04_e2e_tests/INSTRUCTIONS.md`

### Goal
Verify the system works as a whole from the user's perspective using Playwright.

### Required Implementation

#### 1. Playwright Setup
- **File:** `playwright.config.ts` (in project root)
- **Configuration:**
  ```typescript
  export default defineConfig({
    testDir: './tests/e2e',
    webServer: {
      command: 'npm run dev',
      port: 5173,
      reuseExistingServer: !process.env.CI,
    },
    use: {
      baseURL: 'http://localhost:5173',
    },
  });
  ```
- **Backend Server:** Configure to run FastAPI in test mode

#### 2. Test Scenarios

##### System FS Tests
**File:** `tests/e2e/system_fs.spec.ts`
```typescript
test('file explorer loads and displays files', async ({ page }) => {
  // Open App
  await page.goto('/');
  
  // Check System FS icon in system tray
  await expect(page.locator('[data-plugin-id="system_fs"]')).toBeVisible();
  
  // Open File Explorer
  await page.click('[data-plugin-id="system_fs"]');
  await expect(page.locator('text=File Explorer')).toBeVisible();
  
  // Verify files are listed
  await expect(page.locator('.file-item')).toHaveCount(greaterThan(0));
});

test('file changes are reflected in UI', async ({ page, context }) => {
  await page.goto('/');
  
  // Create a test file in watched directory (via backend)
  // Verify it appears in the UI (via WebSocket or polling)
  await expect(page.locator('text=test-file.txt')).toBeVisible();
});
```

##### Dashboard Tests
**File:** `tests/e2e/dashboard.spec.ts`
```typescript
test('dashboard renders with widgets', async ({ page }) => {
  await page.goto('/');
  
  // Verify dashboard is the default view
  await expect(page.locator('[data-plugin-id="system_dashboard"]')).toBeVisible();
  
  // Verify widgets from plugins appear
  await expect(page.locator('.dashboard-widget')).toHaveCount(greaterThan(0));
});
```

##### Settings & Theme Tests
**File:** `tests/e2e/settings.spec.ts`
```typescript
test('theme toggle works', async ({ page }) => {
  await page.goto('/');
  
  // Toggle to dark mode
  await page.click('[data-testid="theme-toggle"]');
  await expect(page.locator('html')).toHaveClass(/dark/);
  
  // Verify persistence after reload
  await page.reload();
  await expect(page.locator('html')).toHaveClass(/dark/);
});
```

#### 3. Test Execution
```bash
# Install Playwright
npm install -D @playwright/test

# Install browsers
npx playwright install

# Run tests
npx playwright test

# Run with UI
npx playwright test --ui

# Run specific test
npx playwright test tests/e2e/system_fs.spec.ts
```

#### 4. CI Integration
Add to `.github/workflows/test.yml`:
```yaml
- name: Run E2E tests
  run: npx playwright test
```

### Dependencies
- Requires dashboard implementation for full test coverage
- Can implement basic tests now, add dashboard tests later

### Estimated Effort
**3-5 hours** (Medium complexity)

---

## ⏳ Task 05: System Dashboard (PENDING)

**Location:** `tasks/phase3_system_plugins/05_system_dashboard/INSTRUCTIONS.md`

### Goal
Implement the main dashboard interface that hosts widgets from other plugins.

### Required Implementation

#### 1. Plugin Structure
Create `plugins/system_dashboard/`:
- **manifest.json**
  ```json
  {
    "id": "system_dashboard",
    "name": "System Dashboard",
    "type": "system",
    "capabilities": ["ui.dashboard"],
    "default_view": true
  }
  ```
- **backend.py** - Minimal backend (mainly serves UI assets)
- **ui/** directory with:
  - `index.js` - Plugin UI entry point
  - `MainView.svelte` - Main dashboard component
  - `WidgetHost.svelte` - Widget container component

#### 2. Dashboard Layout (Frontend)
**File:** `plugins/system_dashboard/ui/MainView.svelte`

```svelte
<script lang="ts">
  import { SlotManager } from '$lib/core/SlotManager.svelte';
  
  // Grid layout configuration
  let gridLayout = {
    columns: 12,
    rowHeight: 60,
    gap: 16
  };
</script>

<div class="dashboard-container">
  <div class="dashboard-grid" style="grid-template-columns: repeat(12, 1fr)">
    <SlotManager 
      slotName="dashboard_widget" 
      context={{ layout: gridLayout }} 
    />
  </div>
</div>

<style>
  .dashboard-grid {
    display: grid;
    gap: 1rem;
    padding: 1rem;
  }
</style>
```

#### 3. Widget Host Implementation
**File:** `plugins/system_dashboard/ui/WidgetHost.svelte`

```svelte
<script lang="ts">
  export let widget: any;
  export let size: 'small' | 'medium' | 'large' = 'medium';
  
  const sizeClasses = {
    small: 'col-span-3 row-span-2',
    medium: 'col-span-6 row-span-4',
    large: 'col-span-12 row-span-6'
  };
</script>

<div class="widget-container {sizeClasses[size]}">
  <div class="widget-header">
    <h3>{widget.title}</h3>
  </div>
  <div class="widget-content">
    <svelte:component this={widget.component} {...widget.props} />
  </div>
</div>
```

#### 4. Widget Registration
Plugins register dashboard widgets via their UI module:

```javascript
// plugins/some_plugin/ui/index.js
import MyDashboardWidget from './MyDashboardWidget.svelte';

export default {
  id: 'some_plugin',
  slots: {
    dashboard_widget: {
      component: MyDashboardWidget,
      props: {
        title: 'My Widget',
        size: 'medium'
      }
    }
  }
};
```

#### 5. Layout Persistence (Optional for MVP)
- Save widget positions to localStorage or backend
- Allow drag-and-drop reordering (using `svelte-dnd-action` or similar)
- Add/remove widgets dynamically

#### 6. Integration with Main App
Update `web/src/App.svelte`:
```svelte
<script lang="ts">
  import { moduleLoader } from '$lib/core/module_loader';
  
  let currentView = 'dashboard'; // Default to dashboard
  
  async function loadView(pluginId: string, viewName: string) {
    const plugin = moduleLoader.getPlugin(pluginId);
    if (plugin?.module?.views?.[viewName]) {
      currentView = viewName;
      currentComponent = plugin.module.views[viewName];
    }
  }
</script>

<main>
  {#if currentView === 'dashboard'}
    <DashboardView />
  {:else}
    <svelte:component this={currentComponent} />
  {/if}
</main>
```

#### 7. Testing

##### Frontend Unit Tests
**File:** `tests/frontend/dashboard.spec.ts`
```typescript
import { render } from '@testing-library/svelte';
import MainView from 'plugins/system_dashboard/ui/MainView.svelte';

test('dashboard renders with widgets', () => {
  const { container } = render(MainView);
  expect(container.querySelector('.dashboard-grid')).toBeInTheDocument();
});

test('empty state shows when no widgets', () => {
  const { getByText } = render(MainView);
  expect(getByText(/no widgets/i)).toBeInTheDocument();
});
```

##### E2E Tests (Playwright)
```typescript
test('widgets are displayed on dashboard', async ({ page }) => {
  await page.goto('/');
  
  // Verify dashboard loads
  await expect(page.locator('.dashboard-grid')).toBeVisible();
  
  // Verify at least one widget
  await expect(page.locator('.widget-container')).toHaveCount(greaterThan(0));
});

test('clicking widget navigates to plugin view', async ({ page }) => {
  await page.goto('/');
  
  // Click on a widget
  await page.click('.widget-container:first-child');
  
  // Verify navigation
  await expect(page.url()).toContain('/plugin/');
});
```

### Example Widgets

Once dashboard is implemented, plugins can create widgets:

**System FS Widget** - Show recent files
```svelte
<script lang="ts">
  let recentFiles = [];
  // Fetch recent files from API
</script>

<div class="fs-widget">
  <h4>Recent Files</h4>
  <ul>
    {#each recentFiles as file}
      <li>{file.name}</li>
    {/each}
  </ul>
</div>
```

**System Monitor Widget** - Show CPU/memory usage
```svelte
<script lang="ts">
  let cpuUsage = 0;
  let memoryUsage = 0;
  // Poll system metrics
</script>

<div class="monitor-widget">
  <div>CPU: {cpuUsage}%</div>
  <div>Memory: {memoryUsage}%</div>
</div>
```

### Estimated Effort
**5-7 hours** (Medium-High complexity)

---

## Implementation Recommendations

### Recommended Order

1. **System LLM Plugin** (First)
   - No dependencies on other tasks
   - Enables semantic search for future features
   - Can be tested independently
   - **Time:** 4-6 hours

2. **System Dashboard** (Second)
   - Depends on frontend core integration (already done)
   - Provides main UI for the application
   - Enables widget system for all plugins
   - **Time:** 5-7 hours

3. **E2E Tests** (Third)
   - Depends on dashboard for full coverage
   - Validates everything works together
   - Can catch integration issues early
   - **Time:** 3-5 hours

**Total estimated time for Phase 3 completion: 12-18 hours**

### Alternative Approach (Testing-First)

If quality assurance is the priority:

1. **E2E Tests Setup** (Basic framework)
   - Set up Playwright configuration
   - Create test structure
   - Write tests for existing features
   - **Time:** 2-3 hours

2. **System LLM Plugin** (With tests)
   - Implement while writing tests
   - Test-driven development approach
   - **Time:** 5-7 hours

3. **System Dashboard** (Complete with tests)
   - Implement with full test coverage
   - Add dashboard E2E tests
   - **Time:** 6-8 hours

---

## Success Criteria

Phase 3 will be considered complete when:

- ✅ System FS plugin is working (DONE)
- ✅ Frontend core integration is working (DONE)
- ⏳ System LLM plugin provides embeddings capability
- ⏳ Dashboard displays widgets from multiple plugins
- ⏳ E2E tests pass for all major user flows
- ⏳ All plugins are documented and tested

---

## Next Steps

**Immediate:** Implement System LLM Plugin
- Most valuable next feature
- Unlocks semantic search capabilities
- No blockers or dependencies

**After LLM:** Choose between Dashboard or E2E Tests based on priorities
- **Dashboard** for user experience
- **E2E Tests** for quality assurance

---

## Resources

- **Task Instructions:** `tasks/phase3_system_plugins/*/INSTRUCTIONS.md`
- **Progress Tracking:** `tasks/PROGRESS.md`
- **Architecture:** `docs/DESIGN.md`
- **Implementation Status:** `docs/IMPLEMENTATION_STATUS.md`
- **Frontend Integration:** `docs/frontend_core_integration.md`

---

## Questions or Issues?

If you encounter any issues during implementation:

1. Check the existing plugin implementations (`plugins/system_fs/`)
2. Review the core SDK (`core/sdk.py`)
3. Check the plugin manager (`core/plugin_manager.py`)
4. Refer to test examples (`tests/plugins/`)

The architecture is designed to be consistent and predictable - if it works for system_fs, the same patterns should work for other plugins.
