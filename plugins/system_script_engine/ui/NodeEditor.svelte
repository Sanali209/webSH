<script>
  /**
   * Simple Visual Node Editor for Script Engine
   * 
   * Provides a canvas where users can:
   * - Add nodes from a palette
   * - Connect nodes to create workflows
   * - Execute workflows
   */
  import { onMount } from 'svelte';
  
  let nodes = [];
  let edges = [];
  let availableNodeTypes = [];
  let loading = true;
  let executing = false;
  let executionResult = null;
  let error = null;
  
  // Load available node types
  onMount(async () => {
    try {
      const response = await fetch('/api/plugins/system_script_engine/nodes');
      const data = await response.json();
      availableNodeTypes = data.nodes || [];
      loading = false;
    } catch (e) {
      error = `Failed to load nodes: ${e.message}`;
      loading = false;
    }
  });
  
  function addNode(nodeType) {
    const newNode = {
      id: `node_${Date.now()}`,
      type: nodeType.id,
      name: nodeType.name,
      config: {},
      position: { x: 100, y: 100 }
    };
    nodes = [...nodes, newNode];
  }
  
  function removeNode(nodeId) {
    nodes = nodes.filter(n => n.id !== nodeId);
    edges = edges.filter(e => e.from !== nodeId && e.to !== nodeId);
  }
  
  function addEdge(fromNode, fromPort, toNode, toPort) {
    const newEdge = {
      from: fromNode,
      to: toNode,
      fromPort: fromPort || 'output',
      toPort: toPort || 'input'
    };
    edges = [...edges, newEdge];
  }
  
  async function executeWorkflow() {
    executing = true;
    executionResult = null;
    error = null;
    
    const workflow = {
      name: "Test Workflow",
      nodes: nodes,
      edges: edges
    };
    
    try {
      const response = await fetch('/api/plugins/system_script_engine/run', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(workflow)
      });
      
      const result = await response.json();
      
      if (result.status === 'error') {
        error = result.error;
      } else {
        executionResult = result;
      }
    } catch (e) {
      error = `Execution failed: ${e.message}`;
    } finally {
      executing = false;
    }
  }
  
  function clearWorkflow() {
    nodes = [];
    edges = [];
    executionResult = null;
    error = null;
  }
</script>

