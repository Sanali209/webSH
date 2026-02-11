import { uiState } from '../stores/ui.svelte.ts';
import axios from 'axios';
import { findEmptySpot } from './gridManager';
import type { Extension } from './extensionLoader';

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

export const addWidget = async (extension: Extension) => {
    const desktopId = uiState.activeDesktop;
    const desktopIndex = uiState.desktops.findIndex((d: any) => d.id === desktopId);

    if (desktopIndex === -1) {
        console.error('Active desktop not found');
        return;
    }

    const currentWidgets = uiState.desktops[desktopIndex].widgets;

    // Determine size and type
    let w = 1;
    let h = 1;
    let type = 'icon';
    let label = extension.title || extension.id;
    let icon = extension.icon || 'file'; // Default icon
    let component = extension.entry_point;
    let props = {};

    // Resolve component URL
    if (component && !component.startsWith('/') && !component.startsWith('http') && extension.plugin_id) {
         component = `/plugins/${extension.plugin_id}/ui/${component}`;
    }

    if (extension.type === 'widget') {
        type = 'widget';
        // Parse size string "WxH" e.g. "2x2"
        if (extension.size) {
            const [width, height] = extension.size.split('x').map(Number);
            w = width || 2;
            h = height || 2;
        } else {
             w = 2; h = 2;
        }
    } else if (extension.type === 'shortcut' || extension.type === 'application') {
         type = 'icon';
    }

    // Find empty spot
    const spot = findEmptySpot(currentWidgets, w, h);

    if (!spot) {
        alert('No space on desktop!');
        return;
    }

    const newWidget = {
        id: crypto.randomUUID(),
        x: spot.x,
        y: spot.y,
        w,
        h,
        type,
        label,
        icon,
        component,
        props: JSON.stringify(props)
    };

    // Add to state
    uiState.desktops[desktopIndex].widgets.push(newWidget);

    // Sync
    await syncWithBackend();
};
