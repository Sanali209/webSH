import { connect, WindowMessenger } from 'penpal';

export interface WidgetConnection {
    destroy: () => void;
    promise: Promise<any>;
}

export const createConnection = (
    iframe: HTMLIFrameElement,
    methods: Record<string, any>
): WidgetConnection => {
    // We need to wait for the iframe to load or access contentWindow
    const contentWindow = iframe.contentWindow;
    if (!contentWindow) {
        throw new Error('Iframe contentWindow is null');
    }

    const connection = connect({
        messenger: new WindowMessenger({
            remoteWindow: contentWindow,
            allowedOrigins: ['*'], // Allow any origin for now, can be restricted later
        }),
        methods,
    });

    return {
        destroy: connection.destroy,
        promise: connection.promise,
    };
};
