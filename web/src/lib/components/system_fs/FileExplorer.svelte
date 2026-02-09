<script lang="ts">
  import { onMount } from 'svelte';
  import { Folder, File as FileIcon, Grip, List as ListIcon, ArrowUp, RefreshCw } from 'lucide-svelte';

  export let initialPath = ".";

  let currentPath = initialPath;
  let entries: Array<{ name: string; path: string; is_dir: boolean; size: number; mtime: number }> = [];
  let viewMode: 'grid' | 'list' = 'list';
  let loading = false;
  let error = "";

  async function loadDir(path: string) {
    loading = true;
    error = "";
    try {
      const res = await fetch(`/api/plugins/system_fs/scan?path=${encodeURIComponent(path)}`);
      if (!res.ok) {
        const errData = await res.json().catch(() => ({ detail: res.statusText }));
        throw new Error(errData.detail || "Failed to load directory");
      }
      entries = await res.json();
      currentPath = path;
      // Sort: Directories first, then files
      entries.sort((a, b) => {
        if (a.is_dir === b.is_dir) return a.name.localeCompare(b.name);
        return a.is_dir ? -1 : 1;
      });
    } catch (e: any) {
      error = e.message;
    } finally {
      loading = false;
    }
  }

  function goUp() {
    // Basic parent logic: remove last segment
    // Handles both slash types implicitly if we standardise or just let OS handle ".."
    // But ".." relative to "." is tricky if we don't know absolute path.
    // Let's ask API for ".." relative to current.
    // Actually, simpler: just join(currentPath, "..") and let API resolve it.
    // But UI path will look ugly: "./../../".
    // Better: split by separator.
    const separator = currentPath.includes("\\") ? "\\" : "/";
    const parts = currentPath.replace(/\/$/, "").split(separator);
    if (parts.length > 1) {
      parts.pop();
      const parent = parts.join(separator) || separator; // fallback to root if empty
      loadDir(parent);
    } else {
        // Already at root or "."
        loadDir("..");
    }
  }

  function formatSize(bytes: number) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
  }

  function formatDate(ts: number) {
      return new Date(ts * 1000).toLocaleString();
  }

  onMount(() => {
    loadDir(currentPath);
  });
</script>

<div class="h-full flex flex-col bg-surface-50-900-token">
  <!-- Toolbar -->
  <div class="flex items-center gap-2 p-2 border-b border-surface-500/30 bg-surface-100-800-token">
    <button class="btn-icon btn-icon-sm variant-ghost" on:click={goUp} title="Up">
      <ArrowUp size={18} />
    </button>
    <button class="btn-icon btn-icon-sm variant-ghost" on:click={() => loadDir(currentPath)} title="Refresh">
      <RefreshCw size={18} />
    </button>

    <div class="flex-1 input-group input-group-divider grid-cols-[1fr_auto]">
        <input type="text" class="input h-8" bind:value={currentPath} on:change={() => loadDir(currentPath)} />
    </div>

    <div class="flex border border-surface-500/30 rounded overflow-hidden">
        <button class="btn-icon btn-icon-sm {viewMode === 'grid' ? 'bg-primary-500 text-white' : 'bg-surface-200-700-token'}" on:click={() => viewMode = 'grid'}>
            <Grip size={18} />
        </button>
        <button class="btn-icon btn-icon-sm {viewMode === 'list' ? 'bg-primary-500 text-white' : 'bg-surface-200-700-token'}" on:click={() => viewMode = 'list'}>
            <ListIcon size={18} />
        </button>
    </div>
  </div>

  <!-- Content -->
  <div class="flex-1 overflow-auto p-2">
    {#if loading}
      <div class="flex justify-center items-center h-full">
         <span class="loading loading-spinner">Loading...</span>
      </div>
    {:else if error}
      <div class="alert variant-filled-error m-4">
         <span>{error}</span>
         <button class="btn variant-filled" on:click={() => loadDir(currentPath)}>Retry</button>
      </div>
    {:else}
      {#if viewMode === 'grid'}
        <div class="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-6 gap-4">
          {#each entries as entry}
            <div
              class="card p-4 flex flex-col items-center gap-2 hover:bg-surface-200-700-token cursor-pointer transition-colors relative group"
              on:click={() => entry.is_dir ? loadDir(entry.path) : null}
              on:keydown={(e) => e.key === 'Enter' && entry.is_dir && loadDir(entry.path)}
              tabindex="0"
              role="button"
            >
              <div class="text-primary-500">
                  {#if entry.is_dir}
                    <Folder size={48} />
                  {:else}
                    <FileIcon size={48} />
                  {/if}
              </div>
              <span class="text-sm text-center truncate w-full" title={entry.name}>{entry.name}</span>

              <!-- Context Menu Slot -->
              <div class="absolute top-2 right-2 opacity-0 group-hover:opacity-100 transition-opacity">
                 <slot name="context_menu" entry={entry} />
              </div>
            </div>
          {/each}
        </div>
      {:else}
        <div class="flex flex-col gap-1">
           {#each entries as entry}
             <div
                class="flex items-center gap-4 p-2 rounded hover:bg-surface-200-700-token cursor-pointer relative group"
                on:click={() => entry.is_dir ? loadDir(entry.path) : null}
                on:keydown={(e) => e.key === 'Enter' && entry.is_dir && loadDir(entry.path)}
                tabindex="0"
                role="button"
             >
                <div class="text-primary-500 shrink-0">
                    {#if entry.is_dir}
                        <Folder size={24} />
                    {:else}
                        <FileIcon size={24} />
                    {/if}
                </div>
                <span class="flex-1 truncate" title={entry.name}>{entry.name}</span>
                <span class="text-xs text-surface-400 w-24 text-right">{entry.is_dir ? '-' : formatSize(entry.size)}</span>
                <span class="text-xs text-surface-400 w-36 text-right hidden sm:block">{formatDate(entry.mtime)}</span>

                 <!-- Context Menu Slot -->
                 <div class="opacity-0 group-hover:opacity-100 transition-opacity">
                    <slot name="context_menu" entry={entry} />
                 </div>
             </div>
           {/each}
        </div>
      {/if}

      {#if entries.length === 0}
         <div class="text-center text-surface-400 mt-10">Empty Directory</div>
      {/if}
    {/if}
  </div>
</div>
