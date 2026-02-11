import type { UIState } from '../stores/ui.svelte.ts';

const STORAGE_KEY = 'shell_ui_state';

export const saveState = (state: UIState) => {
    try {
        // Runes are proxies, but JSON.stringify usually handles them fine if they wrap objects.
        // However, explicit mapping is safer.
        const data = {
            activeDesktop: state.activeDesktop,
            desktops: state.desktops, // deep clone or rely on proxy serialization
            widgets: state.widgets
        };
        localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
    } catch (e) {
        console.error('Failed to save state:', e);
    }
};

export const loadState = (): any | null => {
    try {
        const data = localStorage.getItem(STORAGE_KEY);
        if (data) {
            return JSON.parse(data);
        }
    } catch (e) {
        console.error('Failed to load state:', e);
    }
    return null;
};

export const syncWithBackend = async (state: UIState) => {
    // Placeholder for backend sync
    console.log('Syncing state with backend...', state);
    // await fetch('/api/v1/desktop/sync', { method: 'POST', body: JSON.stringify(state) });
};
