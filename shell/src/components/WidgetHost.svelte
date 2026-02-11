<script lang="ts">
  import { onMount, onDestroy } from 'svelte';
  import { createConnection, type WidgetConnection } from '../lib/services/widgetBridge';

  let { src } = $props();

  let iframeElement: HTMLIFrameElement = $state(null);
  let connection: WidgetConnection | null = null;

  // Mock methods for now, or use real services if available
  const methods = {
    getApiToken: () => 'mock-api-token',
    getDesktopId: () => 'mock-desktop-id',
    emitEvent: (name: string, data: any) => {
      console.log('Event from widget:', name, data);
    }
  };

  onMount(() => {
    if (iframeElement) {
      connection = createConnection(iframeElement, methods);
      connection.promise.catch((err) => {
          console.error('Failed to connect to widget:', err);
      });
    }
  });

  onDestroy(() => {
    if (connection) {
      connection.destroy();
    }
  });
</script>

<iframe
  bind:this={iframeElement}
  {src}
  sandbox="allow-scripts allow-popups"
  title="Widget"
  style="width: 100%; height: 100%; border: none;"
></iframe>
