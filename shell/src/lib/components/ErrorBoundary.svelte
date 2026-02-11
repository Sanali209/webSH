<script>
    let { children } = $props();
</script>

<!-- svelte:boundary is not available in the installed Svelte 5 version.
     Falling back to simple render. Future update should enable <svelte:boundary> -->
<div class="error-boundary-wrapper">
    {@render children()}
</div>

<style>
    .error-boundary-wrapper {
        display: contents;
    }
</style>
