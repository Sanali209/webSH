import { uiState } from '../stores/ui.svelte.ts';
import axios from 'axios';

// Sync current state with backend
export const syncWithBackend = async () => {
    try {
        const payload = uiState.desktops;
        await axios.post('/api/v1/desktop/sync', payload);
        console.log('Synced state with backend');
    } catch (e) {
        console.error('Failed to sync state:', e);
    }
};

// Load state from backend on startup
export const loadState = async () => {
    try {
        const response = await axios.get('/api/v1/desktop/sync');
        const data = response.data;

        if (Array.isArray(data) && data.length > 0) {
            uiState.desktops = data;
            uiState.widgets = data.flatMap((d: any) => d.widgets);
            if (!data.some((d: any) => d.id === uiState.activeDesktop)) {
                uiState.activeDesktop = data[0].id;
            }
        }
        console.log('Loaded state from backend');
    } catch (e) {
        console.error('Failed to load state:', e);
    }
};

// CRUD Operations

export const addDesktop = async () => {
    uiState.addDesktop();
    await syncWithBackend();
};

export const removeDesktop = async (id: number) => {
    uiState.removeDesktop(id);
    await syncWithBackend();
};

export const switchDesktop = (id: number) => {
    uiState.setActiveDesktop(id);
};

export const saveState = () => {
    syncWithBackend();
};
