<template>
  <div class="config-panel">
    <div class="panel-header">
      <h3>配置</h3>
    </div>
    <div class="panel-content" v-if="selectedNode">
      <div class="form-group">
        <label>节点标题</label>
        <input
          v-model="localData.title"
          type="text"
          class="form-input"
          @input="updateNode"
        />
      </div>

      <!-- Start node specific config -->
      <template v-if="selectedNode.type === 'start'">
        <div class="form-group">
          <label>输入变量（JSON格式）</label>
          <textarea
            v-model="localData.inputVariable"
            class="form-textarea"
            placeholder='{"key": "value"}'
            rows="4"
            @input="updateNode"
          ></textarea>
        </div>
      </template>

      <!-- LLM node specific config -->
      <template v-if="selectedNode.type === 'llm'">
        <div class="form-group">
          <label>模型名称</label>
          <select v-model="localData.model" class="form-input" @change="updateNode">
            <option value="gpt-4o">GPT-4o</option>
            <option value="gpt-4o-mini">GPT-4o Mini</option>
            <option value="claude-3-5-sonnet">Claude 3.5 Sonnet</option>
            <option value="claude-3-opus">Claude 3 Opus</option>
          </select>
        </div>

        <div class="form-group">
          <label>系统提示词</label>
          <textarea
            v-model="localData.systemPrompt"
            class="form-textarea"
            rows="6"
            @input="updateNode"
          ></textarea>
        </div>

        <div class="form-group">
          <label>温度: {{ localData.temperature }}</label>
          <input
            v-model.number="localData.temperature"
            type="range"
            min="0"
            max="2"
            step="0.1"
            class="form-slider"
            @input="updateNode"
          />
        </div>

        <div class="form-group">
          <label>最大 Token 数</label>
          <input
            v-model.number="localData.maxTokens"
            type="number"
            class="form-input"
            min="1"
            max="16000"
            @input="updateNode"
          />
        </div>
      </template>

      <!-- if (router) node specific config -->
      <template v-if="selectedNode.type === 'if'">
        <div class="form-group">
          <label>分支列表</label>
          <div v-for="(branch, index) in localData.branches" :key="index" class="branch-item">
            <input
              v-model="localData.branches[index]"
              type="text"
              class="branch-input"
              placeholder="分支名称"
              @input="updateNode"
            />
            <button
              class="btn-remove-branch"
              @click="removeBranch(index)"
              v-if="localData.branches.length > 1"
            >
              ✕
            </button>
          </div>
          <button class="btn-add-branch" @click="addBranch">
            + 添加分支
          </button>
          <div class="hint">每个分支对应一个输出端口，可以分别连接到不同节点</div>
        </div>
      </template>

      <!-- For other node types, show generic JSON editor -->
      <template v-else>
        <div class="form-group">
          <label>节点数据（JSON）</label>
          <textarea
            v-model="jsonData"
            class="form-textarea"
            rows="10"
            @blur="handleJsonUpdate"
          ></textarea>
          <div v-if="jsonError" class="error-message">{{ jsonError }}</div>
        </div>
      </template>
    </div>

    <div v-else class="empty-state" v-if="!selectedNode">
      <p>选择一个节点进行配置</p>
    </div>

    <div class="panel-footer">
      <button v-if="selectedNode" class="btn-delete" @click="handleDeleteSelected">
        删除节点
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, watch, computed } from 'vue'
import { inject } from 'vue'

let selectedNode = inject('selectedNode')
let updateNodeData = inject('updateNodeData')
let deleteSelected = inject('deleteSelected')

if (!selectedNode) selectedNode = ref(null)
if (!updateNodeData) updateNodeData = () => {}
if (!deleteSelected) deleteSelected = () => {}

const localData = ref({})
const jsonData = ref('')
const jsonError = ref('')

