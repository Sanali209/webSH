<script>
    import { registry } from "../../lib/registry.svelte.js";
    import { Activity } from "lucide-svelte";
    import InspectorIcon from "./InspectorIcon.svelte";

    // Register on init
    $effect(() => {
        const item = {
            id: "system-inspector",
            component: InspectorIcon,
            priority: 10,
            props: {},
        };
        registry.register("sidebar.bottom", item);

        return () => {
            registry.unregister("sidebar.bottom", "system-inspector");
        };
    });
</script>

<!-- Implicit UI (none, as it injects into slot) -->
