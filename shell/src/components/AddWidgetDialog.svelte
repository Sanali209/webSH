<script>
    import { loadExtensions } from "../lib/services/extensionLoader";
    import { addWidget } from "../lib/services/uiManager";
    import { closeModal } from "../lib/modal.svelte.js";
    import { StickyNote, Box, Link } from "lucide-svelte";
    import { onMount } from "svelte";

    let activeTab = $state("widgets");
    let items = $state([]);
    let loading = $state(false);

    const tabs = [
        { id: "widgets", label: "Widgets", icon: StickyNote },
        { id: "applications", label: "Applications", icon: Box },
        { id: "shortcuts", label: "Shortcuts", icon: Link },
    ];

    const loadItems = async (tab) => {
        loading = true;
        activeTab = tab;
        // Map tab id to filter type expected by extensionLoader
        let filter = "widget";
        if (tab === "applications") filter = "application";
        if (tab === "shortcuts") filter = "shortcut";

        items = await loadExtensions(filter);
        loading = false;
    };

    const handleSelect = async (item) => {
        await addWidget(item);
        closeModal();
    };

    onMount(() => {
        loadItems("widgets");
    });
</script>

<div class="dialog-container">
    <div class="tabs">
        {#each tabs as tab}
            {@const Icon = tab.icon}
            <button
                class="tab-btn"
                class:active={activeTab === tab.id}
                onclick={() => loadItems(tab.id)}
            >
                <Icon size={16} />
                {tab.label}
            </button>
        {/each}
    </div>

    <div class="content">
        {#if loading}
            <div class="message">Loading...</div>
        {:else if items.length === 0}
            <div class="message">No items found.</div>
        {:else}
            <div class="grid">
                {#each items as item}
                    <button class="item-card" onclick={() => handleSelect(item)}>
                        <div class="icon">
                            {#if item.icon}
                                <!-- Assume icon is a string for now, or lucide icon name -->
                                <!-- For simplicity, just use a generic icon if string isn't an image url -->
                                <Box size={24} />
                            {:else}
                                <Box size={24} />
                            {/if}
                        </div>
                        <div class="info">
                            <h4>{item.title || item.id}</h4>
                            <p>{item.description || item.plugin_id}</p>
                        </div>
                    </button>
                {/each}
            </div>
        {/if}
    </div>
</div>

<style>
    .dialog-container {
        display: flex;
        flex-direction: column;
        height: 100%;
        background: var(--bg-primary);
        color: var(--text-primary);
    }

    .tabs {
        display: flex;
        border-bottom: 1px solid var(--border-color);
        padding: 0 1rem;
        background: var(--bg-secondary);
    }

    .tab-btn {
        background: transparent;
        border: none;
        color: var(--text-secondary);
        padding: 1rem;
        cursor: pointer;
        display: flex;
        align-items: center;
        gap: 0.5rem;
        border-bottom: 2px solid transparent;
        transition: all 0.2s;
    }

    .tab-btn:hover {
        color: var(--text-primary);
    }

    .tab-btn.active {
        color: var(--primary);
        border-bottom-color: var(--primary);
    }

    .content {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
    }

    .grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(150px, 1fr));
        gap: 1rem;
    }

    .item-card {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        padding: 1rem;
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 0.5rem;
        cursor: pointer;
        transition: transform 0.1s, background 0.1s;
        text-align: center;
    }

    .item-card:hover {
        background: var(--bg-hover);
        transform: translateY(-2px);
    }

    .info h4 {
        margin: 0;
        font-size: 0.9rem;
        font-weight: 500;
    }

    .info p {
        margin: 0;
        font-size: 0.75rem;
        color: var(--text-secondary);
    }

    .message {
        text-align: center;
        padding: 2rem;
        color: var(--text-secondary);
    }
</style>
