<template>
  <g>
    <!-- Existing connections -->
    <g
      v-for="conn in connections"
      :key="conn.id"
      @click.stop="handleConnectionClick(conn.id)"
    >
      <path
        :d="getConnectionPath(conn)"
        :stroke="conn.id === selectedConnectionId ? '#6B4EED' : '#999'"
        :stroke-width="conn.id === selectedConnectionId ? '3' : '2'"
        fill="none"
        stroke-linecap="round"
        class="connection-path"
      />
      <circle
        :cx="getMidPoint(conn).x"
        :cy="getMidPoint(conn).y"
        r="4"
        :fill="conn.id === selectedConnectionId ? '#6B4EED' : '#999'"
        class="connection-handle"
      />
    </g>

    <!-- Temporary connection being drawn -->
    <path
      v-if="isDrawingConnection && connectionStart"
      :d="getTemporaryPath()"
      stroke="#6B4EED"
      stroke-width="2"
      fill="none"
      stroke-linecap="round"
      stroke-dasharray="5,5"
    />
  </g>
</template>

<script setup>
import { inject } from 'vue'

const props = defineProps({
  connections: Array,
  selectedConnectionId: String,
  isDrawingConnection: Boolean,
  connectionStart: Object,
  connectionCurrentMouse: Object
})

const emit = defineEmits(['select-connection'])

const nodes = inject('nodes')
const getPortPosition = inject('getPortPosition')
const selectConnection = inject('selectConnection')

function handleConnectionClick(connectionId) {
  selectConnection(connectionId)
}

function getConnectionPath(connection) {
  const sourceNode = nodes.value.find(n => n.id === connection.sourceNodeId)
  const targetNode = nodes.value.find(n => n.id === connection.targetNodeId)

  if (!sourceNode || !targetNode) return ''

  const sourcePos = getPortPosition(sourceNode, connection.sourcePort)
  const targetPos = getPortPosition(targetNode, connection.targetPort)

  // Use cubic bezier curve for smooth connection
  const controlPointDistance = Math.abs(targetPos.x - sourcePos.x) / 2
  const cp1x = sourcePos.x + controlPointDistance
  const cp1y = sourcePos.y
  const cp2x = targetPos.x - controlPointDistance
  const cp2y = targetPos.y

  return `M ${sourcePos.x} ${sourcePos.y} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${targetPos.x} ${targetPos.y}`
}

function getTemporaryPath() {
  const sourceNode = nodes.value.find(n => n.id === props.connectionStart.nodeId)
  if (!sourceNode) return ''

  const sourcePos = getPortPosition(sourceNode, 'output')
  const currentPos = props.connectionCurrentMouse

  const controlPointDistance = Math.abs(currentPos.x - sourcePos.x) / 2
  const cp1x = sourcePos.x + controlPointDistance
  const cp1y = sourcePos.y
  const cp2x = currentPos.x - controlPointDistance
  const cp2y = currentPos.y

  return `M ${sourcePos.x} ${sourcePos.y} C ${cp1x} ${cp1y}, ${cp2x} ${cp2y}, ${currentPos.x} ${currentPos.y}`
}

function getMidPoint(connection) {
  const sourceNode = nodes.value.find(n => n.id === connection.sourceNodeId)
  const targetNode = nodes.value.find(n => n.id === connection.targetNodeId)

  if (!sourceNode || !targetNode) return { x: 0, y: 0 }

  const sourcePos = getPortPosition(sourceNode, connection.sourcePort)
  const targetPos = getPortPosition(targetNode, connection.targetPort)

  return {
    x: (sourcePos.x + targetPos.x) / 2,
    y: (sourcePos.y + targetPos.y) / 2
  }
}
</script>

<style scoped>
.connection-path {
  transition: stroke 0.2s, stroke-width 0.2s;
}

.connection-handle {
  cursor: pointer;
}

.connection-handle:hover {
  r: 6;
}
</style>
