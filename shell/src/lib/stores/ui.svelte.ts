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
    props?: string;
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
        // Find max ID to avoid collisions when removing/adding
        const maxId = this.desktops.length > 0 ? Math.max(...this.desktops.map(d => d.id)) : -1;
        const id = maxId + 1;
        this.desktops.push({ id, widgets: [] });
        return id;
    }

    removeDesktop(id: number) {
        if (this.desktops.length <= 1) return;

        const index = this.desktops.findIndex(d => d.id === id);
        if (index !== -1) {
            const removedDesktop = this.desktops[index];
            // Remove widgets of this desktop from global list
            const widgetIdsToRemove = new Set(removedDesktop.widgets.map(w => w.id));
            this.widgets = this.widgets.filter(w => !widgetIdsToRemove.has(w.id));

            // Remove desktop
            this.desktops.splice(index, 1);

            // If we removed the active desktop, switch to another one
            if (this.activeDesktop === id) {
                const newIndex = Math.max(0, index - 1);
                if (this.desktops[newIndex]) {
                    this.activeDesktop = this.desktops[newIndex].id;
                }
            }
        }
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