watch(selectedNode, (newNode) => {
  if (newNode) {
    localData.value = { ...newNode.data }
    if (!isSpecialNode(newNode.type)) {
      try {
        jsonData.value = JSON.stringify(newNode.data, null, 2)
        jsonError.value = ''
      } catch (e) {
        jsonData.value = ''
        jsonError.value = 'Invalid JSON'
      }
    }
  }
}, { immediate: true })

function isSpecialNode(type) {
  return type === 'start' || type === 'llm' || type === 'if'
}

function addBranch() {
  localData.value.branches.push(`分支${localData.value.branches.length + 1}`)
  updateNode()
}

function removeBranch(index) {
  localData.value.branches.splice(index, 1)
  updateNode()
}

function updateNode() {
  if (selectedNode.value) {
    updateNodeData(selectedNode.value.id, localData.value)
  }
}

function handleJsonUpdate() {
  if (!selectedNode.value) return

  try {
    const parsed = JSON.parse(jsonData.value)
    localData.value = parsed
    updateNode()
    jsonError.value = ''
  } catch (e) {
    jsonError.value = 'JSON 格式错误'
  }
}

function handleDeleteSelected() {
  deleteSelected()
}
</script>

<style scoped>
.config-panel {
  width: 280px;
  height: 100%;
  background: #f8f9fa;
  border-left: 1px solid #e5e7eb;
  display: flex;
  flex-direction: column;
}

.panel-header {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.panel-header h3 {
  margin: 0;
  font-size: 16px;
  color: #333;
  font-weight: 600;
}

.panel-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
}

.panel-footer {
  padding: 16px;
  border-top: 1px solid #e5e7eb;
}

.empty-state {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #9ca3af;
  padding: 16px;
}

.empty-state p {
  margin: 0;
  font-size: 14px;
}

.form-group {
  margin-bottom: 16px;
}

.form-group label {
  display: block;
  font-size: 13px;
  font-weight: 500;
  color: #374151;
  margin-bottom: 6px;
}

.form-input,
.form-textarea,
.form-slider {
  width: 100%;
  padding: 8px 10px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 14px;
  background: white;
  color: #374151;
  box-sizing: border-box;
}

.form-input:focus,
.form-textarea:focus {
  outline: none;
  border-color: #6B4EED;
  box-shadow: 0 0 0 2px rgba(107, 78, 237, 0.2);
}

.form-textarea {
  resize: vertical;
  min-height: 80px;
  font-family: monospace;
}

.form-slider {
  padding: 0;
  height: 6px;
  accent-color: #6B4EED;
}

.error-message {
  color: #dc2626;
  font-size: 12px;
  margin-top: 4px;
}

.btn-delete {
  width: 100%;
  padding: 10px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: background 0.2s;
}

.btn-delete:hover {
  background: #dc2626;
}

.branch-item {
  display: flex;
  gap: 6px;
  margin-bottom: 6px;
  align-items: center;
}

.branch-input {
  flex: 1;
  padding: 6px 8px;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  font-size: 13px;
}

.branch-input:focus {
  outline: none;
  border-color: #6B4EED;
  box-shadow: 0 0 0 2px rgba(107, 78, 237, 0.2);
}

.btn-remove-branch {
  width: 26px;
  height: 26px;
  border: none;
  background: #ef4444;
  color: white;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  line-height: 1;
  padding: 0;
  display: flex;
  align-items: center;
  justify-content: center;
}

.btn-remove-branch:hover {
  background: #dc2626;
}

.btn-add-branch {
  width: 100%;
  padding: 6px;
  margin-top: 4px;
  background: #f3f4f6;
  border: 1px dashed #d1d5db;
  border-radius: 4px;
  font-size: 12px;
  cursor: pointer;
  color: #374151;
}

.btn-add-branch:hover {
  background: #e5e7eb;
  border-color: #6B4EED;
}

.hint {
  font-size: 11px;
  color: #6b7280;
  margin-top: 6px;
}
</style>
