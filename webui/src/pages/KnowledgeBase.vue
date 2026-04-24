<template>
  <div class="kb-container">
    <!-- 左侧：知识库列表 -->
    <div class="sidebar-left">
      <!-- 顶部：搜索 + 新建 -->
      <div class="sidebar-header">
        <div class="search-box">
          <span class="search-icon">🔍</span>
          <input
            v-model="searchKeyword"
            type="text"
            placeholder="搜索知识库..."
            @input="handleSearch"
          />
        </div>
        <button class="btn-create" @click="openCreateModal">
          <span>+</span>
          <span>新建</span>
        </button>
      </div>

      <!-- 知识库卡片列表 -->
      <div class="kb-list">
        <div
          class="kb-card"
          :class="{ active: selectedKb?.uuid === item.uuid }"
          v-for="item in filteredList"
          :key="item.id"
          @click="selectKb(item)"
        >
          <div class="kb-card-header">
            <span class="kb-icon">📚</span>
            <span class="kb-name">{{ item.name }}</span>
          </div>
          <div class="kb-card-footer">
            <span class="kb-model">{{ item.embedding_model }}</span>
          </div>
        </div>
      </div>

      <!-- 空状态 -->
      <div class="empty-state" v-if="kbList.length === 0 && !loading">
        <div class="empty-icon">📚</div>
        <p>暂无知识库</p>
        <button class="btn-create-empty" @click="openCreateModal">创建第一个知识库</button>
      </div>
    </div>

    <!-- 右侧：选中知识库详情 -->
    <div class="main-right" v-if="selectedKb">
      <!-- 顶部标题 -->
      <div class="main-header">
        <h2>{{ selectedKb.name }} - 数据集</h2>
      </div>

      <div class="main-content">
        <!-- 中间：文件列表 -->
        <div class="files-area">
          <div class="files-header">
            <span class="title">文件列表</span>
            <button class="btn-upload" @click="handleUploadFile">
              <span>+</span> 上传文件
            </button>
          </div>
          <div class="file-list">
            <div
              class="file-item"
              v-for="file in fileList"
              :key="file.id"
            >
              <div class="file-icon">📄</div>
              <div class="file-info">
                <div class="file-name">{{ file.file_name }}</div>
                <div class="file-meta">
                  <span>切片: {{ file.chunk_count || 0 }}</span>
                  <span v-if="file.file_size"> • {{ formatFileSize(file.file_size) }}</span>
                </div>
              </div>
              <div class="file-status" :class="'status-' + file.status">
                {{ getStatusText(file.status) }}
              </div>
              <button class="btn-delete-file" @click="confirmDeleteFile(file)">
                🗑️
              </button>
            </div>
          </div>

          <!-- 空文件状态 -->
          <div class="empty-files" v-if="fileList.length === 0">
            <p>该知识库暂无文件，请上传文档</p>
          </div>
        </div>

        <!-- 右侧：知识库信息 -->
        <div class="info-sidebar">
          <div class="info-section">
            <div class="info-label">知识库名称</div>
            <div class="info-value">{{ selectedKb.name }}</div>
          </div>
          <div class="info-section" v-if="selectedKb.description">
            <div class="info-label">描述</div>
            <div class="info-value">{{ selectedKb.description }}</div>
          </div>
          <div class="info-section">
            <div class="info-label">Embedding 模型</div>
            <div class="info-value">{{ selectedKb.embedding_model }}</div>
          </div>
          <div class="info-section">
            <div class="info-label">问答模型</div>
            <div class="info-value">{{ selectedKb.search_model }}</div>
          </div>
          <div class="info-section" v-if="selectedKb.text_process_model">
            <div class="info-label">文本预处理模型</div>
            <div class="info-value">{{ selectedKb.text_process_model }}</div>
          </div>
          <div class="info-section" v-if="selectedKb.image_understand_model">
            <div class="info-label">图片理解模型</div>
            <div class="info-value">{{ selectedKb.image_understand_model }}</div>
          </div>
          <div class="info-section">
            <div class="info-label">向量维度</div>
            <div class="info-value">{{ selectedKb.dimension }}</div>
          </div>
          <div class="info-section">
            <div class="info-label">UUID</div>
            <div class="info-value uuid">{{ selectedKb.uuid }}</div>
          </div>
          <div class="info-section">
            <div class="info-label">collection_name</div>
            <div class="info-value uuid">{{ selectedKb.collection_name }}</div>
          </div>

          <div class="action-buttons">
            <button class="btn-delete-kb" @click="confirmDeleteKb">
              🗑️ 删除知识库
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧：空状态 -->
    <div class="main-right empty-selected" v-else>
      <div class="empty-content">
        <div class="empty-icon">👈</div>
        <p>请在左侧选择一个知识库</p>
      </div>
    </div>

    <!-- 新建知识库弹窗 -->
    <div class="modal-overlay" v-if="showCreateModal" @click.self="closeCreateModal">
      <div class="modal-content">
        <div class="modal-header">
          <h3>新建知识库</h3>
          <button class="btn-close" @click="closeCreateModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label>知识库名称 <span class="required">*</span></label>
            <input
              v-model="createForm.name"
              type="text"
              placeholder="请输入知识库名称"
            />
          </div>
          <div class="form-item">
            <label>描述</label>
            <textarea
              v-model="createForm.description"
              placeholder="请输入知识库描述（可选）"
            ></textarea>
          </div>
          <div class="form-row">
            <div class="form-item">
              <label>Embedding 模型</label>
              <input v-model="createForm.embedding_model" type="text" />
            </div>
            <div class="form-item">
              <label>问答模型</label>
              <input v-model="createForm.search_model" type="text" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-item">
              <label>向量维度</label>
              <input v-model.number="createForm.dimension" type="number" />
            </div>
          </div>
        </div>
        <div class="modal-footer">
          <button class="btn-cancel" @click="closeCreateModal">取消</button>
          <button class="btn-confirm" @click="handleCreateKb" :disabled="creating">
            {{ creating ? '创建中...' : '创建' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 加载遮罩 -->
    <div class="loading-overlay" v-if="loading">
      <div class="loading-spinner"></div>
      <p>加载中...</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()

// State
const loading = ref(false)
const searchKeyword = ref('')
const kbList = ref([])
const selectedKb = ref(null)
const fileList = ref([])
const showCreateModal = ref(false)
const creating = ref(false)

// 创建表单
const createForm = ref({
  name: '',
  description: '',
  embedding_model: 'text-embedding-v4',
  search_model: 'qwen-max',
  dimension: 1536
})

// 过滤列表
const filteredList = computed(() => {
  if (!searchKeyword.value) return kbList.value
  const keyword = searchKeyword.value.toLowerCase()
  return kbList.value.filter(item =>
    item.name.toLowerCase().includes(keyword)
  )
})

// 加载知识库列表
const loadKbList = async () => {
  loading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.post('/api/knowledge/list', {
      page: 1,
      page_size: 100
    }, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
    if (response.data.success && response.data.data) {
      kbList.value = response.data.data.data || []
    }
  } catch (error) {
    console.error('加载知识库列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  // 已经通过computed过滤
}

// 打开创建弹窗
const openCreateModal = () => {
  createForm.value = {
    name: '',
    description: '',
    embedding_model: 'text-embedding-v4',
    search_model: 'qwen-max',
    dimension: 1536
  }
  showCreateModal.value = true
}

const closeCreateModal = () => {
  showCreateModal.value = false
}

// 创建知识库
const handleCreateKb = async () => {
  if (!createForm.value.name.trim()) {
    alert('请输入知识库名称')
    return
  }
  creating.value = true
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.post('/api/knowledge/create', createForm.value, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (response.data.success) {
      closeCreateModal()
      await loadKbList()
    } else {
      alert(response.data.msg || '创建失败')
    }
  } catch (error) {
    console.error('创建知识库失败:', error)
    alert('创建知识库失败')
  } finally {
    creating.value = false
  }
}

// 选择知识库
const selectKb = async (item) => {
  selectedKb.value = item
  await loadFileList(item.id)
}

// 加载文件列表
const loadFileList = async (kbId) => {
  // TODO: 需要后端添加文件列表API，先占位
  // 这里暂时获取不到，后续后端添加接口后完善
  fileList.value = []
}

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (!bytes) return '-'
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  if (bytes < 1024 * 1024 * 1024) return (bytes / 1024 / 1024).toFixed(1) + ' MB'
  return (bytes / 1024 / 1024 / 1024).toFixed(1) + ' GB'
}

// 获取状态文字
const getStatusText = (status) => {
  const statusMap = {
    0: '处理中',
    1: '成功',
    2: '失败'
  }
  return statusMap[status] || '未知'
}

// 上传文件
const handleUploadFile = () => {
  // TODO: 后续实现文件上传和切片
  alert('文件上传功能开发中...')
}

// 删除文件确认
const confirmDeleteFile = (file) => {
  if (confirm(`确认删除文件 "${file.file_name}"？`)) {
    // TODO: 调用删除API
    console.log('删除文件:', file)
  }
}

// 删除知识库确认
const confirmDeleteKb = () => {
  if (!selectedKb.value) return
  if (confirm(`确认删除知识库 "${selectedKb.value.name}"？\n删除后无法恢复，向量表也会被删除。`)) {
    // TODO: 调用删除API
    console.log('删除知识库:', selectedKb.value)
  }
}

// 页面加载
onMounted(() => {
  loadKbList()
})

// Axios interceptor
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => Promise.reject(error)
)

axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('access_token')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
</script>

<style scoped>
:root {
  --sidebar-width: 320px;
  --info-sidebar-width: 280px;
  --border-color: #e5e7eb;
  --text-primary: #1d2129;
  --text-secondary: #86909c;
  --bg-primary: #ffffff;
  --bg-secondary: #f7f8fa;
  --primary-color: #6366f1;
  --primary-hover: #4f46e5;
  --hover-bg: #f2f3f5;
  --radius: 8px;
  --radius-lg: 12px;
  --shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.kb-container {
  display: flex;
  height: 100vh;
  background: var(--bg-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* 左侧知识库列表 */
.sidebar-left {
  width: var(--sidebar-width);
  background: var(--bg-secondary);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.sidebar-header {
  padding: 16px 12px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  gap: 8px;
}

.search-box {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 6px;
  background: var(--bg-primary);
  padding: 8px 10px;
  border-radius: var(--radius);
  border: 1px solid var(--border-color);
}

.search-icon {
  color: var(--text-secondary);
  font-size: 14px;
}

.search-box input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  color: var(--text-primary);
}

.btn-create {
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 12px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 14px;
  transition: all 0.2s;
  white-space: nowrap;
}

.btn-create:hover {
  background: var(--primary-hover);
}

.kb-list {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.kb-card {
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.kb-card:hover {
  background: var(--hover-bg);
  border-color: var(--primary-color);
}

.kb-card.active {
  border-color: var(--primary-color);
  background: var(--hover-bg);
}

.kb-card-header {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 6px;
}

.kb-icon {
  font-size: 18px;
}

.kb-name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.kb-card-footer {
  text-align: right;
}

.kb-model {
  font-size: 12px;
  color: var(--text-secondary);
  background: var(--hover-bg);
  padding: 2px 8px;
  border-radius: 4px;
}

.empty-state {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
  padding: 20px;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  margin: 0 0 16px;
}

.btn-create-empty {
  padding: 8px 16px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
}

/* 右侧详情 */
.main-right {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.main-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
}

.main-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.files-area {
  flex: 1;
  overflow-y: auto;
  padding: 16px 24px;
}

.files-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.files-header .title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.btn-upload {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 6px 12px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 14px;
}

.btn-upload:hover {
  background: var(--primary-hover);
}

.file-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--bg-secondary);
  border-radius: var(--radius);
  border: 1px solid var(--border-color);
}

.file-icon {
  font-size: 24px;
  flex-shrink: 0;
}

.file-info {
  flex: 1;
}

.file-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 4px;
}

.file-meta {
  font-size: 12px;
  color: var(--text-secondary);
}

.file-meta span {
  margin-right: 12px;
}

.file-status {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  flex-shrink: 0;
}

.file-status.status-0 {
  background: #fef3c7;
  color: #d97706;
}

.file-status.status-1 {
  background: #dcfce7;
  color: #166534;
}

.file-status.status-2 {
  background: #fee2e2;
  color: #dc2626;
}

.btn-delete-file {
  background: transparent;
  border: none;
  font-size: 16px;
  cursor: pointer;
  padding: 4px;
  border-radius: 4px;
  flex-shrink: 0;
  opacity: 0.6;
  transition: all 0.2s;
}

.btn-delete-file:hover {
  background: #fee2e2;
  opacity: 1;
}

.empty-files {
  text-align: center;
  padding: 60px 20px;
  color: var(--text-secondary);
}

.empty-files p {
  margin: 0;
}

/* 右侧信息栏 */
.info-sidebar {
  width: var(--info-sidebar-width);
  background: var(--bg-secondary);
  border-left: 1px solid var(--border-color);
  padding: 16px;
  overflow-y: auto;
  flex-shrink: 0;
}

.info-section {
  margin-bottom: 16px;
}

.info-label {
  font-size: 12px;
  color: var(--text-secondary);
  margin-bottom: 4px;
}

.info-value {
  font-size: 14px;
  color: var(--text-primary);
  word-break: break-all;
}

.info-value.uuid {
  font-family: monospace;
  font-size: 11px;
  background: var(--bg-primary);
  padding: 4px 6px;
  border-radius: 4px;
}

.action-buttons {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.btn-delete-kb {
  width: 1111;
  padding: 10px;
  background: #ef4444;
  color: white;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 14px;
}

.btn-delete-kb:hover {
  background: #dc2626;
}

/* 空选中状态 */
.empty-selected {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-content {
  text-align: center;
  color: var(--text-secondary);
}

.empty-content .empty-icon {
  font-size: 64px;
  margin-bottom: 16px;
  opacity: 0.3;
}

/* 弹窗 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(0, 0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: var(--bg-primary);
  border-radius: var(--radius-lg);
  width: 500px;
  max-width: 90vw;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
}

.btn-close {
  background: transparent;
  border: none;
  font-size: 20px;
  cursor: pointer;
  color: var(--text-secondary);
  padding: 0;
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: 4px;
}

.btn-close:hover {
  background: var(--hover-bg);
}

.modal-body {
  padding: 20px;
}

.form-item {
  margin-bottom: 16px;
}

.form-item label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 6px;
}

.form-item .required {
  color: #ef4444;
}

.form-item input,
.form-item textarea {
  width: 100%;
  padding: 10px 12px;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  font-size: 14px;
  color: var(--text-primary);
  outline: none;
  box-sizing: border-box;
}

.form-item textarea {
  min-height: 80px;
  resize: vertical;
}

.form-item input:focus,
.form-item textarea:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-row {
  display: flex;
  gap: 16px;
}

.form-row .form-item {
  flex: 1;
  margin-bottom: 0;
}

.modal-footer {
  display: flex;
  justify-content: flex-end;
  gap: 12px;
  padding: 16px 20px;
  border-top: 1px solid var(--border-color);
}

.btn-cancel {
  padding: 10px 20px;
  background: transparent;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary);
}

.btn-cancel:hover {
  background: var(--hover-bg);
}

.btn-confirm {
  padding: 10px 20px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  font-size: 14px;
}

.btn-confirm:hover:not(:disabled) {
  background: var(--primary-hover);
}

.btn-confirm:disabled {
  background: var(--text-secondary);
  cursor: not-allowed;
}

/* 加载遮罩 */
.loading-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: rgba(255, 255, 255, 0.8);
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  z-index: 999;
}

.loading-spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin-bottom: 16px;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.loading-overlay p {
  color: var(--text-secondary);
  margin: 0;
}

/* Scrollbar */
.kb-list::-webkit-scrollbar,
.files-area::-webkit-scrollbar,
.info-sidebar::-webkit-scrollbar {
  width: 6px;
}

.kb-list::-webkit-scrollbar-track,
.files-area::-webkit-scrollbar-track,
.info-sidebar::-webkit-scrollbar-track {
  background: transparent;
}

.kb-list::-webkit-scrollbar-thumb,
.files-area::-webkit-scrollbar-thumb,
.info-sidebar::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.kb-list::-webkit-scrollbar-thumb:hover,
.files-area::-webkit-scrollbar-thumb:hover,
.info-sidebar::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

/* Responsive */
@media (max-width: 900px) {
  .kb-container {
    flex-direction: column;
  }
  .sidebar-left {
    width: 100%;
    max-height: 40vh;
  }
  .info-sidebar {
    display: none;
  }
}
</style>
