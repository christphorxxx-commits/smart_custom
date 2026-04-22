<template>
  <div
    class="flow-canvas"
    @drop="handleDrop"
    @dragover.prevent="handleDragOver"
    @mousedown="handleCanvasMouseDown"
    @mousemove="handleMouseMove"
    @mouseup="handleMouseUp"
    @click="handleCanvasClick"
    @wheel.prevent="handleWheel"
  >
    <div
      class="canvas-content"
      :style="canvasTransform"
    >
      <!-- Grid background -->
      <svg class="grid-bg" :width="gridSize * 100" :height="gridSize * 100">
        <pattern
          id="grid"
          :width="gridSize"
          :height="gridSize"
          patternUnits="userSpaceOnUse"
        >
          <path
            :d="`M ${gridSize} 0 L 0 0 0 ${gridSize}`"
            fill="none"
            stroke="#e5e7eb"
            stroke-width="1"
          />
        </pattern>
        <rect width="100%" height="100%" fill="url(#grid)" />
      </svg>

      <!-- Nodes layer -->
      <div class="nodes-layer">
        <NodeComponent
          v-for="node in (Array.isArray(nodes?.value) ? nodes.value : Array.isArray(nodes) ? nodes : []).filter(n => n != null)"
          :key="node.id"
          :node="node"
          @mousedown="handleNodeMouseDown"
          @click="handleNodeClick"
        >
          <!-- Node preview content -->
          <template v-if="node.type === 'start'">
            <div>开始节点</div>
          </template>
          <template v-else-if="node.type === 'llm'">
            <div>{{ node.data?.model || node.config?.model || 'LLM' }}</div>
          </template>
          <template v-else-if="node.type === 'prompt'">
            <div>提示词模板</div>
          </template>
          <template v-else-if="node.type === 'if'">
            <div>条件判断</div>
          </template>
          <template v-else-if="node.type === 'code'">
            <div>代码执行</div>
          </template>
          <template v-else-if="node.type === 'dataset'">
            <div>数据集检索</div>
          </template>
          <template v-else-if="node.type === 'endpoint'">
            <div>输出结束</div>
          </template>
        </NodeComponent>
      </div>

      <!-- Connections layer (SVG) - must be on top of nodes but not block mouse events -->
      <svg class="connections-layer" :width="svgWidth" :height="svgHeight">
        <ConnectionLine
          :connections="connections?.value || connections"
          :selectedConnectionId="selectedConnectionId?.value || selectedConnectionId"
          :isDrawingConnection="isDrawingConnection?.value || false"
          :connectionStart="connectionStart?.value || connectionStart"
          :connectionCurrentMouse="connectionCurrentMouse?.value || connectionCurrentMouse"
          @select-connection="selectConnection"
        />
      </svg>
    </div>
  </div>
</template>

<script setup>
import { ref, inject, computed } from 'vue'
import NodeComponent from './NodeComponent.vue'
import ConnectionLine from './ConnectionLine.vue'

const emit = defineEmits(['drop'])

// Inject dependencies and handle null cases
let nodes = inject('nodes')
let connections = inject('connections')
let viewport = inject('viewport')
let selectedNodeId = inject('selectedNodeId')
let selectedConnectionId = inject('selectedConnectionId')
let isDrawingConnection = inject('isDrawingConnection')
let connectionStart = inject('connectionStart')
let connectionCurrentMouse = inject('connectionCurrentMouse')
let addNode = inject('addNode')
let updateNodePosition = inject('updateNodePosition')
let selectNode = inject('selectNode')
let selectConnection = inject('selectConnection')
let clearSelection = inject('clearSelection')
let updateConnectionMouse = inject('updateConnectionMouse')
let cancelConnection = inject('cancelConnection')
let panView = inject('panView')
let zoomAt = inject('zoomAt')

// Fallback defaults if inject returns null
if (!nodes) nodes = ref([])
if (!connections) connections = ref([])
if (!viewport) viewport = { x: 0, y: 0, scale: 1 }
if (!selectedNodeId) selectedNodeId = ref(null)
if (!selectedConnectionId) selectedConnectionId = ref(null)
if (!isDrawingConnection) isDrawingConnection = ref(false)
if (!connectionStart) connectionStart = ref(null)
if (!connectionCurrentMouse) connectionCurrentMouse = ref({ x: 0, y: 0 })
if (!addNode) addNode = () => {}
if (!updateNodePosition) updateNodePosition = () => {}
if (!selectNode) selectNode = () => {}
if (!selectConnection) selectConnection = () => {}
if (!clearSelection) clearSelection = () => {}
if (!updateConnectionMouse) updateConnectionMouse = () => {}
if (!cancelConnection) cancelConnection = () => {}
if (!panView) panView = () => {}
if (!zoomAt) zoomAt = () => {}

