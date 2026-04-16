<script>
  import { appState } from "../../lib/store.svelte.js";
  import { uiState } from "../../lib/stores/ui.svelte.ts";
  import {
    addDesktop,
    removeDesktop,
    switchDesktop,
  } from "../../lib/services/uiManager.ts";
  import {
    LayoutGrid,
    Monitor,
    Settings as SettingsIcon,
    Plug,
    Plus,
    X,
    Menu,
  } from "lucide-svelte";
  import Slot from "../system/Slot.svelte";
  import { openModal } from "../../lib/modal.svelte.js";
  import SettingsModal from "../system/SettingsModal.svelte";

  function toggleSidebar() {
    appState.isSidebarOpen = !appState.isSidebarOpen;
  }

  function openSettings() {
    openModal(SettingsModal);
  }
</script>

<aside class="sidebar" class:collapsed={!appState.isSidebarOpen}>
  <div class="logo-area">
    <button
      class="toggle-btn"
      onclick={toggleSidebar}
      aria-label="Toggle Sidebar"
    >
      <Menu size={24} />
    </button>
    {#if appState.isSidebarOpen}
      <span class="logo-text">WebSH</span>
    {/if}
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
          {#if appState.isSidebarOpen}
            <span class="label">Desktop {desktop.id}</span>
          {/if}
        </button>

        {#if appState.isSidebarOpen && uiState.desktops.length > 1}
          <button
            class="delete-btn"
            onclick={(e) => {
              e.stopPropagation();
              removeDesktop(desktop.id);
            }}
            aria-label="Delete Desktop {desktop.id}"
          >
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
      {#if appState.isSidebarOpen}
        <span class="label">Plugins</span>
      {/if}
    </button>
    <button class="action-btn" onclick={openSettings} aria-label="Settings">
      <SettingsIcon size={20} />
      {#if appState.isSidebarOpen}
        <span class="label">Settings</span>
      {/if}
    </button>
  </div>
</aside>

<style>
  .sidebar {
    position: absolute; /* Overlay on top of content */
    top: 0;
    left: 0;
    width: 250px;
    height: 100vh;
    background: var(--bg-secondary);
    border-right: 1px solid var(--border-color);
    display: flex;
    flex-direction: column;
    transition: width 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    z-index: 1000; /* Ensure it's above everything */
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.3);
  }

  .sidebar.collapsed {
    width: 60px;
  }

  .logo-area {
    height: 60px;
    display: flex;
    align-items: center;
    padding: 0 1rem;
    border-bottom: 1px solid var(--border-color);
    gap: 1rem;
  }

  .logo-text {
    font-weight: bold;
    font-size: 1.2rem;
    color: var(--text-primary);
    white-space: nowrap;
  }

  .toggle-btn {
    background: transparent;
    border: none;
    color: var(--text-primary);
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 0.5rem;
    border-radius: 4px;
  }

  .toggle-btn:hover {
    background: var(--bg-hover);
  }

  .sidebar.collapsed .logo-area {
    justify-content: center;
    padding: 0;
  }

  .sidebar.collapsed .logo-text {
    display: none;
  }

  nav {
    flex: 1;
    padding: 1rem 0;
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
    overflow-y: auto;
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
    white-space: nowrap;
    overflow: hidden;
  }

  .sidebar.collapsed .desktop-btn {
    justify-content: center;
    padding: 0.75rem 0;
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

  .sidebar.collapsed .delete-btn {
    display: none;
  }

  .add-btn {
    display: flex;
    align-items: center;
    gap: 1rem;
    padding: 0.75rem 1rem;
    background: transparent;
    border: 1px dashed var(--border-color);
    color: var(--text-secondary);
    cursor: pointer;
    margin: 0.5rem 1rem;
    border-radius: 4px;
    transition: all 0.2s;
    white-space: nowrap;
  }

  .sidebar.collapsed .add-btn {
    margin: 0.5rem;
    padding: 0.75rem;
    justify-content: center;
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
    flex-direction: column;
    gap: 0.5rem;
  }

  .action-btn {
    background: transparent;
    border: none;
    color: var(--text-secondary);
    cursor: pointer;
    padding: 0.75rem 1rem;
    border-radius: 4px;
    display: flex;
    align-items: center;
    gap: 1rem;
    transition: all 0.2s;
    width: 100%;
    text-align: left;
  }

  .sidebar.collapsed .action-btn {
    justify-content: center;
    padding: 0.75rem 0;
  }

  .action-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .label {
    flex: 1;
  }

  .sidebar.collapsed .label {
    display: none;
  }
</style>
