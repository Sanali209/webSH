<script>
  import { appState, setActiveDesktop } from "../../lib/store.svelte.js";
  import { LayoutGrid, Monitor, Settings, Plug } from "lucide-svelte";
  import Slot from "../system/Slot.svelte";

  let desktops = [1, 2, 3, 4, 5];
</script>

<aside class="sidebar" class:collapsed={!appState.isSidebarOpen}>
  <div class="logo-area">
    <LayoutGrid size={28} />
  </div>

  <nav>
    {#each desktops as id}
      <button
        class="desktop-btn"
        class:active={appState.activeDesktop === id}
        onclick={() => setActiveDesktop(id)}
        aria-label="Desktop {id}"
      >
        <Monitor size={20} />
        <span class="label">Desktop {id}</span>
      </button>
    {/each}
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
    width: 100%;
    text-align: left;
  }

  .desktop-btn:hover {
    background: var(--bg-hover);
    color: var(--text-primary);
  }

  .desktop-btn.active {
    background: var(--accent-color);
    color: white;
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
</style>
