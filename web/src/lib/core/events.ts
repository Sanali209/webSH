import { writable } from 'svelte/store';
import { addNotification } from '$lib/stores/notifications';

export const isConnected = writable(false);

let socket: WebSocket | null = null;
let reconnectTimer: any = null;

export function connect() {
    if (socket && (socket.readyState === WebSocket.OPEN || socket.readyState === WebSocket.CONNECTING)) {
        return;
    }

    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const host = window.location.host;
    // Handle dev mode (vite proxy usually handles /ws, but if not, fallback)
    const url = `${protocol}//${host}/ws/events`;

    console.log(`Connecting to WebSocket at ${url}`);
    socket = new WebSocket(url);

    socket.onopen = () => {
        console.log('WebSocket connected');
        isConnected.set(true);
        if (reconnectTimer) {
            clearTimeout(reconnectTimer);
            reconnectTimer = null;
        }
    };

    socket.onclose = () => {
        console.log('WebSocket disconnected');
        isConnected.set(false);
        socket = null;
        // Reconnect logic
        reconnectTimer = setTimeout(connect, 3000);
    };

    socket.onerror = (error) => {
        console.error('WebSocket error:', error);
        socket?.close();
    };

    socket.onmessage = (event) => {
        try {
            const message = JSON.parse(event.data);
            handleEvent(message);
        } catch (e) {
            console.error('Failed to parse WebSocket message:', e);
        }
    };
}

function handleEvent(message: any) {
    // message structure: { event: string, data: any, correlation_id: string }
    const { event, data } = message;

    if (event === 'notification:new') {
        addNotification(data.message, data.severity, data.timeout);
    }
}
