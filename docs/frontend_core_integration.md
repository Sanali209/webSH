# Frontend Core Integration

This document describes the dynamic plugin loading system for the PC Center frontend.

## Overview

The frontend core integration allows plugins to dynamically load their UI components and register them in specific slots throughout the application. This is achieved through two main components:

1. **ModuleLoader** - Fetches and dynamically imports plugin UI modules
2. **SlotManager** - Renders plugin components in specific UI slots

## ModuleLoader

The `ModuleLoader` is a singleton service that manages the dynamic loading of plugin UI modules.

### Usage

```typescript
import { moduleLoader } from '$lib/core/module_loader';

// Initialize the loader (typically done on app mount)
await moduleLoader.init();

// Get a specific plugin
const plugin = moduleLoader.getPlugin('system_fs');

// Get all active plugins
const activePlugins = moduleLoader.getActivePlugins();

// Reload plugins
await moduleLoader.reload();
```

### How It Works

1. Fetches the list of active plugins from `/api/plugins` endpoint
2. For each active plugin, attempts to dynamically import from `/plugins/{plugin_id}/ui/index.js`
3. Stores loaded modules in an internal map
4. Provides methods to access loaded plugins

### Plugin UI Module Structure

A plugin's UI module should export a default object with the following structure:

```javascript
export default {
  id: 'plugin_id',
  name: 'Plugin Name',
  
  // Slot registrations
  slots: {
    system_tray: {
      component: SvelteTrayComponent,
      props: { /* default props */ }
    },
    context_menu: {
      component: SvelteContextMenuComponent,
      props: { /* default props */ }
    }
  },
  
  // Main views
  views: {
    main: SvelteMainViewComponent
  }
};
```

## SlotManager

The `SlotManager` is a Svelte component that renders plugin components in specific UI slots.

### Usage

```svelte
<script>
  import SlotManager from '$lib/core/SlotManager.svelte';
</script>

<!-- Render plugins registered for the system_tray slot -->
<SlotManager slotName="system_tray" />

<!-- Pass context data to slot components -->
<SlotManager slotName="context_menu" context={{ selectedFile: file }} />
```

### Available Slots

- **system_tray** - For plugin icons/widgets in the application header
- **context_menu** - For contextual actions (e.g., file operations)

Additional slots can be added by using `SlotManager` with a custom `slotName`.

### Styling

The SlotManager includes default styles for common slot layouts:
- `system_tray` - Horizontal flex layout with gap
- `context_menu` - Vertical flex layout

Custom slots will use `display: contents` to inherit parent layout.

## File Structure

```
web/src/lib/core/
├── module_loader.ts    # ModuleLoader singleton
└── SlotManager.svelte  # SlotManager component

plugins/{plugin_id}/ui/
└── index.js           # Plugin UI entry point
```

## Example: Adding a Plugin UI Component

1. Create the plugin UI directory:
   ```bash
   mkdir -p plugins/my_plugin/ui
   ```

2. Create the UI entry point (`plugins/my_plugin/ui/index.js`):
   ```javascript
   import MyTrayIcon from './MyTrayIcon.svelte';
   
   export default {
     id: 'my_plugin',
     name: 'My Plugin',
     slots: {
       system_tray: {
         component: MyTrayIcon,
         props: { icon: 'star' }
       }
     }
   };
   ```

3. The backend automatically serves this file at `/plugins/my_plugin/ui/index.js`

4. When the ModuleLoader initializes, it will discover and load your plugin UI

## Testing

The ModuleLoader and SlotManager can be tested by:

1. Creating mock plugin manifests
2. Providing test components for slot rendering
3. Verifying correct initialization and component registration

See the test files in `tests/` for examples.

## Future Enhancements

- **Hot Module Replacement** - Reload plugin UIs without full page refresh
- **Plugin Dependencies** - Allow plugins to depend on other plugin UIs
- **Lazy Loading** - Load plugin UIs only when needed
- **Error Boundaries** - Better isolation of plugin UI errors
