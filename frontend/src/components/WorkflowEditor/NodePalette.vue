<template>
  <div class="node-palette">
    <div class="palette-header">
      <h3>节点库</h3>
    </div>
    <div class="palette-content">
      <div v-for="group in nodeGroups" :key="group.title" class="node-group">
        <div class="group-title">{{ group.title }}</div>
        <div
          v-for="node in group.nodes"
          :key="node.type"
          class="palette-node-item"
          :style="{ borderColor: getNodeColor(node.type) }"
          draggable="true"
          @dragstart="handleDragStart($event, node.type)"
        >
          <div class="node-color-indicator" :style="{ backgroundColor: getNodeColor(node.type) }"></div>
          <span>{{ node.title }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { inject } from 'vue'

const emit = defineEmits(['drag-start'])

const nodeGroups = [
  {
    title: '起始/结束',
    nodes: [
      { type: 'start', title: '开始' },
      { type: 'endpoint', title: '结束' }
    ]
  },
  {
    title: 'AI',
    nodes: [
      { type: 'llm', title: '大模型' },
      { type: 'prompt', title: '提示词' }
    ]
  },
  {
    title: '逻辑',
    nodes: [
      { type: 'if', title: '条件判断' },
      { type: 'code', title: '代码执行' }
    ]
  },
  {
    title: '数据',
    nodes: [
      { type: 'dataset', title: '数据集' }
    ]
  }
]

let getNodeColor = inject('getNodeColor')
if (!getNodeColor) getNodeColor = () => '#6B4EED'

function handleDragStart(event, type) {
  event.dataTransfer.setData('node-type', type)
  event.dataTransfer.effectAllowed = 'move'
}
</script>

<style scoped>
.node-palette {
  width: 180px;
  height: 100%;
  background: #f8f9fa;
  border-right: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
}

.palette-header {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.palette-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.palette-content {
  flex: 1;
  overflow-y: auto;
  padding: 12px 8px;
}

.node-group {
  margin-bottom: 16px;
}

.group-title {
  font-size: 12px;
  color: #6b7280;
  font-weight: 500;
  margin-bottom: 8px;
  padding-left: 4px;
  text-transform: uppercase;
}

.palette-node-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 12px;
  margin-bottom: 6px;
  background: white;
  border: 2px solid transparent;
  border-radius: 6px;
  cursor: grab;
  transition: all 0.2s;
  font-size: 14px;
  color: #374151;
}

.palette-node-item:hover {
  background: var(--primary-color);
  color: white;
  transform: translateX(4px);
}

.palette-node-item:active {
  cursor: grabbing;
}

.node-color-indicator {
  width: 12px;
  height: 12px;
  border-radius: 50%;
  flex-shrink: 0;
}
</style>
