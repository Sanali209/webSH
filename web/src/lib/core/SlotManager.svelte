<script lang="ts">
  /**
   * SlotManager - Manages plugin slots for dynamic component rendering
   * 
   * Allows plugins to register components that should be rendered in specific
   * UI slots (e.g., system_tray, context_menu, toolbar, etc.)
   */
  import { onMount } from 'svelte';
  import { moduleLoader, type PluginModule } from './module_loader';

  export let slotName: string;
  export let context: any = {}; // Context data passed to slot components

  let components: Array<{ 
    pluginId: string; 
    component: any; 
    props?: any;
  }> = [];
  let error: string = '';
  let loading: boolean = true;

  async function loadSlotComponents() {
    loading = true;
    error = '';
    
    try {
      // Ensure module loader is initialized
      if (!moduleLoader.isInitialized()) {
        await moduleLoader.init();
      }

      const plugins = moduleLoader.getActivePlugins();
      const slotComponents: typeof components = [];

      for (const plugin of plugins) {
        if (plugin.module && plugin.module.default) {
          const pluginExport = plugin.module.default;
          
          // Check if plugin exports slot configuration
          if (pluginExport.slots && pluginExport.slots[slotName]) {
            const slotConfig = pluginExport.slots[slotName];
            
            slotComponents.push({
              pluginId: plugin.id,
              component: slotConfig.component,
              props: slotConfig.props || {},
            });
          }
        }
      }

      components = slotComponents;
    } catch (e: any) {
      error = `Failed to load slot components: ${e.message}`;
      console.error(error, e);
    } finally {
      loading = false;
    }
  }

  onMount(async () => {
    await loadSlotComponents();
  });

  // Expose reload function
  export async function reload() {
    await loadSlotComponents();
  }
</script>

{#if loading}
  <div class="slot-manager-loading">
    <!-- Optional loading indicator -->
  </div>
{:else if error}
  <div class="slot-manager-error text-error-500 text-xs">
    {error}
  </div>
{:else if components.length > 0}
  <div class="slot-manager-content slot-{slotName}">
    {#each components as item (item.pluginId)}
      <div class="slot-item" data-plugin-id={item.pluginId}>
        <svelte:component this={item.component} {...item.props} context={context} />
      </div>
    {/each}
  </div>
{:else}
  <!-- Empty slot, render nothing -->
{/if}

<style>
  .slot-manager-content {
    display: contents;
  }

  .slot-item {
    display: contents;
  }

  /* Specific slot layouts */
  .slot-system_tray {
    display: flex;
    gap: 0.5rem;
    align-items: center;
  }

  .slot-context_menu {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
</style>
