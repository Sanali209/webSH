<script lang="ts">
    import { Bell, Wifi, Battery, Plus } from "lucide-svelte";
    import { uiState } from "../../lib/stores/ui.svelte.ts";
    import { loadExtensions, type Extension } from "../../lib/services/extensionLoader";
    import { openModal } from "../../lib/modal.svelte.js";
    import AddWidgetDialog from "../AddWidgetDialog.svelte";
    import { onMount } from "svelte";

    let time = $state(new Date().toLocaleTimeString());
    let topBarExtensions = $state<Extension[]>([]);

    $effect(() => {
        const interval = setInterval(() => {
            time = new Date().toLocaleTimeString();
        }, 1000);
        return () => clearInterval(interval);
    });

    onMount(async () => {
        topBarExtensions = await loadExtensions("top_bar.item");
    });
</script>

<header class="topbar">
    <div class="left">
        <h3>Desktop {uiState.activeDesktop}</h3>
    </div>

    <div class="center">
        <!-- Tray / Dynamic Island placeholder -->
    </div>

    <div class="right">
        <button class="icon-btn" onclick={() => openModal(AddWidgetDialog, {}, "Add Item")} aria-label="Add Widget">
            <Plus size={18} />
        </button>

        {#each topBarExtensions as ext (ext.id)}
            {#if ext.component}
                {@const Component = ext.component}
                <div class="extension-item">
                    <Component />
                </div>
            {/if}
        {/each}

        <div class="status-item">
            <Wifi size={16} />
        </div>
        <div class="status-item">
            <span class="clock">{time}</span>
        </div>
        <button class="icon-btn">
            <Bell size={18} />
        </button>
    </div>
</header>

<style>
    .topbar {
        height: 60px;
        background: var(--bg-secondary);
        border-bottom: 1px solid var(--border-color);
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 0 1.5rem;
    }

    .right {
        display: flex;
        align-items: center;
        gap: 1rem;
    }

    .status-item {
        display: flex;
        align-items: center;
        color: var(--text-secondary);
    }

    .clock {
        font-variant-numeric: tabular-nums;
        font-size: 0.9rem;
    }

    .icon-btn {
        background: transparent;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        padding: 0.5rem;
        border-radius: 50%;
    }

    .icon-btn:hover {
        background: var(--bg-hover);
        color: var(--text-primary);
    }

    .extension-item {
        display: flex;
        align-items: center;
    }
</style>
