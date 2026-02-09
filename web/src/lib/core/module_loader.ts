/**
 * ModuleLoader - Dynamically loads plugin UI modules
 * 
 * Fetches the list of active plugins from the backend API
 * and dynamically imports their UI components from served static paths.
 */

export interface PluginManifest {
  id: string;
  name: string;
  version: string;
  description: string;
  status: 'active' | 'inactive';
}

export interface PluginModule {
  id: string;
  manifest: PluginManifest;
  module?: any; // The dynamically imported module
  error?: string;
}

class ModuleLoader {
  private plugins: Map<string, PluginModule> = new Map();
  private initialized: boolean = false;

  /**
   * Initialize the module loader by fetching active plugins
   */
  async init(): Promise<void> {
    if (this.initialized) {
      return;
    }

    try {
      const response = await fetch('/api/plugins');
      if (!response.ok) {
        throw new Error(`Failed to fetch plugins: ${response.statusText}`);
      }

      const manifests: PluginManifest[] = await response.json();
      
      // Load each active plugin's UI module
      for (const manifest of manifests) {
        if (manifest.status === 'active') {
          await this.loadPlugin(manifest);
        }
      }

      this.initialized = true;
    } catch (error) {
      console.error('Failed to initialize ModuleLoader:', error);
      throw error;
    }
  }

  /**
   * Dynamically load a plugin's UI module
   */
  private async loadPlugin(manifest: PluginManifest): Promise<void> {
    const pluginModule: PluginModule = {
      id: manifest.id,
      manifest,
    };

    try {
      // Attempt to dynamically import the plugin's UI entry point
      const modulePath = `/plugins/${manifest.id}/ui/index.js`;
      const module = await import(/* @vite-ignore */ modulePath);
      pluginModule.module = module;
      console.log(`Successfully loaded plugin UI: ${manifest.id}`);
    } catch (error) {
      // Plugin may not have a UI component, which is fine
      pluginModule.error = `Failed to load UI module: ${error}`;
      console.warn(`Plugin ${manifest.id} has no UI module or failed to load:`, error);
    }

    this.plugins.set(manifest.id, pluginModule);
  }

  /**
   * Get a loaded plugin module by ID
   */
  getPlugin(id: string): PluginModule | undefined {
    return this.plugins.get(id);
  }

  /**
   * Get all loaded plugins
   */
  getAllPlugins(): PluginModule[] {
    return Array.from(this.plugins.values());
  }

  /**
   * Get all active plugins (successfully loaded with a module)
   */
  getActivePlugins(): PluginModule[] {
    return this.getAllPlugins().filter(p => p.module && !p.error);
  }

  /**
   * Check if the loader is initialized
   */
  isInitialized(): boolean {
    return this.initialized;
  }

  /**
   * Reload a specific plugin
   */
  async reloadPlugin(id: string): Promise<void> {
    const pluginModule = this.plugins.get(id);
    if (!pluginModule) {
      throw new Error(`Plugin ${id} not found`);
    }

    await this.loadPlugin(pluginModule.manifest);
  }

  /**
   * Reload all plugins
   */
  async reload(): Promise<void> {
    this.initialized = false;
    this.plugins.clear();
    await this.init();
  }
}

// Export singleton instance
export const moduleLoader = new ModuleLoader();
