/**
 * System Dashboard Plugin - UI Entry Point
 */

import MainView from './MainView.svelte';

export default {
  id: 'system_dashboard',
  name: 'System Dashboard',
  
  // Main view component
  views: {
    dashboard: MainView
  },
  
  // Dashboard doesn't need to register in slots itself
  // It provides slots for other plugins
  slots: {}
};
