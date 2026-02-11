<script>
    import { modalStore, closeModal } from "../../lib/modal.svelte.js";
    import { X } from "lucide-svelte";
</script>

{#if modalStore.active}
    <div class="modal-overlay" onclick={closeModal} role="dialog" aria-modal="true">
        <div class="modal-content" onclick={(e) => e.stopPropagation()}>
            <div class="modal-header">
                <h3>{modalStore.active.title}</h3>
                <button class="close-btn" onclick={closeModal}>
                    <X size={20} />
                </button>
            </div>
            <div class="modal-body">
                <svelte:component
                    this={modalStore.active.component}
                    {...modalStore.active.props}
                />
            </div>
        </div>
    </div>
{/if}

<style>
    .modal-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100vw;
        height: 100vh;
        background: rgba(0, 0, 0, 0.5);
        backdrop-filter: blur(4px);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 9999;
    }

    .modal-content {
        background: var(--bg-secondary, #1e293b);
        border: 1px solid var(--border-color, #334155);
        border-radius: 8px;
        width: 80vw;
        height: 80vh;
        display: flex;
        flex-direction: column;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
        overflow: hidden;
    }

    .modal-header {
        padding: 1rem;
        border-bottom: 1px solid var(--border-color, #334155);
        display: flex;
        justify-content: space-between;
        align-items: center;
        background: rgba(0, 0, 0, 0.2);
    }

    .modal-header h3 {
        margin: 0;
        font-size: 1.25rem;
        color: var(--text-primary, #fff);
    }

    .close-btn {
        background: transparent;
        border: none;
        color: var(--text-secondary, #94a3b8);
        cursor: pointer;
        padding: 4px;
        border-radius: 4px;
    }

    .close-btn:hover {
        background: rgba(255, 255, 255, 0.1);
        color: #fff;
    }

    .modal-body {
        flex: 1;
        overflow: hidden;
        position: relative;
    }
</style>
