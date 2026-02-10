import { writable } from 'svelte/store';

export type Notification = {
    id: string;
    message: string;
    severity: 'info' | 'warning' | 'error';
    timeout?: number;
};

export const notifications = writable<Notification[]>([]);

export const addNotification = (message: string, severity: 'info' | 'warning' | 'error' = 'info', timeout = 5000) => {
    const id = crypto.randomUUID();
    const newNotification: Notification = { id, message, severity, timeout };

    notifications.update((curr) => [...curr, newNotification]);

    setTimeout(() => {
        notifications.update((curr) => curr.filter((n) => n.id !== id));
    }, timeout);
};
