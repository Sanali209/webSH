<script>
    let { component, props } = $props();
    let Widget = $state(null);
    let error = $state(null);

    $effect(() => {
        if (!component) return;

        // Dynamic import
        // Note: In Vite, we need to match the actual file structure.
        // We assume plugins are located in src/plugins/{component}/index.svelte
        const loadWidget = async () => {
            try {
                if (component.startsWith("/") || component.startsWith("http")) {
                     /* @vite-ignore */
                     const mod = await import(/* @vite-ignore */ component);
                     Widget = mod.default || mod;
                } else {
                    // Using specific glob import for reliability in Vite
                    const modules = import.meta.glob(
                        "../../plugins/*/index.svelte",
                    );
                    const path = `../../plugins/${component}/index.svelte`;

                    if (modules[path]) {
                        const mod = await modules[path]();
                        Widget = mod.default;
                    } else {
                        throw new Error(`Widget ${component} not found`);
                    }
                }
            } catch (e) {
                console.error(`Failed to load widget ${component}:`, e);
                error = e.message;
            }
        };

        loadWidget();
    });
</script>

<div class="widget-loader">
    {#if error}
        <div class="error">
            <span>⚠️ {error}</span>
        </div>
    {:else if Widget}
        <Widget {...props} />
    {:else}
        <div class="loading">
            <span>Loading...</span>
        </div>
    {/if}
</div>

<style>
    .widget-loader {
        width: 100%;
        height: 100%;
        overflow: hidden;
    }

    .loading,
    .error {
        width: 100%;
        height: 100%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 0.8rem;
        color: var(--text-secondary);
        background: rgba(0, 0, 0, 0.2);
        border-radius: 8px;
    }

    .error {
        color: #ef4444;
        border: 1px solid rgba(239, 68, 68, 0.2);
    }
</style>
