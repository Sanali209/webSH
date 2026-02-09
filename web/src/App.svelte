<script lang="ts">
  import { onMount } from 'svelte';
  // We will dynamically load plugins here later
  import FileExplorer from '$lib/components/system_fs/FileExplorer.svelte';
</script>

<div class="h-full w-full flex flex-col">
  <header class="p-4 bg-surface-100-800-token border-b border-surface-500/30">
    <h1 class="h3 font-bold">PC Center</h1>
  </header>
  <main class="flex-1 p-4 overflow-auto">
    <FileExplorer />
  </main>
</div>
