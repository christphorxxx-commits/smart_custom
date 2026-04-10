<template>
  <div class="workflow-editor">
    <!-- Toolbar -->
    <div class="toolbar">
      <div class="toolbar-left">
        <button class="btn-secondary" @click="goBack">
          ← 返回
        </button>
        <button class="btn-secondary" @click="resetView">
          🔄 重置视图
        </button>
        <button class="btn-secondary" @click="loadDefaultWorkflow">
          📄 加载默认
        </button>
      </div>
      <div class="toolbar-right">
        <span class="scale-info">{{ Math.round(viewport.scale * 100) }}%</span>
        <button class="btn-primary" @click="handleSave">
          💾 保存
        </button>
      </div>
    </div>

    <div class="editor-main">
      <!-- Left palette -->
      <NodePalette />

      <!-- Center canvas -->
      <FlowCanvas />

      <!-- Right config panel -->
      <NodeConfigPanel />
    </div>

    <!-- Toast for save -->
    <div v-if="saveToastVisible" class="toast success">
      工作流已复制到剪贴板
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, onUnmounted, provide } from 'vue'
import { useRouter } from 'vue-router'
import { useWorkflowEditor } from '../../composables/useWorkflowEditor.js'
import NodePalette from './NodePalette.vue'
import FlowCanvas from './FlowCanvas.vue'
import NodeConfigPanel from './NodeConfigPanel.vue'

const router = useRouter()
const {
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
} = useWorkflowEditor()

// Provide all dependencies to child components
provide('nodes', nodes)
provide('connections', connections)
provide('viewport', viewport)
provide('selectedNodeId', selectedNodeId)
provide('selectedConnectionId', selectedConnectionId)
provide('selectedNode', selectedNode)
provide('isDrawingConnection', isDrawingConnection)
provide('connectionStart', connectionStart)
provide('connectionCurrentMouse', connectionCurrentMouse)
provide('addNode', addNode)
provide('updateNodePosition', updateNodePosition)
provide('updateNodeData', updateNodeData)
provide('deleteNode', deleteNode)
provide('deleteConnection', deleteConnection)
provide('deleteSelected', deleteSelected)
provide('selectNode', selectNode)
provide('selectConnection', selectConnection)
provide('clearSelection', clearSelection)
provide('startConnection', startConnection)
provide('updateConnectionMouse', updateConnectionMouse)
provide('completeConnection', completeConnection)
provide('cancelConnection', cancelConnection)
provide('getNodeColor', getNodeColor)
provide('getPortPosition', getPortPosition)
provide('panView', panView)
provide('zoomAt', zoomAt)

const saveToastVisible = ref(false)

function goBack() {
  router.push('/')
}

function handleSave() {
  const json = serialize()
  navigator.clipboard.writeText(json).then(() => {
    saveToastVisible.value = true
    setTimeout(() => {
      saveToastVisible.value = false
    }, 2000)
  })
}

async function loadDefaultWorkflow() {
  try {
    const response = await fetch('/api/workflow/default')
    if (response.ok) {
      const data = await response.json()
      deserialize(data)
      saveToastVisible.value = true
      setTimeout(() => {
        saveToastVisible.value = false
      }, 2000)
    } else {
      // If API fails, try to embed the default json directly
      const defaultData = {
        "nodes": [
          {"id": "start", "type": "start"},
          {
            "id": "router",
            "type": "router",
            "config": {
              "options": ["story", "joke", "poem"]
            }
          },
          {
            "id": "story_node",
            "type": "llm",
            "config": {
              "prompt": "写一个故事：{input}"
            }
          },
          {
            "id": "joke_node",
            "type": "llm",
            "config": {
              "prompt": "讲一个笑话：{input}"
            }
          },
          {
            "id": "poem_node",
            "type": "llm",
            "config": {
              "prompt": "写一首诗：{input}"
            }
          },
          {"id": "end", "type": "end"}
        ],
        "edges": [
          {"source": "start", "target": "router", "type": "normal"},
          {
            "source": "router",
            "target": "story_node",
            "type": "conditional",
            "condition": "story"
          },
          {
            "source": "router",
            "target": "joke_node",
            "type": "conditional",
            "condition": "joke"
          },
          {
            "source": "router",
            "target": "poem_node",
            "type": "conditional",
            "condition": "poem"
          },
          {"source": "story_node", "target": "end", "type": "normal"},
          {"source": "joke_node", "target": "end", "type": "normal"},
          {"source": "poem_node", "target": "end", "type": "normal"}
        ]
      }
      deserialize(defaultData)
      saveToastVisible.value = true
      setTimeout(() => {
        saveToastVisible.value = false
      }, 2000)
    }
  } catch (e) {
    console.error('Failed to load default workflow:', e)
  }
}

function handleKeyDown(event) {
  if (event.key === 'Delete' || event.key === 'Backspace' && event.ctrlKey) {
    deleteSelected()
  }
}

onMounted(() => {
  document.addEventListener('keydown', handleKeyDown)
  // Add a default start node
  addNode('start', 100, 200)
})

onUnmounted(() => {
  document.removeEventListener('keydown', handleKeyDown)
})
</script>

<style scoped>
.workflow-editor {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background: #fff;
}

.toolbar {
  height: 50px;
  border-bottom: 1px solid #e5e7eb;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 16px;
  background: white;
}

.toolbar-left,
.toolbar-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.scale-info {
  font-size: 14px;
  color: #6b7280;
  font-weight: 500;
  min-width: 40px;
  text-align: right;
}

.editor-main {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.btn-primary,
.btn-secondary {
  padding: 8px 16px;
  border-radius: 6px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-primary {
  background: var(--primary-color);
  color: white;
}

.btn-primary:hover {
  opacity: 0.9;
}

.btn-secondary {
  background: #f3f4f6;
  color: #374151;
  border: 1px solid #d1d5db;
}

.btn-secondary:hover {
  background: #e5e7eb;
}

.toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  z-index: 1000;
  animation: fadeInUp 0.3s ease;
}

.toast.success {
  background: #10b981;
}

@keyframes fadeInUp {
  from {
    opacity: 0;
    transform: translate(-50%, 20px);
  }
  to {
    opacity: 1;
    transform: translate(-50%, 0);
  }
}
</style>
