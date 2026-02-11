import axios from 'axios';
import { loadState } from './services/uiManager.ts';

export const appState = $state({
    activeDesktop: 1,
    plugins: [],
    isSidebarOpen: true,
    notifications: [],
    isConnected: false,
    desktopWidgets: {
        1: [
            { id: 'trash', x: 0, y: 0, w: 1, h: 1, type: 'icon', label: 'Trash', icon: 'trash' },
            { id: 'settings', x: 0, y: 1, w: 1, h: 1, type: 'icon', label: 'Settings', icon: 'settings' },
            { id: 'clock', x: 1, y: 0, w: 2, h: 2, type: 'widget', label: 'Clock', component: 'ClockWidget' },
            { id: 'inspector', x: -1, y: -1, w: 0, h: 0, type: 'headless', label: 'System Inspector', component: 'SystemInspector' }
        ],
        2: [],
        3: [],
        4: [],
        5: []
    }
});

export const getActiveDesktop = () => appState.activeDesktop;
export const setActiveDesktop = (id) => { appState.activeDesktop = id; };

export const moveWidget = (desktopId, widgetId, newX, newY) => {
    const desktop = appState.desktopWidgets[desktopId];
    const widget = desktop.find(w => w.id === widgetId);
    if (widget) {
        widget.x = newX;
        widget.y = newY;
    }
};

export const addWidget = (desktopId, widget) => {
    appState.desktopWidgets[desktopId].push(widget);
};

export const executeShortcut = (widgetId) => {
    console.log(`Executing shortcut for widget: ${widgetId}`);
    // Future: Call Kernel API to execute capability
    // axios.post('/api/v1/execute', { id: widgetId });
};

export const initSystem = async () => {
    try {
        // 1. Fetch Plugins
        const response = await axios.get('/api/v1/plugins');
        appState.plugins = response.data;
        console.log('Plugins loaded:', appState.plugins);

        // 2. Load Desktop State
        await loadState();

    } catch (e) {
        console.error('Failed to load plugins or state:', e);
    }

    // 3. WebSocket Connection
    connectWebSocket();
};

let ws;
const connectWebSocket = () => {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        console.log('WebSocket connected');
        appState.isConnected = true;
    };

    ws.onmessage = (event) => {
        try {
            const msg = JSON.parse(event.data);
            console.log('WS Message:', msg);
            // Handle events here
        } catch (e) {
            console.error('WS Parse Error:', e);
        }
    };

    ws.onclose = () => {
        console.log('WebSocket disconnected');
        appState.isConnected = false;
        // Reconnect logic could go here
        setTimeout(connectWebSocket, 5000);
    };

    ws.onerror = (e) => {
        console.error('WebSocket error:', e);
    };
};
