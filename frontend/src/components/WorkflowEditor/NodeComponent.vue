<template>
  <div
    class="node"
    :class="{ selected: isSelected }"
    :style="{
      left: node.x + 'px',
      top: node.y + 'px',
      borderColor: borderColor,
      minHeight: hasMultipleOutputs ? 'auto' : '60px'
    }"
    @mousedown="handleMouseDown"
    @click.stop="handleClick"
  >
    <!-- Input port -->
    <div
      class="port input-port"
      :style="{ backgroundColor: borderColor }"
      @mousedown.stop
      @mouseup.stop="handleInputPortConnect"
    ></div>

    <div class="node-header" :style="{ backgroundColor: borderColor }">
      <span class="node-title">{{ node.data?.title || node.type }}</span>
    </div>

    <div class="node-body">
      <!-- Show branch names for if node -->
      <template v-if="node.type === 'if' && node.data?.branches">
        <div v-for="(branch, index) in node.data.branches" :key="index" class="branch-label">
          {{ branch || `Branch ${index + 1}` }}
        </div>
      </template>
      <template v-else>
        <slot></slot>
      </template>
    </div>

    <!-- Output ports - single for normal node, multiple for if -->
    <template v-if="node.type === 'if' && node.data?.branches">
      <div
        v-for="(branch, index) in node.data.branches"
        :key="index"
        class="port output-port multiple"
        :style="{
          backgroundColor: borderColor,
          top: getBranchPortY(index) + '%'
        }"
        @mousedown.stop="handleOutputPortStart($event, 'output_' + index.toString())"
      ></div>
    </template>
    <template v-else>
      <!-- Single output port -->
      <div
        class="port output-port"
        :style="{ backgroundColor: borderColor }"
        @mousedown.stop="handleOutputPortStart($event, 'output')"
      ></div>
    </template>
  </div>
</template>

<script setup>
import { ref, inject, computed } from 'vue'

const props = defineProps({
  node: Object
})

const emit = defineEmits(['click', 'mousedown'])

let selectedNodeId = inject('selectedNodeId')
let getNodeColor = inject('getNodeColor')
let startConnection = inject('startConnection')
let completeConnection = inject('completeConnection')

if (!selectedNodeId) selectedNodeId = ref(null)
if (!getNodeColor) getNodeColor = () => '#6B4EED'
if (!startConnection) startConnection = () => {}
if (!completeConnection) completeConnection = () => {}

const isSelected = computed(() => selectedNodeId.value === props.node.id)

const borderColor = computed(() => getNodeColor(props.node.type))

const hasMultipleOutputs = computed(() => {
  return props.node.type === 'if' && props.node.data?.branches && props.node.data.branches.length > 1
})

function getBranchPortY(index) {
  if (!props.node.data?.branches || props.node.data.branches.length === 0) {
    return 50
  }
  const step = 100 / (props.node.data.branches.length + 1)
  return step * (index + 1)
}

function handleMouseDown(event) {
  emit('mousedown', event, props.node)
}

function handleClick(event) {
  emit('click', props.node)
}

function handleOutputPortStart(event, port) {
  event.preventDefault()
  event.stopPropagation()
  startConnection(props.node.id, port)
}

function handleInputPortConnect(event) {
  event.preventDefault()
  event.stopPropagation()
  completeConnection(props.node.id, 'input')
}
</script>

<style scoped>
.node {
  position: absolute;
  width: 180px;
  min-height: 60px;
  background: white;
  border: 2px solid #ccc;
  border-radius: 8px;
  box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
  cursor: move;
  display: flex;
  flex-direction: column;
  transition: all 0.2s;
  z-index: 1;
}

.node.selected {
  border-color: #6B4EED;
  box-shadow: 0 0 0 3px rgba(107, 78, 237, 0.2);
}

.node:hover {
  box-shadow: 0 6px 12px rgba(0, 0, 0, 0.15);
}

.port {
  position: absolute;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  border: 2px solid white;
  cursor: crosshair;
  z-index: 10;
}

.input-port {
  left: -6px;
  top: 50%;
  transform: translateY(-50%);
}

.output-port {
  right: -6px;
  transform: translateY(-50%);
}

.output-port.multiple {
  transform: translateY(-50%);
}

.port:hover {
  transform: translateY(-50%) scale(1.3);
}

.output-port.multiple:hover {
  transform: translateY(-50%) scale(1.3);
}

.node-header {
  padding: 6px 10px;
  border-radius: 4px 4px 0 0;
}

.node-title {
  color: white;
  font-size: 13px;
  font-weight: 500;
  line-height: 1.4;
}

.node-body {
  padding: 8px 10px;
  font-size: 12px;
  color: #6b7280;
  min-height: 20px;
}

.branch-label {
  padding: 2px 4px;
  margin-bottom: 3px;
  background: #f3f4f6;
  border-radius: 3px;
}

.branch-label:last-child {
  margin-bottom: 0;
}
</style>
