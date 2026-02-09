<script lang="ts">
  import { onMount } from 'svelte';
  import { moduleLoader } from '$lib/core/module_loader';
  import SlotManager from '$lib/core/SlotManager.svelte';
  import FileExplorer from '$lib/components/system_fs/FileExplorer.svelte';

  let initialized = false;
  let error = '';

  onMount(async () => {
    try {
      await moduleLoader.init();
      initialized = true;
      console.log('ModuleLoader initialized successfully');
    } catch (e: any) {
      error = `Failed to initialize plugins: ${e.message}`;
      console.error(error, e);
      // Still set initialized to true to show the app
      initialized = true;
    }
  });
</script>

<div class="h-full w-full flex flex-col">
  <header class="p-4 bg-surface-100-800-token border-b border-surface-500/30 flex items-center justify-between">
    <h1 class="h3 font-bold">PC Center</h1>
    
    <!-- System Tray Slot - for plugin icons/widgets -->
    <div class="flex items-center gap-2">
      {#if initialized}
        <SlotManager slotName="system_tray" />
      {/if}
    </div>
  </header>
  
  <main class="flex-1 p-4 overflow-auto">
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
    {:else}
      <!-- For now, keep FileExplorer hardcoded as the main view -->
      <!-- In the future, this could be dynamic based on active module -->
      <FileExplorer />
    {/if}
  </main>
</div>
