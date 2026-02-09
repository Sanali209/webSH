/**
 * Script Engine Plugin UI Entry Point
 */

export default {
  id: 'system_script_engine',
  name: 'Script Engine',
  
  views: {
    main: () => import('./NodeEditor.svelte')
  },
  
  slots: {
    // Could add dashboard widget here in the future
  }
};