<div class="script-engine">
  <h1>Workflow Editor</h1>
  
  {#if loading}
    <div class="loading">Loading workflow nodes...</div>
  {:else if error}
    <div class="error">{error}</div>
  {:else}
    <div class="editor-container">
      <!-- Node Palette -->
      <div class="node-palette">
        <h2>Available Nodes</h2>
        <div class="node-types">
          {#each availableNodeTypes as nodeType}
            <div class="node-type" on:click={() => addNode(nodeType)}>
              <div class="node-type-name">{nodeType.name}</div>
              <div class="node-type-desc">{nodeType.description}</div>
            </div>
          {/each}
        </div>
      </div>
      
      <!-- Canvas -->
      <div class="canvas-container">
        <div class="canvas-toolbar">
          <button on:click={executeWorkflow} disabled={executing || nodes.length === 0}>
            {executing ? 'Executing...' : 'Run Workflow'}
          </button>
          <button on:click={clearWorkflow}>Clear</button>
          <span class="node-count">{nodes.length} nodes, {edges.length} connections</span>
        </div>
        
        <div class="canvas">
          {#if nodes.length === 0}
            <div class="empty-state">
              <p>Click on nodes in the palette to add them to the workflow</p>
            </div>
          {/if}
          
          {#each nodes as node, i}
            <div class="node" style="top: {i * 120 + 50}px; left: 150px;">
              <div class="node-header">
                <span class="node-title">{node.name}</span>
                <button class="node-remove" on:click={() => removeNode(node.id)}>×</button>
              </div>
              <div class="node-body">
                <div class="node-id">{node.id}</div>
                <div class="node-type">{node.type}</div>
              </div>
            </div>
          {/each}
          
          <!-- Simple visualization of connections -->
          {#if edges.length > 0}
            <div class="edges-info">
              {edges.length} connection(s)
            </div>
          {/if}
        </div>
        
        <!-- Results Panel -->
        {#if executionResult}
          <div class="results-panel">
            <h3>Execution Results</h3>
            <div class="result-status" class:success={executionResult.status === 'success'}>
              Status: {executionResult.status}
            </div>
            <div class="result-duration">
              Duration: {executionResult.duration?.toFixed(3)}s
            </div>
            <details>
              <summary>Node Results ({Object.keys(executionResult.node_results || {}).length})</summary>
              <pre>{JSON.stringify(executionResult.node_results, null, 2)}</pre>
            </details>
          </div>
        {/if}
        
        {#if error}
          <div class="error-panel">
            <h3>Error</h3>
            <div class="error-message">{error}</div>
          </div>
        {/if}
      </div>
    </div>
  {/if}
</div>

<style>
  .script-engine {
    padding: 20px;
    height: 100vh;
    display: flex;
    flex-direction: column;
  }
  
  h1 {
    margin: 0 0 20px 0;
    font-size: 24px;
  }
  
  .loading, .error {
    padding: 20px;
    text-align: center;
  }
  
  .error {
    background: #fee;
    color: #c00;
    border-radius: 4px;
  }
  
  .editor-container {
    display: flex;
    gap: 20px;
    flex: 1;
    overflow: hidden;
  }
  
  .node-palette {
    width: 250px;
    background: #f5f5f5;
    border-radius: 8px;
    padding: 15px;
    overflow-y: auto;
  }
  
  .node-palette h2 {
    margin: 0 0 15px 0;
    font-size: 16px;
  }
  
  .node-types {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .node-type {
    padding: 10px;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
    cursor: pointer;
    transition: all 0.2s;
  }
  
  .node-type:hover {
    border-color: #007bff;
    box-shadow: 0 2px 8px rgba(0,123,255,0.2);
  }
  
  .node-type-name {
    font-weight: 600;
    margin-bottom: 4px;
  }
  
  .node-type-desc {
    font-size: 12px;
    color: #666;
  }
  
  .canvas-container {
    flex: 1;
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .canvas-toolbar {
    display: flex;
    gap: 10px;
    align-items: center;
    padding: 10px;
    background: #f5f5f5;
    border-radius: 4px;
  }
  
  .canvas-toolbar button {
    padding: 8px 16px;
    border: none;
    border-radius: 4px;
    background: #007bff;
    color: white;
    cursor: pointer;
    font-size: 14px;
  }
  
  .canvas-toolbar button:hover:not(:disabled) {
    background: #0056b3;
  }
  
  .canvas-toolbar button:disabled {
    background: #ccc;
    cursor: not-allowed;
  }
  
  .node-count {
    margin-left: auto;
    font-size: 14px;
    color: #666;
  }
  
  .canvas {
    flex: 1;
    background: white;
    border: 2px solid #ddd;
    border-radius: 8px;
    position: relative;
    overflow: auto;
  }
  
  .empty-state {
    position: absolute;
    top: 50%;
    left: 50%;
    transform: translate(-50%, -50%);
    text-align: center;
    color: #999;
  }
  
  .node {
    position: absolute;
    min-width: 200px;
    background: white;
    border: 2px solid #007bff;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  }
  
  .node-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 10px;
    background: #007bff;
    color: white;
    border-radius: 6px 6px 0 0;
  }
  
  .node-title {
    font-weight: 600;
  }
  
  .node-remove {
    background: none;
    border: none;
    color: white;
    font-size: 20px;
    cursor: pointer;
    padding: 0 5px;
  }
  
  .node-body {
    padding: 10px;
  }
  
  .node-id, .node-type {
    font-size: 12px;
    color: #666;
    margin-bottom: 4px;
  }
  
  .edges-info {
    position: absolute;
    top: 10px;
    right: 10px;
    padding: 8px 12px;
    background: #e3f2fd;
    border-radius: 4px;
    font-size: 12px;
    color: #1976d2;
  }
  
  .results-panel, .error-panel {
    padding: 15px;
    background: #f5f5f5;
    border-radius: 8px;
    margin-top: 10px;
  }
  
  .results-panel h3, .error-panel h3 {
    margin: 0 0 10px 0;
    font-size: 16px;
  }
  
  .result-status {
    padding: 8px;
    border-radius: 4px;
    margin-bottom: 8px;
    background: #ffc107;
  }
  
  .result-status.success {
    background: #4caf50;
    color: white;
  }
  
  .result-duration {
    font-size: 14px;
    color: #666;
    margin-bottom: 10px;
  }
  
  details {
    margin-top: 10px;
  }
  
  summary {
    cursor: pointer;
    font-weight: 600;
    margin-bottom: 8px;
  }
  
  pre {
    background: white;
    padding: 10px;
    border-radius: 4px;
    overflow-x: auto;
    font-size: 12px;
  }
  
  .error-panel {
    background: #fee;
  }
  
  .error-message {
    color: #c00;
    font-family: monospace;
    white-space: pre-wrap;
  }
</style>
