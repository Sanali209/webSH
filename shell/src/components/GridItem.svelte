<script>
    import { File, StickyNote, Trash, Settings } from 'lucide-svelte';
    import WidgetLoader from './desktop/WidgetLoader.svelte';

    let { item } = $props();

    const getIcon = (name) => {
        switch (name) {
            case "trash": return Trash;
            case "settings": return Settings;
            default: return File;
        }
    };

    // Helper to parse props if string
    const getProps = (p) => {
        if (!p) return {};
        if (typeof p === 'string') {
            try { return JSON.parse(p); } catch { return {}; }
        }
        return p;
    };
</script>

<div
    class="grid-item-root"
    style:grid-column="span {item.w}"
    style:grid-row="span {item.h}"
    role="gridcell"
    tabindex="0"
>
    {#if item.type === "icon"}
        {@const Icon = getIcon(item.icon)}
        <div class="icon-wrapper">
            <Icon size={32} />
            <span class="label">{item.label}</span>
        </div>
    {:else if item.type === "widget"}
        <div class="widget-wrapper">
            <div class="header">
                <StickyNote size={14} />
                <span>{item.label}</span>
            </div>
            <div class="body">
                 <WidgetLoader
                    component={item.component}
                    props={getProps(item.props)}
                />
            </div>
        </div>
    {/if}
</div>

<style>
    .grid-item-root {
        width: 100%;
        height: 100%;
        position: relative;
        /* Ensure it takes space */
        min-height: 64px;
    }

    /* Icon Style */
    .icon-wrapper {
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        height: 100%;
        gap: 4px;
        color: white;
        text-shadow: 0 1px 2px rgba(0, 0, 0, 0.5);
    }

    .icon-wrapper:hover {
        background: rgba(255, 255, 255, 0.1);
        border-radius: 8px;
    }

    .label {
        font-size: 0.85rem;
        text-align: center;
        max-width: 100%;
        overflow: hidden;
        text-overflow: ellipsis;
        white-space: nowrap;
    }

    /* Widget Style */
    .widget-wrapper {
        background: rgba(30, 41, 59, 0.9);
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
        height: 100%;
        width: 100%;
        border-radius: 8px;
        display: flex;
        flex-direction: column;
        overflow: hidden;
    }

    .header {
        background: rgba(0, 0, 0, 0.2);
        padding: 4px 8px;
        font-size: 0.75rem;
        display: flex;
        align-items: center;
        gap: 6px;
        color: #94a3b8;
    }

    .body {
        flex: 1;
        padding: 8px;
        color: #cbd5e1;
        font-size: 0.9rem;
    }
</style>
