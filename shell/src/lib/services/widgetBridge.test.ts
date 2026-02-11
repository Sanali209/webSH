import { describe, it, expect, vi } from 'vitest';
import { createConnection } from './widgetBridge';
import * as penpal from 'penpal';

vi.mock('penpal', () => ({
    connect: vi.fn(),
    WindowMessenger: vi.fn(),
}));

describe('WidgetBridge', () => {
    it('should create a connection using penpal', async () => {
        const iframe = document.createElement('iframe');
        // We need to attach iframe to document to have contentWindow, or mock contentWindow
        // Mock contentWindow
        Object.defineProperty(iframe, 'contentWindow', { value: {} });

        const methods = { test: 'method' };

        const mockDestroy = vi.fn();
        const mockPromise = Promise.resolve({});

        vi.mocked(penpal.connect).mockReturnValue({
            destroy: mockDestroy,
            promise: mockPromise,
        } as any);

        const connection = createConnection(iframe, methods);

        expect(penpal.WindowMessenger).toHaveBeenCalledWith({
            remoteWindow: iframe.contentWindow,
            allowedOrigins: ['*'],
        });

        expect(penpal.connect).toHaveBeenCalledWith({
            messenger: expect.any(Object), // Instance of WindowMessenger
            methods,
        });

        expect(connection.destroy).toBe(mockDestroy);
        expect(connection.promise).toBe(mockPromise);
    });
});
