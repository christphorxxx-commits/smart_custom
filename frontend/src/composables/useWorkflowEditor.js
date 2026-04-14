import { ref, reactive, computed } from 'vue'

/**
 * Composable for Workflow Editor core logic
 */
export function useWorkflowEditor() {
  // Nodes and connections state
  const nodes = ref([])
  const connections = ref([])

  // Viewport transform
  const viewport = reactive({
    x: 0,
    y: 0,
    scale: 1
  })

  // Selection state
  const selectedNodeId = ref(null)
  const selectedConnectionId = ref(null)

  // Connection drawing state
  const isDrawingConnection = ref(false)
  const connectionStart = ref(null)
  const connectionCurrentMouse = ref({ x: 0, y: 0 })

  // Node ID counter
  let nodeIdCounter = 0
  let connectionIdCounter = 0

  // Get selected node
  const selectedNode = computed(() => {
    return nodes.value.find(n => n.id === selectedNodeId.value)
  })

  // Get selected connection
  const selectedConnection = computed(() => {
    return connections.value.find(c => c.id === selectedConnectionId.value)
  })

  // Generate unique node ID
  function generateNodeId() {
    return `node_${++nodeIdCounter}`
  }

  // Generate unique connection ID
  function generateConnectionId() {
    return `conn_${++connectionIdCounter}`
  }

  // Add a new node
  function addNode(type, x, y) {
    const node = {
      id: generateNodeId(),
      type,
      x,
      y,
      data: getDefaultNodeData(type)
    }
    nodes.value.push(node)
    return node
  }

  // Get default data for node type
  function getDefaultNodeData(type) {
    switch (type) {
      case 'start':
        return {
          title: 'Start',
          inputVariable: ''
        }
      case 'llm':
        return {
          title: 'LLM',
          model: 'gpt-4o',
          systemPrompt: 'You are a helpful assistant.',
          temperature: 0.7,
          maxTokens: 2048
        }
      case 'prompt':
        return {
          title: 'Prompt',
          template: ''
        }
      case 'code':
        return {
          title: 'Code',
          code: ''
        }
      case 'if':
        return {
          title: 'Condition',
          condition: 'true\nfalse',
          branches: ['true', 'false']
        }
      case 'dataset':
        return {
          title: 'Dataset',
          collection: ''
        }
      case 'endpoint':
        return {
          title: 'End',
          output: ''
        }
      default:
        return {
          title: type
        }
    }
  }

  // Get node color by type
  function getNodeColor(type) {
    const colorMap = {
      start: '#10b981',     // green
      endpoint: '#10b981',  // green
      llm: '#6B4EED',       // purple (primary)
      prompt: '#6B4EED',    // purple
      code: '#f97316',      // orange
      if: '#f97316',        // orange
      dataset: '#3b82f6'    // blue
    }
    return colorMap[type] || '#6B4EED'
  }

  // Update node position
  function updateNodePosition(nodeId, x, y) {
    const node = nodes.value.find(n => n.id === nodeId)
    if (node) {
      node.x = x
      node.y = y
    }
  }

  // Update node data
  function updateNodeData(nodeId, data) {
    const node = nodes.value.find(n => n.id === nodeId)
    if (node) {
      node.data = { ...node.data, ...data }
    }
  }

  // Delete node
  function deleteNode(nodeId) {
    // Remove connections connected to this node
    connections.value = connections.value.filter(
      conn => conn.sourceNodeId !== nodeId && conn.targetNodeId !== nodeId
    )
    // Remove node
    nodes.value = nodes.value.filter(n => n.id !== nodeId)
    // Clear selection
    if (selectedNodeId.value === nodeId) {
      selectedNodeId.value = null
    }
  }

  // Delete connection
  function deleteConnection(connectionId) {
    connections.value = connections.value.filter(c => c.id !== connectionId)
    if (selectedConnectionId.value === connectionId) {
      selectedConnectionId.value = null
    }
  }

  // Delete selected (node or connection)
  function deleteSelected() {
    if (selectedNodeId.value) {
      deleteNode(selectedNodeId.value)
    } else if (selectedConnectionId.value) {
      deleteConnection(selectedConnectionId.value)
    }
  }

  // Select node
  function selectNode(nodeId) {
    selectedNodeId.value = nodeId
    selectedConnectionId.value = null
  }

  // Select connection
  function selectConnection(connectionId) {
    selectedConnectionId.value = connectionId
    selectedNodeId.value = null
  }

  // Clear selection
  function clearSelection() {
    selectedNodeId.value = null
    selectedConnectionId.value = null
  }

  // Start connection drawing
  function startConnection(sourceNodeId, sourcePort) {
    isDrawingConnection.value = true
    connectionStart.value = { nodeId: sourceNodeId, port: sourcePort }
  }

  // Update connection mouse position during drawing
  function updateConnectionMouse(x, y) {
    connectionCurrentMouse.value = { x, y }
  }

  // Complete connection drawing
  function completeConnection(targetNodeId, targetPort) {
    if (!isDrawingConnection.value || !connectionStart.value) {
      return
    }

    // Don't connect to self
    if (connectionStart.value.nodeId === targetNodeId) {
      cancelConnection()
      return
    }

    // Check if connection already exists
    const exists = connections.value.some(
      conn =>
        (conn.sourceNodeId === connectionStart.value.nodeId &&
         conn.targetNodeId === targetNodeId) ||
        (conn.sourceNodeId === targetNodeId &&
         conn.targetNodeId === connectionStart.value.nodeId)
    )

    if (!exists) {
      connections.value.push({
        id: generateConnectionId(),
        sourceNodeId: connectionStart.value.nodeId,
        sourcePort: connectionStart.value.port,
        targetNodeId,
        targetPort
      })
    }

    cancelConnection()
  }

  // Cancel connection drawing
  function cancelConnection() {
    isDrawingConnection.value = false
    connectionStart.value = null
    connectionCurrentMouse.value = { x: 0, y: 0 }
  }

  // Get node center position for connection calculation
  function getNodeCenter(node) {
    // Node is 180px wide, 60px tall approx
    return {
      x: node.x + 90,
      y: node.y + 30
    }
  }

  // Get port position
  function getPortPosition(node, port) {
    // port is 'input', 'output', or 'output_0', 'output_1', etc.
    const isInput = port === 'input'

    if (node.type === 'if' && node.data.branches && port.startsWith('output_')) {
      // Multiple output ports for if node
      const index = parseInt(port.split('_')[1], 10)
      const nodeHeight = Math.max(60, 30 + (node.data.branches.length * 26))
      const step = nodeHeight / (node.data.branches.length + 1)
      const y = node.y + step * (index + 1)
      return { x: node.x + 180, y }
    }

    // Single output port
    const center = getNodeCenter(node)
    if (!isInput) {
      return { x: node.x + 180, y: center.y }
    } else {
      return { x: node.x, y: center.y }
    }
  }

  // Pan viewport
  function panView(dx, dy) {
    viewport.x += dx / viewport.scale
    viewport.y += dy / viewport.scale
  }

  // Zoom viewport
  function zoomAt(x, y, delta) {
    const prevScale = viewport.scale
    const newScale = Math.min(2, Math.max(0.5, viewport.scale + delta * 0.1))

    // Adjust pan to zoom at mouse position
    const rectX = x - viewport.x * prevScale
    const rectY = y - viewport.y * prevScale
    viewport.scale = newScale
    viewport.x = (x - rectX) / newScale
    viewport.y = (y - rectY) / newScale
  }

  // Reset view
  function resetView() {
    viewport.x = 0
    viewport.y = 0
    viewport.scale = 1
  }

  // Serialize workflow
  function serialize() {
    return JSON.stringify({
      nodes: nodes.value,
      connections: connections.value,
      version: 1
    }, null, 2)
  }

  // Deserialize workflow
  // Supports both editor format and backend default.json format
  function deserialize(data) {
    try {
      const parsed = typeof data === 'string' ? JSON.parse(data) : data
      clearAll()

      // Check if it's backend format (nodes + edges)
      if (parsed.nodes && parsed.edges) {
        // Backend format: convert to editor format
        // Do simple auto-layout
        const convertedNodes = convertBackendNodes(parsed.nodes)
        const convertedConnections = convertBackendEdges(parsed.edges)
        nodes.value = convertedNodes
        connections.value = convertedConnections
      } else if (parsed.nodes && parsed.connections) {
        // Editor format
        nodes.value = parsed.nodes.filter(n => n != null)
        connections.value = parsed.connections.filter(c => c != null)
      } else {
        nodes.value = []
        connections.value = []
      }

      // Update counters based on max ID found
      if (nodes.value.length > 0) {
        let maxId = 0
        nodes.value.forEach(n => {
          const numMatch = n.id.match(/\d+/)
          if (numMatch) {
            const num = parseInt(numMatch[0], 10)
            if (num > maxId) maxId = num
          }
        })
        nodeIdCounter = maxId
      }

      if (connections.value.length > 0) {
        let maxId = 0
        connections.value.forEach(c => {
          const numMatch = c.id.match(/\d+/)
          if (numMatch) {
            const num = parseInt(numMatch[0], 10)
            if (num > maxId) maxId = num
          }
        })
        connectionIdCounter = maxId
      }

      return true
    } catch (e) {
      console.error('Failed to deserialize workflow:', e)
      return false
    }
  }

  // Convert backend nodes format to editor format with auto layout
  function convertBackendNodes(backendNodes) {
    const nodeWidth = 200
    const horizontalSpacing = 120
    const startX = 100

    // Do simple sequential horizontal layout by order in JSON
    return backendNodes.filter(node => node != null).map((node, index) => {
      let editorType = node.type
      // Map backend node types to editor types
      if (editorType === 'router') editorType = 'if'
      if (editorType === 'end') editorType = 'endpoint'

      const x = startX + index * (nodeWidth + horizontalSpacing)
      const y = 150

      const defaultData = getDefaultNodeData(editorType)
      let nodeData = { ...defaultData, ...node.config }

      // Special mappings
      if (editorType === 'llm' && node.config && node.config.prompt) {
        nodeData.systemPrompt = node.config.prompt
      }
      if (editorType === 'if' && node.config && node.config.options) {
        nodeData.condition = node.config.options.join('\n')
        nodeData.branches = node.config.options
      }
      if (node.config && node.config.title) {
        nodeData.title = node.config.title
      }

      return {
        id: node.id,
        type: editorType,
        x,
        y,
        data: nodeData
      }
    })
  }

  // Convert backend edges to editor connections
  function convertBackendEdges(backendEdges) {
    return backendEdges.filter(edge => edge != null).map((edge, index) => ({
      id: `conn_${index}`,
      sourceNodeId: edge.source,
      sourcePort: 'output',
      targetNodeId: edge.target,
      targetPort: 'input'
    }))
  }

  function getDefaultTitle(type) {
    const titles = {
      start: '开始',
      endpoint: '结束',
      if: '条件路由',
      llm: '大模型',
      prompt: '提示词',
      code: '代码执行',
      dataset: '数据集'
    }
    return titles[type] || type
  }

  // Clear everything
  function clearAll() {
    nodes.value = []
    connections.value = []
    selectedNodeId.value = null
    selectedConnectionId.value = null
    nodeIdCounter = 0
    connectionIdCounter = 0
  }

  return {
    // State
    nodes,
    connections,
    viewport,
    selectedNodeId,
    selectedConnectionId,
    selectedNode,
    selectedConnection,
    isDrawingConnection,
    connectionStart,
    connectionCurrentMouse,

    // Methods
    addNode,
    updateNodePosition,
    updateNodeData,
    deleteNode,
    deleteConnection,
    deleteSelected,
    selectNode,
    selectConnection,
    clearSelection,
    startConnection,
    updateConnectionMouse,
    completeConnection,
    cancelConnection,
    getNodeColor,
    getPortPosition,
    panView,
    zoomAt,
    resetView,
    serialize,
    deserialize,
    clearAll
  }
}
