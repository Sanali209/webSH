<script>
    import { onMount, onDestroy } from "svelte";
    import * as d3 from "d3";
    import JSONTree from "svelte-json-tree";
    import { X, Play, Pause, Trash2 } from "lucide-svelte";

    let socket;
    let isPaused = $state(false);
    let nodes = $state([]);
    let links = $state([]);
    let selectedNode = $state(null);
    let svg;
    let simulation;
    let width = $state(800);
    let height = $state(600);
    let container;

    // Scale for coloring nodes by status
    const colorScale = d3
        .scaleOrdinal()
        .domain(["OK", "ERROR", "UNSET"])
        .range(["#4ade80", "#f87171", "#94a3b8"]);

    onMount(() => {
        connect();
        initGraph();

        const resizeObserver = new ResizeObserver((entries) => {
            if (entries[0]) {
                width = entries[0].contentRect.width;
                height = entries[0].contentRect.height;
                if (simulation) {
                    simulation.force(
                        "center",
                        d3.forceCenter(width / 2, height / 2),
                    );
                    simulation.alpha(1).restart();
                }
            }
        });

        if (container) resizeObserver.observe(container);

        return () => {
            if (socket) socket.close();
            resizeObserver.disconnect();
            if (simulation) simulation.stop();
        };
    });

    function connect() {
        const protocol = window.location.protocol === "https:" ? "wss:" : "ws:";
        // Connect to debug stream
        const wsUrl = `${protocol}//${window.location.host}/api/v1/debug/stream`;

        socket = new WebSocket(wsUrl);

        socket.onmessage = (event) => {
            if (isPaused) return;
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === "span") {
                    handleSpan(msg.data);
                }
            } catch (e) {
                console.error("Inspector Error:", e);
            }
        };

        socket.onclose = () => {
            console.log("Inspector disconnected");
        };
    }

    function handleSpan(span) {
        // Add Node
        const existingNode = nodes.find((n) => n.id === span.span_id);
        if (!existingNode) {
            const newNode = {
                id: span.span_id,
                label: span.name,
                data: span,
                x: width / 2 + (Math.random() - 0.5) * 50,
                y: height / 2 + (Math.random() - 0.5) * 50,
            };
            nodes.push(newNode);

            // Add Link if parent exists
            if (span.parent_id) {
                // Check if parent node exists (it might verify out of order)
                // If not, we create a placeholder or wait.
                // For simplicity, we only link if parent is known, or we create a ghost parent.
                let parent = nodes.find((n) => n.id === span.parent_id);
                if (!parent) {
                    // Create ghost parent
                    parent = {
                        id: span.parent_id,
                        label: "Unknown Parent",
                        isGhost: true,
                        x: width / 2,
                        y: height / 2,
                    };
                    nodes.push(parent);
                }

                links.push({
                    source: parent.id,
                    target: newNode.id,
                });
            }

            updateGraph();
        } else {
            // Update existing node (e.g. status change)
            existingNode.data = span;
            // If it was ghost, make it real
            if (existingNode.isGhost) {
                existingNode.isGhost = false;
                existingNode.label = span.name;
            }
        }
    }

    function initGraph() {
        simulation = d3
            .forceSimulation(nodes)
            .force(
                "link",
                d3
                    .forceLink(links)
                    .id((d) => d.id)
                    .distance(100),
            )
            .force("charge", d3.forceManyBody().strength(-300))
            .force("center", d3.forceCenter(width / 2, height / 2))
            .on("tick", ticked);
    }

    function updateGraph() {
        if (!simulation) return;

        simulation.nodes(nodes);
        simulation.force("link").links(links);
        simulation.alpha(1).restart();
    }

    function ticked() {
        if (!svg) return;

        const link = d3
            .select(svg)
            .select(".links")
            .selectAll("line")
            .data(links)
            .join("line")
            .attr("stroke", "#999")
            .attr("stroke-opacity", 0.6)
            .attr("stroke-width", 1.5)
            .attr("x1", (d) => d.source.x)
            .attr("y1", (d) => d.source.y)
            .attr("x2", (d) => d.target.x)
            .attr("y2", (d) => d.target.y);

        const node = d3
            .select(svg)
            .select(".nodes")
            .selectAll("g")
            .data(nodes)
            .join("g")
            .call(
                d3
                    .drag()
                    .on("start", dragstarted)
                    .on("drag", dragged)
                    .on("end", dragended),
            );

        node.selectAll("circle")
            .data((d) => [d])
            .join("circle")
            .attr("r", 5)
            .attr("fill", (d) =>
                d.isGhost ? "#666" : colorScale(d.data?.status || "UNSET"),
            );

        node.selectAll("text")
            .data((d) => [d])
            .join("text")
            .text((d) => d.label)
            .attr("x", 8)
            .attr("y", 3)
            .attr("fill", "#ccc")
            .style("font-size", "10px")
            .style("pointer-events", "none");

        node.attr("transform", (d) => `translate(${d.x},${d.y})`).on(
            "click",
            (e, d) => {
                selectedNode = d;
            },
        );
    }

    function dragstarted(event, d) {
        if (!event.active) simulation.alphaTarget(0.3).restart();
        d.fx = d.x;
        d.fy = d.y;
    }

    function dragged(event, d) {
        d.fx = event.x;
        d.fy = event.y;
    }

    function dragended(event, d) {
        if (!event.active) simulation.alphaTarget(0);
        d.fx = null;
        d.fy = null;
    }

    function clearGraph() {
        nodes = [];
        links = [];
        selectedNode = null;
        updateGraph();
    }
</script>

<div class="inspector-container">
    <div class="sidebar">
        <div class="toolbar">
            <button
                onclick={() => (isPaused = !isPaused)}
                title={isPaused ? "Resume" : "Pause"}
            >
                {#if isPaused}<Play size={16} />{:else}<Pause size={16} />{/if}
            </button>
            <button onclick={clearGraph} title="Clear">
                <Trash2 size={16} />
            </button>
        </div>
        <div class="node-details">
            {#if selectedNode}
                <h3>{selectedNode.label}</h3>
                <div class="json-tree">
                    <JSONTree value={selectedNode.data} />
                </div>
            {:else}
                <p class="placeholder">Select a node to view details</p>
            {/if}
        </div>
    </div>

    <div class="graph-area" bind:this={container}>
        <svg bind:this={svg} {width} {height}>
            <g class="links"></g>
            <g class="nodes"></g>
        </svg>
    </div>
</div>

<style>
    .inspector-container {
        display: flex;
        width: 100%;
        height: 100%;
        background: #0f172a;
        color: #f8fafc;
    }

    .sidebar {
        width: 300px;
        border-right: 1px solid #334155;
        display: flex;
        flex-direction: column;
        background: #1e293b;
    }

    .toolbar {
        padding: 0.5rem;
        border-bottom: 1px solid #334155;
        display: flex;
        gap: 0.5rem;
    }

    .toolbar button {
        background: #334155;
        border: none;
        color: white;
        padding: 4px;
        border-radius: 4px;
        cursor: pointer;
    }

    .toolbar button:hover {
        background: #475569;
    }

    .node-details {
        flex: 1;
        overflow-y: auto;
        padding: 1rem;
    }

    .node-details h3 {
        margin-top: 0;
        font-size: 1rem;
        color: #60a5fa;
        word-break: break-all;
    }

    .graph-area {
        flex: 1;
        position: relative;
        overflow: hidden;
    }

    .json-tree {
        font-size: 0.85rem;
    }

    .placeholder {
        color: #64748b;
        font-style: italic;
        text-align: center;
        margin-top: 2rem;
    }
</style>
