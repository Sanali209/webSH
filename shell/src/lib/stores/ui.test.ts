import { describe, it, expect, beforeEach } from 'vitest';
import { UIState } from './ui.svelte.ts';

describe('UIState', () => {
    let uiState: UIState;

    beforeEach(() => {
        uiState = new UIState();
    });

    it('should initialize with default desktop', () => {
        expect(uiState.desktops.length).toBe(1);
        expect(uiState.activeDesktop).toBe(0);
        expect(uiState.widgets.length).toBe(0);
    });

    it('should add a desktop', () => {
        const id = uiState.addDesktop();
        expect(uiState.desktops.length).toBe(2);
        expect(uiState.desktops[1].id).toBe(id);
    });

    it('should set active desktop', () => {
        uiState.setActiveDesktop(1);
        expect(uiState.activeDesktop).toBe(1);
    });

    it('should add a widget', () => {
        const widget = {
            id: 'w1',
            x: 0,
            y: 0,
            w: 1,
            h: 1,
            type: 'icon' as const
        };
        uiState.addWidget(0, widget);
        expect(uiState.desktops[0].widgets.length).toBe(1);
        expect(uiState.desktops[0].widgets[0].id).toBe('w1');
    });

    it('should remove a widget', () => {
        const widget = {
            id: 'w1',
            x: 0,
            y: 0,
            w: 1,
            h: 1,
            type: 'icon' as const
        };
        uiState.addWidget(0, widget);
        uiState.removeWidget(0, 'w1');
        expect(uiState.desktops[0].widgets.length).toBe(0);
    });
});
