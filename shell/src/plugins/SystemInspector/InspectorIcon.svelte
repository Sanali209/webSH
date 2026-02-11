<script>
    import { Activity } from "lucide-svelte";

    const handleClick = () => {
        alert("System Status: OK\nMemory: 100/1000 MB");
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
