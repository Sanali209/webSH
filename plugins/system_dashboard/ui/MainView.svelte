<script lang="ts">
  /**
   * MainView - System Dashboard main component
   * 
   * Displays a grid layout that hosts widgets from other plugins
   */
  import { onMount } from 'svelte';
  import SlotManager from '$lib/core/SlotManager.svelte';
  
  // Dashboard configuration
  let config = {
    grid_columns: 12,
    row_height: 60,
    gap: 16
  };
  
  let loading = true;
  let error = '';
  
  // Fetch dashboard configuration from backend
  async function loadConfig() {
    try {
      const response = await fetch('/api/plugins/system_dashboard/config');
      if (response.ok) {
        config = await response.json();
      }
    } catch (e) {
      console.error('Failed to load dashboard config:', e);
      error = 'Failed to load dashboard configuration';
    } finally {
      loading = false;
    }
  }
  
  onMount(() => {
    loadConfig();
  });
</script>

<div class="dashboard-container h-full w-full bg-surface-50-900-token overflow-auto">
  {#if loading}
    <div class="flex items-center justify-center h-full">
      <span class="loading loading-spinner">Loading dashboard...</span>
    </div>
  {:else if error}
    <div class="alert variant-filled-error m-4">
      <span>{error}</span>
    </div>
  {:else}
    <!-- Dashboard Header -->
    <div class="dashboard-header p-4 border-b border-surface-500/30">
      <h2 class="h2 font-bold">Dashboard</h2>
      <p class="text-sm text-surface-600-300-token">Overview of your system</p>
    </div>
    
    <!-- Dashboard Grid -->
    <div 
      class="dashboard-grid p-4"
      style="display: grid; grid-template-columns: repeat({config.grid_columns}, 1fr); gap: {config.gap}px;"
    >
      <!-- Slot for dashboard widgets from plugins -->
      <SlotManager 
        slotName="dashboard_widget" 
        context={{ 
          grid_columns: config.grid_columns,
          row_height: config.row_height,
          gap: config.gap
        }} 
      />
      
      <!-- Empty state if no widgets -->
      <div class="col-span-full empty-state" id="dashboard-empty-state">
        <div class="card p-8 text-center bg-surface-100-800-token">
          <div class="mb-4 text-surface-400">
            <svg xmlns="http://www.w3.org/2000/svg" class="h-16 w-16 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M4 5a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM14 5a1 1 0 011-1h4a1 1 0 011 1v2a1 1 0 01-1 1h-4a1 1 0 01-1-1V5zM4 16a1 1 0 011-1h4a1 1 0 011 1v3a1 1 0 01-1 1H5a1 1 0 01-1-1v-3zM14 12a1 1 0 011-1h4a1 1 0 011 1v7a1 1 0 01-1 1h-4a1 1 0 01-1-1v-7z" />
            </svg>
          </div>
          <h3 class="h3 mb-2">No Widgets Available</h3>
          <p class="text-surface-600-300-token">
            Install plugins with dashboard widgets to see them here.
          </p>
        </div>
      </div>
    </div>
  {/if}
</div>

<style>
  .dashboard-container {
    min-height: 100%;
  }
  
  .dashboard-grid {
    min-height: calc(100vh - 120px);
  }
  
  /* Hide empty state if widgets are present */
  .dashboard-grid:has(> :not(.empty-state)) .empty-state {
    display: none;
  }
</style>
