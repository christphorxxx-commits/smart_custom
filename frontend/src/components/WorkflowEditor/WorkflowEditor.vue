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

    <!-- Save Modal -->
    <div v-if="showSaveModal" class="modal-overlay" @click="showSaveModal = false">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>{{ isEditing ? '编辑工作流' : '保存工作流' }}</h3>
          <button class="close-btn" @click="showSaveModal = false">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label>工作流名称 <span class="required">*</span></label>
            <input
              v-model="saveForm.name"
              type="text"
              placeholder="请输入工作流名称"
            />
          </div>
          <div class="form-item">
            <label>工作流描述</label>
            <textarea
              v-model="saveForm.description"
              placeholder="请输入工作流描述（可选）"
              rows="3"
            ></textarea>
          </div>
          <div class="form-item">
            <label>图标</label>
            <input
              v-model="saveForm.icon"
              type="text"
              placeholder="emoji图标，例如 🤖"
            />
          </div>
          <div class="form-item">
            <label class="checkbox-label">
              <input v-model="saveForm.is_public" type="checkbox">
              <span>公开分享</span>
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="showSaveModal = false">取消</button>
          <button class="confirm-btn" @click="confirmSave" :disabled="saving">
            {{ saving ? '保存中...' : '确认保存' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Toast -->
    <div v-if="saveToastVisible" class="toast" :class="saveToastClass">
      {{ saveToastMessage }}
    </div>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, onUnmounted, provide } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import axios from 'axios'
import { useWorkflowEditor } from '../../composables/useWorkflowEditor.js'
import NodePalette from './NodePalette.vue'
import FlowCanvas from './FlowCanvas.vue'
import NodeConfigPanel from './NodeConfigPanel.vue'

const router = useRouter()
const route = useRoute()
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

// Modal state
const showSaveModal = ref(false)
const saving = ref(false)
const isEditing = ref(false)

// Save form
const saveForm = reactive({
  name: '',
  description: '',
  icon: '🤖',
  is_public: false
})

// Toast state
const saveToastVisible = ref(false)
const saveToastMessage = ref('')
const saveToastClass = ref('success')

function goBack() {
  router.push('/')
}

function handleSave() {
  // Check if at least one non-start/end node
  const validNodes = nodes.value.filter(n => n.type !== 'start' && n.type !== 'end')
  if (validNodes.length === 0) {
    showToast('请至少添加一个有效节点', 'error')
    return
  }
  // Open save modal
  showSaveModal.value = true
}

async function confirmSave() {
  if (!saveForm.name.trim()) {
    showToast('请输入工作流名称', 'error')
    return
  }

  saving.value = true
  try {
    const data = JSON.parse(serialize())
    const response = await axios.post('/api/app/save', {
      name: saveForm.name,
      description: saveForm.description,
      icon: saveForm.icon || '🤖',
      nodes: data.nodes,
      edges: data.connections,
      is_public: saveForm.is_public
    })

    if (response.data.success) {
      showToast('保存成功！', 'success')
      showSaveModal.value = false
      // Redirect to workflow list or chat page after save
      setTimeout(() => {
        router.push('/')
      }, 1000)
    } else {
      showToast(response.data.msg || '保存失败', 'error')
    }
  } catch (error) {
    console.error('Save failed:', error)
    showToast(error.response?.data?.msg || '网络错误，请稍后重试', 'error')
  } finally {
    saving.value = false
  }
}

function showToast(message, type = 'success') {
  saveToastMessage.value = message
  saveToastClass.value = type
  saveToastVisible.value = true
  setTimeout(() => {
    saveToastVisible.value = false
  }, 3000)
}

async function loadDefaultWorkflow() {
  try {
    const response = await fetch('/api/app/default')
    if (response.ok) {
      const data = await response.json()
      deserialize(data.data || data)
      showToast('默认工作流加载成功', 'success')
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
        "connections": [
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
      showToast('默认工作流加载成功', 'success')
    }
  } catch (e) {
    console.error('Failed to load default workflow:', e)
    showToast('加载默认工作流失败', 'error')
  }
}

function handleKeyDown(event) {
  if (event.key === 'Delete' || event.key === 'Backspace' && event.ctrlKey) {
    deleteSelected()
  }
}

// Load existing workflow if editing
onMounted(() => {
  document.addEventListener('keydown', handleKeyDown)
  // Add a default start node
  addNode('start', 100, 200)

  const id = route.params.id
  if (id) {
    isEditing.value = true
    // Load existing workflow data
    axios.get(`/api/app/${id}`).then(res => {
      if (res.data.success) {
        const data = res.data.data
        deserialize({
          nodes: data.nodes,
          connections: data.edges
        })
        saveForm.name = data.name
        saveForm.description = data.description || ''
        saveForm.icon = data.icon || '🤖'
        saveForm.is_public = data.is_public || false
      }
    }).catch(err => {
      console.error('Failed to load workflow:', err)
      showToast('加载工作流失败', 'error')
    })
  }
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

.toast.error {
  background: #ef4444;
}

/* Modal */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  width: 480px;
  background: white;
  border-radius: 16px;
  overflow: hidden;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
}

.modal-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 24px;
  border-bottom: 1px solid #e2e8f0;
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1e293b;
}

.close-btn {
  width: 32px;
  height: 32px;
  display: flex;
  align-items: center;
  justify-content: center;
  border: none;
  background: transparent;
  font-size: 18px;
  cursor: pointer;
  border-radius: 6px;
}

.close-btn:hover {
  background: #f1f5f9;
}

.modal-body {
  padding: 24px;
}

.form-item {
  margin-bottom: 20px;
}

.form-item label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: #334155;
  margin-bottom: 8px;
}

.form-item .required {
  color: #ef4444;
}

.form-item input,
.form-item textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-item input:focus,
.form-item textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-item input::placeholder,
.form-item textarea::placeholder {
  color: #94a3b8;
}

.form-item textarea {
  resize: vertical;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.checkbox-label input {
  width: auto;
  cursor: pointer;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 24px 24px;
}

.cancel-btn {
  padding: 10px 24px;
  border: 1px solid #e2e8f0;
  background: white;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: #f1f5f9;
}

.confirm-btn {
  padding: 10px 24px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s;
}

.confirm-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.35);
}

.confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
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
