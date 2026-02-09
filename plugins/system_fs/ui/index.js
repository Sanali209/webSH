/**
 * System FS Plugin - UI Module Entry Point
 * 
 * This file demonstrates how a plugin can export UI components
 * that will be loaded dynamically by the ModuleLoader.
 */

import FileSystemWidget from './FileSystemWidget.svelte';

export default {
  // Plugin metadata
  id: 'system_fs',
  name: 'File System',
  
  // Slot registrations - define which components to render in which slots
  slots: {
    // Dashboard widget
    dashboard_widget: {
      component: FileSystemWidget,
      props: {
        title: 'File System',
        size: 'medium'
      }
    },
    
    // Example: Add a file system icon to the system tray
    system_tray: {
      component: null, // Would be a Svelte component
      props: {
        icon: 'folder',
        tooltip: 'File System'
      }
    },
    
    // Example: Add context menu actions for files
    context_menu: {
      component: null, // Would be a Svelte component for context menu items
      props: {}
    }
  },
  
  // Main views exported by this plugin
  views: {
    explorer: null, // Would be FileExplorer component
  }
};

