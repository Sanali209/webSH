<script>
  import { appState } from "../../lib/store.svelte.js";
  import { uiState } from "../../lib/stores/ui.svelte.ts";
  import { addDesktop, removeDesktop, switchDesktop } from "../../lib/services/uiManager.ts";
  import { LayoutGrid, Monitor, Settings, Plug, Plus, X } from "lucide-svelte";
  import Slot from "../system/Slot.svelte";
</script>

<aside class="sidebar" class:collapsed={!appState.isSidebarOpen}>
  <div class="logo-area">
    <LayoutGrid size={28} />
  </div>

  <nav>
    {#each uiState.desktops as desktop (desktop.id)}
      <div class="desktop-row">
          <button
            class="desktop-btn"
            class:active={uiState.activeDesktop === desktop.id}
            onclick={() => switchDesktop(desktop.id)}
            aria-label="Desktop {desktop.id}"
          >
            <Monitor size={20} />
            <span class="label">Desktop {desktop.id}</span>
          </button>

          {#if appState.isSidebarOpen && uiState.desktops.length > 1}
            <button class="delete-btn" onclick={(e) => { e.stopPropagation(); removeDesktop(desktop.id); }} aria-label="Delete Desktop {desktop.id}">
                <X size={14} />
            </button>
          {/if}
      </div>
    {/each}

    <button class="add-btn" onclick={addDesktop} aria-label="Add Desktop">
        <Plus size={20} />
        {#if appState.isSidebarOpen}
            <span class="label">New Desktop</span>
        {/if}
    </button>
  </nav>

  <div class="footer">
    <Slot name="sidebar.bottom" />
    <button class="action-btn" aria-label="Plugins">
      <Plug size={20} />
    </button>
    <button class="action-btn" aria-label="Settings">
      <Settings size={20} />
    </button>
  </div>
</aside>

<style>
  .sidebar {
    width: 250px;
    height: 100vh;
    background: var(--bg-secondary);
    border-right: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    transition: width 0.2s;
  }

  .sidebar.collapsed {
    width: 60px;
  }

  .logo-area {
    height: 60px;
    display: flex;
    align-items: center;
    justify-content: center;
    border-bottom: 1px solid var(--border-color);
  }

  nav {
    flex: 1;
    padding: 1rem 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }

  .desktop-row {
    display: flex;
    align-items: center;
    padding: 0 1rem;
    gap: 0.5rem;
  }

  .sidebar.collapsed .desktop-row {
      padding: 0;
      justify-content: center;
  }

  .desktop-btn {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 1rem;
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    transition: all 0.2s;
    flex: 1;
    text-align: left;
    border-radius: 4px;
  }

  .desktop-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .desktop-btn.active {
    background: var(--accent-color);
    color: white;
  }

  .delete-btn {
      background: transparent;
      border: none;
      color: var(--text-secondary);
      cursor: pointer;
      padding: 0.5rem;
      opacity: 0;
      transition: opacity 0.2s;
      display: flex;
      align-items: center;
      justify-content: center;
  }

  .desktop-row:hover .delete-btn {
      opacity: 1;
  }

  .delete-btn:hover {
      color: #ef4444; /* Red-500 */
      background: rgba(239, 68, 68, 0.1);
      border-radius: 4px;
  }

  .add-btn {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
    padding: 0.75rem 1rem;
    background: transparent;
    border: 1px dashed var(--border-color);
    color: var(--text-secondary);
    cursor: pointer;
    margin: 0.5rem 1rem;
    border-radius: 4px;
    transition: all 0.2s;
  }

  .add-btn:hover {
      border-color: var(--text-primary);
      color: var(--text-primary);
      background: var(--bg-hover);
  }

  .footer {
    padding: 1rem;
    border-top: 1px solid var(--border-color);
    display: flex;
    justify-content: space-around;
  }

  .action-btn {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 0.5rem;
    border-radius: 4px;
  }

  .action-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  /* Hide labels when collapsed */
  .sidebar.collapsed .label {
    display: none;
  }

  .sidebar.collapsed .desktop-btn {
    justify-content: center;
    padding: 0.75rem 0;
  }

  .sidebar.collapsed .add-btn {
      margin: 0.5rem 0.5rem;
      padding: 0.5rem;
  }

  .sidebar.collapsed .desktop-row {
      padding: 0 0.5rem;
  }

  /* Hide delete button when collapsed */
  .sidebar.collapsed .delete-btn {
      display: none;
  }
</style>
