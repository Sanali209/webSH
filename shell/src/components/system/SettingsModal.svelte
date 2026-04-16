<script>
    import { modalStore, closeModal } from "../../lib/modal.svelte.js";
    import { X } from "lucide-svelte";

    // This component is intended to be rendered inside ModalContainer
    // It receives props from the openModal call
    // However, since we are building it as a standalone content, we can just export props
</script>

<div class="settings-modal">
    <div class="header">
        <h2>Settings</h2>
        <button class="close-btn" onclick={closeModal}>
            <X size={20} />
        </button>
    </div>

    <div class="content">
        <div class="section">
            <h3>Appearance</h3>
            <div class="option">
                <label>
                    <input type="checkbox" checked /> Dark Mode
                </label>
            </div>
            <div class="option">
                <label>
                    <input type="checkbox" checked /> Transparent Sidebar
                </label>
            </div>
        </div>

        <div class="section">
            <h3>System</h3>
            <div class="option">
                <span>Version: 3.0.0</span>
            </div>
        </div>
    </div>

    <div class="footer">
        <button class="save-btn" onclick={closeModal}>Close</button>
    </div>
</div>

<style>
    .settings-modal {
        background: var(--bg-secondary);
        border: 1px solid var(--border-color);
        border-radius: 8px;
        width: 400px;
        max-width: 90vw;
        box-shadow: 0 10px 25px rgba(0, 0, 0, 0.5);
        color: var(--text-primary);
        display: flex;
        flex-direction: column;
    }

    .header {
        padding: 1rem;
        border-bottom: 1px solid var(--border-color);
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .header h2 {
        margin: 0;
        font-size: 1.25rem;
    }

    .close-btn {
        background: transparent;
        border: none;
        color: var(--text-secondary);
        cursor: pointer;
        padding: 0.25rem;
        display: flex;
    }

    .close-btn:hover {
        color: var(--text-primary);
    }

    .content {
        padding: 1.5rem;
        display: flex;
        flex-direction: column;
        gap: 1.5rem;
    }

    .section h3 {
        margin: 0 0 0.5rem 0;
        font-size: 0.9rem;
        text-transform: uppercase;
        color: var(--text-secondary);
        font-weight: 600;
    }

    .option {
        padding: 0.5rem 0;
    }

    .footer {
        padding: 1rem;
        border-top: 1px solid var(--border-color);
        display: flex;
        justify-content: flex-end;
    }

    .save-btn {
        background: var(--accent-color);
        color: white;
        border: none;
        padding: 0.5rem 1rem;
        border-radius: 4px;
        cursor: pointer;
        font-weight: 500;
    }

    .save-btn:hover {
        opacity: 0.9;
    }
</style>
