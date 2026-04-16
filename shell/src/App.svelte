<script>
  import Sidebar from "./components/layout/Sidebar.svelte";
  import TopBar from "./components/layout/TopBar.svelte";
  import DesktopGrid from "./components/DesktopGrid.svelte";
  import ModalContainer from "./components/system/ModalContainer.svelte";
  import { appState, initSystem } from "./lib/store.svelte.js";
  import ErrorBoundary from "./lib/components/ErrorBoundary.svelte";
  import WidgetSkeleton from "./lib/components/WidgetSkeleton.svelte";
  import { uiState } from "./lib/stores/ui.svelte.ts";

  $effect(() => {
    initSystem();
    console.log("New UI State Active Desktop:", uiState.activeDesktop);
  });
</script>

<main class="app-container">
  <ModalContainer />
  <Sidebar />

  <div class="content-wrapper">
    <TopBar />

    <div class="viewport">
      <DesktopGrid />
    </div>
  </div>
</main>

<style>
  :global(:root) {
    --bg-primary: #0f172a;
    --bg-secondary: #1e293b;
    --bg-hover: #334155;
    --text-primary: #f8fafc;
    --text-secondary: #94a3b8;
    --border-color: #334155;
    --accent-color: #3b82f6;
  }

  :global(body) {
    margin: 0;
    font-family: "Inter", system-ui, sans-serif;
    background: var(--bg-primary);
    color: var(--text-primary);
    overflow: hidden;
  }

  .app-container {
    display: flex;
    height: 100vh;
    width: 100vw;
  }

  .content-wrapper {
    flex: 1;
    display: flex;
    flex-direction: column;
  }

  .viewport {
    flex: 1;
    padding: 2rem;
    overflow-y: auto;
  }
</style>
