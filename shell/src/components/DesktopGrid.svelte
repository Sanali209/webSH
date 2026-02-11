<script>
    import { dndzone } from 'svelte-dnd-action';
    import { flip } from 'svelte/animate';
    import { uiState } from '../lib/stores/ui.svelte.ts';
    import { packItems } from '../lib/services/gridManager.ts';
    import GridItem from './GridItem.svelte';

    // We use a derived value to get the active desktop's widgets
    let activeDesktopObj = $derived(uiState.desktops.find(d => d.id === uiState.activeDesktop));

    // Local state for dndzone
    let items = $state([]);
    let clientWidth = $state(0);
    // Calculate cols based on CSS: repeat(auto-fill, minmax(64px, 1fr)) gap: 16px
    // Formula: floor((width + gap) / (item_min_width + gap))
    let cols = $derived(Math.max(1, Math.floor((clientWidth + 16) / 80)));

    // Sync from store to local state
    $effect(() => {
        if (activeDesktopObj) {
            items = activeDesktopObj.widgets;
        }
    });

    const handleDndConsider = (e) => {
        items = e.detail.items;
    };

    const handleDndFinalize = (e) => {
        let newItems = e.detail.items;
        // Recalculate x,y based on new order and current layout
        newItems = packItems(newItems, cols);
        items = newItems;
        // Update the global store with the new order and coordinates
        if (activeDesktopObj) {
            activeDesktopObj.widgets = items;
        }
    };
</script>

<section
    bind:clientWidth={clientWidth}
    use:dndzone={{items, flipDurationMs: 300}}
    onconsider={handleDndConsider}
    onfinalize={handleDndFinalize}
    class="grid-container"
>
    {#each items as item (item.id)}
        <div
            class="grid-item-wrapper"
            animate:flip={{duration: 300}}
            style:grid-column="span {item.w}"
            style:grid-row="span {item.h}"
        >
            <GridItem {item} />
        </div>
    {/each}
</section>

<style>
    .grid-container {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(64px, 1fr));
        grid-auto-rows: 64px;
        gap: 16px;
        height: 100%;
        width: 100%;
        padding: 1rem;
        overflow-y: auto;
        box-sizing: border-box;
    }

    .grid-item-wrapper {
        position: relative;
        /* Ensure the wrapper fills the grid cell(s) */
        width: 100%;
        height: 100%;
    }
</style>
