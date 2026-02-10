# PC Center Developer Guide

This guide is intended for developers who want to contribute to the PC Center core, create new plugins, or understand the system architecture.

## Table of Contents

1.  [Getting Started](#getting-started)
2.  [Architecture Overview](#architecture-overview)
3.  [Backend Development](#backend-development)
    *   [Plugin Structure](#plugin-structure)
    *   [The Plugin SDK](#the-plugin-sdk)
    *   [Database & Persistence](#database--persistence)
    *   [Background Tasks](#background-tasks)
4.  [Frontend Development](#frontend-development)
    *   [Module Loader](#module-loader)
    *   [Slot System](#slot-system)
    *   [Plugin UI Structure](#plugin-ui-structure)
5.  [Testing](#testing)
6.  [Contributing](#contributing)

---

## Getting Started

### Prerequisites

*   **Python 3.10+**
*   **Node.js 18+**
*   **Poetry** (Python dependency management)
*   **Docker & Docker Compose**

### Installation

1.  **Clone the Repository:**
    ```bash
    git clone https://github.com/yourusername/pc-center.git
    cd pc-center
    ```

2.  **Backend Setup:**
    ```bash
    poetry install
    poetry shell
    # Start the backend server
    uvicorn core.main:app --reload
    ```

3.  **Frontend Setup:**
    ```bash
    cd web
    npm install
    # Start the dev server
    npm run dev
    ```

4.  **Access:**
    *   Frontend: `http://localhost:5173`
    *   Backend API Docs: `http://localhost:8000/docs`

---

## Architecture Overview

PC Center follows a modular micro-kernel architecture where the core system provides essential services (Event Bus, Database, Plugin Loader) and features are implemented as **Plugins**.

### Core Components

*   **`core/main.py`**: The entry point. Initializes FastAPI, Taskiq, and the Plugin Loader.
*   **`core/plugin_manager.py`**: Responsible for discovering, validating, resolving dependencies, and loading plugins.
*   **`core/events.py`**: An asynchronous Event Bus allowing decoupled communication between plugins.
*   **`core/database.py`**: Manages LanceDB connections and provides a `PluginDatabaseContext` for scoped data access.
*   **`core/sdk.py`**: The public API for plugin developers.

### Frontend Architecture

The frontend is a **Single Page Application (SPA)** built with Svelte and Vite. It uses a dynamic **Module Loader** to fetch and render plugin UI components at runtime.

---

## Backend Development

### Plugin Structure

A standard plugin resides in `plugins/<plugin_id>/` and must contain:

*   **`manifest.json`**: Metadata (ID, name, version, dependencies, permissions).
*   **`backend.py`**: The main Python module implementing `PluginBase`.
*   **`ui/`**: (Optional) a directory containing the compiled/transpiled frontend assets.

Example `manifest.json`:
```json
{
  "id": "my_plugin",
  "name": "My Awesome Plugin",
  "version": "0.1.0",
  "description": "Does amazing things.",
  "dependencies": ["system_fs"],
  "permissions": ["filesystem:read"],
  "entry_point": "backend.py"
}
```

### The Plugin SDK

Your plugin class must inherit from `PluginBase` and implement lifecycle methods:

```python
from core.sdk import PluginBase, PluginContext

class MyPlugin(PluginBase):
    def on_load(self, context: PluginContext):
        self.context = context
        # Register event listeners, API routes, etc.
        print(f"Plugin {self.context.plugin_id} loaded!")

    def on_activate(self):
        print("Plugin activated")

    def on_deactivate(self):
        print("Plugin deactivated")
```

### Database & Persistence

Plugins should not access the global database directly. Use `self.context.db`:

```python
# Create a table (if not exists)
self.context.db.create_table("my_items", schema=...)

# Insert data
self.context.db.insert("my_items", [{"name": "item1", "value": 10}])

# Query data
results = self.context.db.query("my_items").where("value > 5").to_list()
```

### Background Tasks

Offload heavy processing to Taskiq workers using the `background_task` decorator:

```python
@self.context.background_task
def process_data(data):
    # Heavy computation here
    pass
```

---

## Frontend Development

### Module Loader

The frontend `ModuleLoader` fetches the list of active plugins from `/api/plugins` and dynamically imports their UI entry point (`/plugins/<id>/ui/index.js`).

### Slot System

Plugins can inject components into various parts of the UI (Dashboard, System Tray, File Context Menu) using the **Slot System**.

In your plugin's `ui/index.js`:

```javascript
import MyWidget from './MyWidget.svelte';

export default {
  id: 'my_plugin',
  slots: {
    dashboard_widget: {
      component: MyWidget,
      props: { title: 'My Widget' }
    },
    system_tray: {
      component: MyTrayIcon,
      props: { icon: 'star' }
    }
  },
  views: {
    main: MyMainView
  }
};
```

### Plugin UI Structure

*   **`ui/index.js`**: The entry point. Must export a default object with `slots` and `views`.
*   **Components**: Standard Svelte components.

---

## Testing

We use `pytest` for backend testing.

1.  **Run all tests:**
    ```bash
    poetry run pytest
    ```
2.  **Run specific test file:**
    ```bash
    poetry run pytest tests/core/test_plugin_manager.py
    ```

**Mocking:**
The codebase relies heavily on mocking external dependencies (like `watchdog`, `lancedb`) to ensure tests run in isolated environments. See `tests/conftest.py` for global mocks.

---

## Contributing

1.  **Fork** the repository.
2.  **Create a branch** for your feature (`git checkout -b feature/amazing-feature`).
3.  **Commit** your changes (`git commit -m "Add amazing feature"`).
4.  **Push** to the branch (`git push origin feature/amazing-feature`).
5.  **Open a Pull Request**.

### Code Style

*   **Python:** Follow PEP 8. We use `ruff` for linting and formatting.
*   **TypeScript/Svelte:** Use standard JS/TS conventions. Prettier is recommended.