// State for dragging
const isDraggingNode = ref(false)
const isPanning = ref(false)
const dragNode = ref(null)
const dragStart = ref({ x: 0, y: 0 })
const lastPan = ref({ x: 0, y: 0 })

const gridSize = 20

const canvasTransform = computed(() => {
  return {
    transform: `translate(${viewport.x}px, ${viewport.y}px) scale(${viewport.scale})`
  }
})

// Fixed SVG size - will be large enough for any panning
const svgWidth = 5000
const svgHeight = 4000

function handleDragOver(event) {
  event.dataTransfer.dropEffect = 'move'
}

function handleDrop(event) {
  const type = event.dataTransfer.getData('node-type')
  if (!type) return

  const rect = event.currentTarget.getBoundingClientRect()
  const x = (event.clientX - rect.left - viewport.x) / viewport.scale
  const y = (event.clientY - rect.top - viewport.y) / viewport.scale

  addNode(type, x - 90, y - 30)
}

function handleCanvasMouseDown(event) {
  // Only block if we clicked directly on a node - node will handle the event
  // Allow panning on background, grid, connections layer
  if (event.target.closest('.node')) {
    return
  }

  if (event.button === 1 || (event.button === 0)) {
    // Allow left click drag to pan canvas
    isPanning.value = true
    lastPan.value = { x: event.clientX, y: event.clientY }
    event.preventDefault()
    if (event.button === 0) {
      clearSelection()
      cancelConnection()
    }
  }
}

function handleCanvasClick(event) {
  if (event.target === event.currentTarget) {
    clearSelection()
    cancelConnection()
  }
}

function handleNodeMouseDown(event, node) {
  if (event.button !== 0) return

  isDraggingNode.value = true
  dragNode.value = node
  dragStart.value = {
    x: event.clientX,
    y: event.clientY,
    nodeX: node.x,
    nodeY: node.y
  }
  selectNode(node.id)
  event.preventDefault()
  event.stopPropagation()
}

function handleNodeClick(node) {
  selectNode(node.id)
}

function handleMouseMove(event) {
  if (isDraggingNode.value && dragNode.value) {
    const dx = (event.clientX - dragStart.value.x) / viewport.scale
    const dy = (event.clientY - dragStart.value.y) / viewport.scale
    const newX = dragStart.value.nodeX + dx
    const newY = dragStart.value.nodeY + dy
    updateNodePosition(dragNode.value.id, newX, newY)
  }

  if (isPanning.value) {
    const dx = event.clientX - lastPan.value.x
    const dy = event.clientY - lastPan.value.y
    panView(dx, dy)
    lastPan.value = { x: event.clientX, y: event.clientY }
  }

  if (isDrawingConnection.value) {
    const rect = event.currentTarget.getBoundingClientRect()
    const x = (event.clientX - rect.left - viewport.x) / viewport.scale
    const y = (event.clientY - rect.top - viewport.y) / viewport.scale
    updateConnectionMouse(x, y)
  }
}

function handleMouseUp() {
  if (isDrawingConnection.value) {
    cancelConnection()
  }
  isDraggingNode.value = false
  isPanning.value = false
  dragNode.value = null
}

function handleWheel(event) {
  const rect = event.currentTarget.getBoundingClientRect()
  const x = event.clientX - rect.left
  const y = event.clientY - rect.top
  const delta = event.deltaY > 0 ? -0.1 : 0.1
  zoomAt(x, y, delta)
}
</script>

<style scoped>
.flow-canvas {
  flex: 1;
  height: 100%;
  overflow: hidden;
  background: #f1f1f3;
  position: relative;
  cursor: grab;
}

.flow-canvas:active {
  cursor: grabbing;
}

.canvas-content {
  position: absolute;
  top: 0;
  left: 0;
  transform-origin: 0 0;
  will-change: transform;
}

.grid-bg {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}

.connections-layer {
  position: absolute;
  top: 0;
  left: 0;
  pointer-events: none;
}
/* Connection handles still need to be clickable */
.connections-layer .connection-handle {
  pointer-events: auto;
}

.nodes-layer {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: auto;
}
</style>
