import { connect, WindowMessenger } from 'penpal';

export function connectToParent() {
    const listeners = {};

    const connection = connect({
        messenger: new WindowMessenger({
            remoteWindow: window.parent,
            allowedOrigins: ['*'],
        }),
        methods: {
            emit: (event, data) => {
                if (listeners[event]) {
                    listeners[event].forEach(cb => cb(data));
                }
            }
        }
    });

    return {
        call: async (method, ...args) => {
            const parent = await connection.promise;
            if (typeof parent[method] !== 'function') {
                throw new Error(`Method ${method} not found on parent`);
            }
            return parent[method](...args);
        },
        on: (event, handler) => {
            if (!listeners[event]) {
                listeners[event] = [];
            }
            listeners[event].push(handler);
        },
        destroy: connection.destroy
    };
}
