<script lang="ts">
  import { onMount } from 'svelte';
  import { moduleLoader } from '$lib/core/module_loader';
  import SlotManager from '$lib/core/SlotManager.svelte';
  import FileExplorer from '$lib/components/system_fs/FileExplorer.svelte';

  let initialized = false;
  let error = '';
  let currentView = 'dashboard'; // Default to dashboard
  let DashboardView = null;

  onMount(async () => {
    try {
      await moduleLoader.init();
      initialized = true;
      console.log('ModuleLoader initialized successfully');
      
      // Load dashboard component
      const dashboardPlugin = moduleLoader.getPlugin('system_dashboard');
      if (dashboardPlugin && dashboardPlugin.module && dashboardPlugin.module.views) {
        DashboardView = dashboardPlugin.module.views.dashboard;
      }
    } catch (e: any) {
      error = `Failed to initialize plugins: ${e.message}`;
      console.error(error, e);
      // Still set initialized to true to show the app
      initialized = true;
    }
  });
  
  function navigateTo(view: string) {
    currentView = view;
  }
</script>

<div class="h-full w-full flex flex-col">
  <header class="p-4 bg-surface-100-800-token border-b border-surface-500/30 flex items-center justify-between">
    <h1 class="h3 font-bold">PC Center</h1>
    
    <!-- Navigation -->
    <nav class="flex items-center gap-2">
      <button 
        class="btn btn-sm {currentView === 'dashboard' ? 'variant-filled-primary' : 'variant-ghost'}"
        on:click={() => navigateTo('dashboard')}
      >
        Dashboard
      </button>
      <button 
        class="btn btn-sm {currentView === 'files' ? 'variant-filled-primary' : 'variant-ghost'}"
        on:click={() => navigateTo('files')}
      >
        Files
      </button>
    </nav>
    
    <!-- System Tray Slot - for plugin icons/widgets -->
    <div class="flex items-center gap-2">
      {#if initialized}
        <SlotManager slotName="system_tray" />
      {/if}
    </div>
  </header>
  
  <main class="flex-1 overflow-auto">
    {#if !initialized}
      <div class="flex items-center justify-center h-full">
        <span class="loading loading-spinner">Loading plugins...</span>
      </div>
    {:else if error}
      <div class="alert variant-filled-warning m-4">
        <span>{error}</span>
      </div>
      <!-- Still show FileExplorer even if plugin loading failed -->
      <FileExplorer />
    {:else if currentView === 'dashboard'}
      {#if DashboardView}
        <svelte:component this={DashboardView} />
      {:else}
        <div class="p-4">
          <div class="alert variant-filled-warning">
            Dashboard plugin not loaded. Showing file explorer instead.
          </div>
          <FileExplorer />
        </div>
      {/if}
    {:else if currentView === 'files'}
      <FileExplorer />
    {/if}
  </main>
</div>
