<script>
    import { uiState } from "../../lib/stores/ui.svelte.ts";
    import { syncWithBackend } from "../../lib/services/uiManager.ts";
    import { executeShortcut } from "../../lib/store.svelte.js";
    import { File, Settings, StickyNote, Trash } from "lucide-svelte";
    import WidgetLoader from "./WidgetLoader.svelte";

    let dragging = $state(null);
    let ghost = $state(null);

    // Grid constants
    const COLS = 12;
    const ROWS = 8;

    // Active desktop widgets
    let activeDesktopObj = $derived(uiState.desktops.find(d => d.id === uiState.activeDesktop));
    let widgets = $derived(activeDesktopObj ? activeDesktopObj.widgets : []);

    const getIcon = (name) => {
        switch (name) {
            case "trash":
                return Trash;
            case "settings":
                return Settings;
            default:
                return File;
        }
    };

    const handleDragStart = (e, widget) => {
        dragging = widget;
        e.dataTransfer.effectAllowed = "move";
        e.dataTransfer.setData("text/plain", JSON.stringify(widget));
    };

    const handleDragOver = (e) => {
        e.preventDefault();
        if (!dragging) return;

        const gridRect = e.currentTarget.getBoundingClientRect();
        const cellWidth = gridRect.width / COLS;
        const cellHeight = gridRect.height / ROWS;

        const x = Math.floor((e.clientX - gridRect.left) / cellWidth);
        const y = Math.floor((e.clientY - gridRect.top) / cellHeight);

        // Validate bounds
        if (x >= 0 && x < COLS && y >= 0 && y < ROWS) {
            // Check boundaries with widget size
            const targetX = Math.min(x, COLS - dragging.w);
            const targetY = Math.min(y, ROWS - dragging.h);

            ghost = { ...dragging, x: targetX, y: targetY };
        }
    };

    const handleDrop = (e) => {
        e.preventDefault();
        if (ghost && dragging && activeDesktopObj) {
            const w = activeDesktopObj.widgets.find(w => w.id === dragging.id);
            if (w) {
                w.x = ghost.x;
                w.y = ghost.y;
                syncWithBackend();
            }
        }
        dragging = null;
        ghost = null;
    };

    const handleDragEnd = () => {
        dragging = null;
        ghost = null;
    };

    const handleDblClick = (widget) => {
        executeShortcut(widget.id);
    };

    const getProps = (p) => {
        if (!p) return {};
        if (typeof p === 'string') {
            try { return JSON.parse(p); } catch { return {}; }
        }
        return p;
    };
</script>

<div
    class="desktop-grid"
    ondragover={handleDragOver}
    ondrop={handleDrop}
    role="grid"
    tabindex="0"
>
    <!-- Render Ghost -->
    {#if ghost}
        <div
            class="grid-item ghost"
            style:grid-column="{ghost.x + 1} / span {ghost.w}"
            style:grid-row="{ghost.y + 1} / span {ghost.h}"
        ></div>
    {/if}

    <!-- Render Widgets -->
    {#each widgets as widget (widget.id)}
        {@const Icon = getIcon(widget.icon)}
        <div
            class="grid-item"
            class:dragging={dragging?.id === widget.id}
            style:grid-column="{widget.x + 1} / span {widget.w}"
            style:grid-row="{widget.y + 1} / span {widget.h}"
            draggable="true"
            ondragstart={(e) => handleDragStart(e, widget)}
            ondragend={handleDragEnd}
            ondblclick={() => handleDblClick(widget)}
            role="gridcell"
            tabindex="0"
        >
            {#if widget.type === "icon"}
                <div class="icon-wrapper">
                    <Icon size={32} />
                    <span class="label">{widget.label}</span>
                </div>
            {:else if widget.type === "widget"}
                <div class="widget-wrapper">
                    <div class="header">
                        <StickyNote size={14} />
                        <span>{widget.label}</span>
                    </div>
                    <div class="body">
                        <WidgetLoader
                            component={widget.component}
                            props={getProps(widget.props)}
                        />
                    </div>
                </div>
            {/if}
        </div>
    {/each}
</div>

<style>
    .desktop-grid {
        display: grid;
        grid-template-columns: repeat(12, 1fr);
        grid-template-rows: repeat(8, 1fr);
        gap: 8px;
        height: 100%;
        width: 100%;
        padding: 1rem;
        box-sizing: border-box;
    }

    .grid-item {
        border-radius: 8px;
        /* blocked by content */
        cursor: grab;
        user-select: none;
        transition: transform 0.1s;
    }

    .grid-item:active {
        cursor: grabbing;
    }

    .grid-item.dragging {
        opacity: 0.5;
    }

    .grid-item.ghost {
        background: rgba(255, 255, 255, 0.1);
        border: 2px dashed rgba(255, 255, 255, 0.3);
        pointer-events: none;
        z-index: 0;
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
