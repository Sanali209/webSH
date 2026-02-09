<script lang="ts">
  /**
   * FileSystemWidget - Dashboard widget for system_fs plugin
   * Shows basic file system statistics
   */
  import { onMount } from 'svelte';
  import { Folder, File as FileIcon } from 'lucide-svelte';
  
  export let context = {};
  
  let stats = {
    totalFiles: 0,
    totalDirs: 0,
    loading: true
  };
  
  async function loadStats() {
    try {
      // For MVP, just show placeholder stats
      // In real implementation, would fetch from API
      stats = {
        totalFiles: 42,
        totalDirs: 8,
        loading: false
      };
    } catch (e) {
      console.error('Failed to load file system stats:', e);
      stats.loading = false;
    }
  }
  
  onMount(() => {
    loadStats();
  });
</script>

<div class="fs-widget card p-4 bg-surface-100-800-token">
  <div class="flex items-center justify-between mb-4">
    <h3 class="h4 font-bold">File System</h3>
    <Folder size={24} class="text-primary-500" />
  </div>
  
  {#if stats.loading}
    <div class="text-center py-4">
      <span class="text-sm text-surface-500">Loading...</span>
    </div>
  {:else}
    <div class="space-y-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <FileIcon size={18} class="text-surface-500" />
          <span class="text-sm">Files</span>
        </div>
        <span class="font-semibold">{stats.totalFiles}</span>
      </div>
      
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-2">
          <Folder size={18} class="text-surface-500" />
          <span class="text-sm">Directories</span>
        </div>
        <span class="font-semibold">{stats.totalDirs}</span>
      </div>
      
      <div class="pt-2 border-t border-surface-500/30">
        <button class="btn btn-sm variant-ghost-primary w-full">
          Open File Explorer
        </button>
      </div>
    </div>
  {/if}
</div>

<style>
  .fs-widget {
    min-height: 180px;
  }
</style>
