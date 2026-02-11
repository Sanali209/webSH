
export interface Extension {
    id: string;
    plugin_id: string;
    type: string;
    entry_point: string;
    component?: any;
    title?: string;
    icon?: string;
    [key: string]: any;
}

export async function loadExtensions(typeFilter?: string): Promise<Extension[]> {
    try {
        const response = await fetch('/api/v1/registry/ui-extensions');
        if (!response.ok) {
            console.error('Failed to fetch extensions:', response.statusText);
            return [];
        }

        const data = await response.json();
        let items: Extension[] = [];

        if (typeFilter) {
            if (typeFilter === 'widget') items = data.widgets || [];
            else if (typeFilter === 'application' || typeFilter === 'view') items = data.applications || [];
            else if (typeFilter === 'shortcut') items = data.shortcuts || [];
            else if (typeFilter === 'top_bar.item') items = data.top_bar || [];
            else {
                 items = [
                    ...(data.widgets || []),
                    ...(data.applications || []),
                    ...(data.shortcuts || []),
                    ...(data.top_bar || [])
                ].filter((item: Extension) => item.type === typeFilter);
            }
        } else {
             items = [
                ...(data.widgets || []),
                ...(data.applications || []),
                ...(data.shortcuts || []),
                ...(data.top_bar || [])
            ];
        }

        const loadedExtensions: Extension[] = [];

        for (const item of items) {
            if (item.entry_point) {
                try {
                    let url = item.entry_point;

                    // If relative, prepend /plugins/{plugin_id}/ui/
                    if (!url.startsWith('/') && !url.startsWith('http')) {
                         url = `/plugins/${item.plugin_id}/ui/${url}`;
                    }

                    // Dynamic import
                    /* @vite-ignore */
                    const module = await import(/* @vite-ignore */ url);

                    loadedExtensions.push({
                        ...item,
                        component: module.default || module
                    });
                } catch (e) {
                    console.error(`Failed to load extension ${item.id} from ${item.entry_point}`, e);
                }
            } else {
                loadedExtensions.push(item);
            }
        }

        return loadedExtensions;

    } catch (e) {
        console.error('Error loading extensions:', e);
        return [];
    }
}
