export interface Widget {
    id: string;
    x: number;
    y: number;
    w: number;
    h: number;
    type: 'icon' | 'widget' | 'headless';
    label?: string;
    icon?: string;
    component?: string;
}

export interface Desktop {
    id: number;
    widgets: Widget[];
}

export class UIState {
    activeDesktop = $state(0);
    desktops = $state<Desktop[]>([]);
    widgets = $state<Widget[]>([]); // Global widget registry or clipboard
    isDevMode = import.meta.env.DEV;

    constructor() {
        // Initialize with at least one desktop
        this.desktops = [{ id: 0, widgets: [] }];
    }

    setActiveDesktop(id: number) {
        this.activeDesktop = id;
    }

    addDesktop() {
        const id = this.desktops.length;
        this.desktops.push({ id, widgets: [] });
        return id;
    }

    addWidget(desktopId: number, widget: Widget) {
        const desktop = this.desktops.find(d => d.id === desktopId);
        if (desktop) {
            desktop.widgets.push(widget);
            this.widgets.push(widget); // Add to global list too if needed
        }
    }

    removeWidget(desktopId: number, widgetId: string) {
        const desktop = this.desktops.find(d => d.id === desktopId);
        if (desktop) {
            desktop.widgets = desktop.widgets.filter(w => w.id !== widgetId);
            this.widgets = this.widgets.filter(w => w.id !== widgetId);
        }
    }
}

export const uiState = new UIState();
