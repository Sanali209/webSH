<script lang="ts">
  import { notifications } from '$lib/stores/notifications';
  import { flip } from 'svelte/animate';
  import { fade } from 'svelte/transition';
</script>

<div class="fixed bottom-4 right-4 z-50 flex flex-col gap-2 pointer-events-none">
  {#each $notifications as toast (toast.id)}
    <div
      animate:flip
      transition:fade
      class="pointer-events-auto p-4 rounded-md shadow-lg text-white max-w-sm break-words
        {toast.severity === 'info' ? 'bg-surface-500' :
         toast.severity === 'warning' ? 'bg-warning-500' :
         'bg-error-500'}"
    >
      <div class="font-bold capitalize mb-1">{toast.severity}</div>
      <div>{toast.message}</div>
    </div>
  {/each}
</div>
