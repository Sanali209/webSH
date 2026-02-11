<script>
    import { Activity } from "lucide-svelte";
    import { openModal } from "../../lib/modal.svelte.js";
    import InspectorView from "./InspectorView.svelte";

    const handleClick = () => {
        openModal(InspectorView, {}, "System Inspector");
    };
</script>

<button
    class="action-btn"
    onclick={handleClick}
    aria-label="System Inspector"
    title="System Inspector"
>
    <Activity size={20} />
</button>

<style>
    .action-btn {
        background: transparent;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        padding: 0.5rem;
        border-radius: 4px;
        display: flex;
        align-items: center;
        justify-content: center;
    }

    .action-btn:hover {
        background: var(--bg-hover);
        color: var(--text-primary);
    }
</style>
