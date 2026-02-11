<script>
    import { registry } from "../../lib/registry.svelte.js";

    let { name, class: className } = $props();

    // Reactive derivation of items for this specific slot
    let items = $derived(registry.getItems(name));
</script>

<div class="slot {name} {className || ''}">
    {#each items as item (item.id)}
        {@const Component = item.component}
        <div class="slot-item">
            <Component {...item.props} />
        </div>
    {/each}
</div>

<style>
    .slot {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
</style>
