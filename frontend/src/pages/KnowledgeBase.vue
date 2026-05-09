<template>
  <div class="kb-page-container">
    <!-- 左侧导航栏（和主页一致，保留） -->
    <div class="left-sidebar">
      <!-- Logo -->
      <div class="logo-section">
        <div class="logo">
          <img src="../assets/bwen.jpg" alt="白问" class="logo-image" />
          <span class="logo-text" v-if="!isLeftSidebarCollapsed">白问</span>
        </div>
        <button class="toggle-btn" @click="toggleLeftSidebar" title="展开/收起">
          <span>{{ isLeftSidebarCollapsed ? '▶' : '◀' }}</span>
        </button>
      </div>

      <!-- 导航菜单 -->
      <nav class="nav-menu">
        <div
          class="nav-item"
          :class="{ active: activeNav === 'portal' }"
          @click="handleNavClick('portal')"
        >
          <span class="nav-icon">🏠</span>
          <span class="nav-text" v-if="!isLeftSidebarCollapsed">门户</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: activeNav === 'workbench' }"
          @click="handleNavClick('workbench')"
        >
          <span class="nav-icon">🛠️</span>
          <span class="nav-text" v-if="!isLeftSidebarCollapsed">工作台</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: activeNav === 'flow-editor' }"
          @click="handleNavClick('flow-editor')"
        >
          <span class="nav-icon">🎨</span>
          <span class="nav-text" v-if="!isLeftSidebarCollapsed">工作流编排</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: activeNav === 'knowledge' }"
          @click="handleNavClick('knowledge')"
        >
          <span class="nav-icon">📚</span>
          <span class="nav-text" v-if="!isLeftSidebarCollapsed">知识库</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: activeNav === 'account' }"
          @click="handleNavClick('account')"
        >
          <span class="nav-icon">👤</span>
          <span class="nav-text" v-if="!isLeftSidebarCollapsed">账号</span>
        </div>
        <div
          class="nav-item"
          :class="{ active: activeNav === 'admin' }"
          @click="handleNavClick('admin')"
        >
          <span class="nav-icon">⚙️</span>
          <span class="nav-text" v-if="!isLeftSidebarCollapsed">管理员</span>
        </div>
      </nav>

      <!-- 底部用户信息 -->
      <div class="user-section" @click="toggleUserMenu">
        <div class="user-avatar">
          {{ userInitial }}
        </div>
        <div class="user-details" v-if="!isLeftSidebarCollapsed">
          <div class="user-name">{{ username }}</div>
        </div>
        <div class="expand-icon" v-if="!isLeftSidebarCollapsed">
          {{ isUserMenuExpanded ? '▲' : '▼' }}
        </div>
      </div>

      <!-- 用户下拉菜单 -->
      <div class="user-menu" v-if="isUserMenuExpanded && !isLeftSidebarCollapsed">
        <div class="menu-item" @click="handleLogout">
          <span class="menu-icon">🚪</span>
          <span class="menu-text">退出登录</span>
        </div>
      </div>
    </div>

    <!-- 右侧主内容：知识库管理 -->
    <div class="kb-main-content">
      <div class="kb-container">
        <!-- 左侧：知识库列表 -->
        <div class="kb-list-sidebar">
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
        <div class="kb-detail-main" v-if="selectedKb">
          <!-- 顶部标题 -->
          <div class="detail-header">
            <h2>{{ selectedKb.name }} - 数据集</h2>
          </div>

          <div class="detail-content">
            <!-- 中间：文件/切片列表 -->
            <div class="files-area">
              <!-- Tab 导航 -->
              <div class="tabs-header">
                <div class="tabs-nav">
                  <div
                    class="tab-item"
                    :class="{ active: activeTab === 'files' }"
                    @click="switchTab('files')"
                  >
                    文件列表
                  </div>
                  <div
                    class="tab-item"
                    :class="{ active: activeTab === 'chunks' }"
                    @click="switchTab('chunks')"
                  >
                    切片列表
                  </div>
                </div>

                <!-- 文件列表操作按钮 -->
                <div class="header-actions">
                  <!-- 隐藏的文件选择器 -->
                  <input
                    type="file"
                    ref="fileInputRef"
                    style="display: none"
                    accept=".txt,.md,.pdf,.doc,.docx,.py,.js,.json,.yaml,.yml,.xml,.html,.css,.java,.go,.cpp,.c,.h,.rs"
                    @change="handleFileSelect"
                  />
                  <button class="btn-upload" v-if="activeTab === 'files'" @click="handleUploadFile" :disabled="uploading">
                    <span v-if="!uploading">+ 上传文件</span>
                    <span v-else>上传中 {{ uploadProgress }}%</span>
                  </button>
                </div>
              </div>

              <!-- 文件列表内容 -->
              <div class="tab-content" v-if="activeTab === 'files'">
                <div class="file-list">
                  <div
                    class="file-item"
                    v-for="file in fileList"
                    :key="file.id"
                    @click="viewFileChunks(file)"
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
                    <button class="btn-delete-file" @click.stop="confirmDeleteFile(file)">
                      🗑️
                    </button>
                  </div>
                </div>

                <!-- 空文件状态 -->
                <div class="empty-files" v-if="fileList.length === 0">
                  <p>该知识库暂无文件，请上传文档</p>
                </div>
              </div>

              <!-- 切片列表内容 -->
              <div class="tab-content" v-if="activeTab === 'chunks'">
                <!-- 切片搜索和过滤 -->
                <div class="chunks-toolbar">
                  <!-- 当前过滤文件提示 -->
                  <div class="filter-info" v-if="chunkFilterFileId">
                    <span class="filter-label">📄 正在查看：</span>
                    <span class="filter-file-name">{{ getFilterFileName() }}</span>
                    <button class="btn-clear-filter" @click="handleFileFilter(null)">✕ 清除过滤</button>
                  </div>

                  <div class="chunk-search-box">
                    <span class="search-icon">🔍</span>
                    <input
                      v-model="chunkSearchKeyword"
                      type="text"
                      placeholder="搜索切片内容..."
                      @keyup.enter="handleChunkSearch"
                    />
                  </div>
                  <div class="file-filter-list">
                    <span
                      class="file-filter-tag"
                      :class="{ active: chunkFilterFileId === null }"
                      @click="handleFileFilter(null)"
                    >
                      全部
                    </span>
                    <span
                      class="file-filter-tag"
                      :class="{ active: chunkFilterFileId === file.id }"
                      v-for="file in fileList"
                      :key="'filter-' + file.id"
                      @click="handleFileFilter(file.id)"
                    >
                      {{ file.file_name }}
                    </span>
                  </div>
                </div>

                <!-- 切片列表 -->
                <div
                  class="chunk-list"
                  ref="chunkListRef"
                  @scroll="handleChunkScroll"
                >
                  <div class="chunk-item" v-for="chunk in chunkList" :key="chunk.id">
                    <div class="chunk-header">
                      <span class="chunk-file-name">📄 {{ chunk.file_name || '未知文件' }}</span>
                      <span class="chunk-id">{{ chunk.id }}</span>
                    </div>
                    <div class="chunk-content">{{ chunk.document }}</div>
                    <div class="chunk-meta" v-if="chunk.cmetadata">
                      <span v-for="(value, key) in chunk.cmetadata" :key="key">
                        {{ key }}: {{ typeof value === 'object' ? JSON.stringify(value) : value }}
                      </span>
                    </div>
                  </div>

                  <!-- 加载更多提示 -->
                  <div class="load-more" v-if="!chunkLoading && chunkList.length > 0">
                    <span v-if="!hasMoreChunks">已加载全部 {{ chunkTotal }} 条切片</span>
                    <span v-else>滚动加载更多...</span>
                  </div>

                  <!-- 加载中状态 -->
                  <div class="chunk-loading" v-if="chunkLoading">
                    <div class="loading-spinner-small"></div>
                    <span>加载中...</span>
                  </div>
                </div>

                <!-- 空切片状态 -->
                <div class="empty-files" v-if="chunkList.length === 0 && !chunkLoading">
                  <p>暂无切片数据</p>
                </div>
              </div>
            </div>

            <!-- 最右侧：知识库信息 -->
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
        <div class="kb-detail-main empty-selected" v-else>
          <div class="empty-content">
            <div class="empty-icon">👈</div>
            <p>请在左侧选择一个知识库</p>
          </div>
        </div>
      </div>
    </div>

    <!-- 新建知识库弹窗 -->
    <div class="modal-overlay" v-if="showCreateModal" @click.self="closeCreateModal">
      <div class="modal-content" @click.stop>
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
              rows="3"
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
              <label>文本预处理模型</label>
              <input v-model="createForm.text_process_model" type="text" />
            </div>
            <div class="form-item">
              <label>图片理解模型</label>
              <input v-model="createForm.image_understand_model" type="text" />
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

// 左侧边栏状态
const isLeftSidebarCollapsed = ref(false)
const isUserMenuExpanded = ref(false)

// 导航状态
const activeNav = ref('knowledge')

// 用户信息
const username = ref('用户')
const userInitial = computed(() => {
  return username.value.charAt(0).toUpperCase()
})

// 知识库状态
const loading = ref(false)
const searchKeyword = ref('')
const kbList = ref([])
const selectedKb = ref(null)
const fileList = ref([])
const showCreateModal = ref(false)
const creating = ref(false)

// 切片列表相关状态
const activeTab = ref('files') // 'files' | 'chunks'
const chunkList = ref([])
const chunkSearchKeyword = ref('')
const chunkFilterFileId = ref(null)
const chunkLoading = ref(false)
const chunkPage = ref(1)
const chunkPageSize = ref(20)
const chunkTotal = ref(0)
const hasMoreChunks = ref(true) // 是否还有更多数据
const chunkListRef = ref(null) // 切片列表 DOM 引用

// 创建表单
const createForm = ref({
  name: '',
  description: '',
  embedding_model: 'text-embedding-v4',
  search_model: 'qwen-max',
  text_process_model: '',
  image_understand_model: '',
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

// 左侧边栏切换
const toggleLeftSidebar = () => {
  isLeftSidebarCollapsed.value = !isLeftSidebarCollapsed.value
}

// 切换用户菜单
const toggleUserMenu = () => {
  isUserMenuExpanded.value = !isUserMenuExpanded.value
}

// 导航点击
const handleNavClick = (nav) => {
  activeNav.value = nav
  if (nav === 'portal') {
    // 点击门户跳转到客户端主页
    window.location.href = '/'
  } else if (nav === 'workbench') {
    // 回到工作台（主页）
    router.push('/')
  } else if (nav === 'flow-editor') {
    // 跳转到应用编排（创建新应用）
    router.push('/workflow/create')
  } else if (nav === 'knowledge') {
    // 当前已经是知识库页面
  }
}

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
      kbList.value = response.data.data.items || []
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
    text_process_model: '',
    image_understand_model: '',
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
      showToast('创建成功', 'success')
    } else {
      showToast(response.data.msg || '创建失败', 'error')
    }
  } catch (error) {
    console.error('创建知识库失败:', error)
    showToast('创建知识库失败', 'error')
  } finally {
    creating.value = false
  }
}

// 切换Tab
const switchTab = async (tab) => {
  activeTab.value = tab
  if (tab === 'chunks' && selectedKb.value) {
    await loadChunkList()
  }
}

// 选择知识库
const selectKb = async (item) => {
  selectedKb.value = item
  activeTab.value = 'files'
  chunkList.value = []
  await loadFileList(item.uuid)
}

// 加载文件列表
const loadFileList = async (knowledgeUuid) => {
  if (!knowledgeUuid) return
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.get(`/api/knowledge/document/list/${knowledgeUuid}`, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (response.data.success && Array.isArray(response.data.data)) {
      fileList.value = response.data.data
    }
  } catch (error) {
    console.error('加载文件列表失败:', error)
  }
}

// 加载切片列表（append: 是否追加模式）
const loadChunkList = async (append = false) => {
  if (!selectedKb.value) return
  if (append && !hasMoreChunks.value) return // 追加模式但没有更多数据时直接返回

  chunkLoading.value = true
  try {
    const token = localStorage.getItem('access_token')
    const response = await axios.post('/api/knowledge/chunks/list', {
      knowledge_uuid: selectedKb.value.uuid,
      file_id: chunkFilterFileId.value,
      keyword: chunkSearchKeyword.value || undefined,
      page: chunkPage.value,
      page_size: chunkPageSize.value
    }, {
      headers: { Authorization: `Bearer ${token}` }
    })
    if (response.data.success && response.data.data) {
      const newItems = response.data.data.items || []
      const total = response.data.data.total || 0

      if (append) {
        // 追加模式：去重后合并
        const existingIds = new Set(chunkList.value.map(c => c.id))
        const uniqueNewItems = newItems.filter(c => !existingIds.has(c.id))
        chunkList.value = [...chunkList.value, ...uniqueNewItems]
      } else {
        // 覆盖模式
        chunkList.value = newItems
      }

      chunkTotal.value = total
      // 判断是否还有更多数据
      hasMoreChunks.value = chunkList.value.length < total
    }
  } catch (error) {
    console.error('加载切片列表失败:', error)
  } finally {
    chunkLoading.value = false
  }
}

// 加载更多切片
const loadMoreChunks = async () => {
  if (chunkLoading.value || !hasMoreChunks.value) return
  chunkPage.value++
  await loadChunkList(true)
}

// 搜索切片
const handleChunkSearch = () => {
  chunkPage.value = 1
  hasMoreChunks.value = true
  loadChunkList(false)
}

// 按文件过滤切片
const handleFileFilter = (fileId) => {
  chunkFilterFileId.value = chunkFilterFileId.value === fileId ? null : fileId
  chunkPage.value = 1
  hasMoreChunks.value = true
  loadChunkList(false)
}

// 点击文件查看该文件的所有切片
const viewFileChunks = (file) => {
  activeTab.value = 'chunks'
  chunkFilterFileId.value = file.id
  chunkPage.value = 1
  hasMoreChunks.value = true
  loadChunkList(false)
}

// 获取当前过滤的文件名
const getFilterFileName = () => {
  if (!chunkFilterFileId.value) return ''
  const file = fileList.value.find(f => f.id === chunkFilterFileId.value)
  return file?.file_name || '未知文件'
}

// 滚动事件处理
const handleChunkScroll = (e) => {
  const target = e.target
  // 距离底部小于 100px 时触发加载更多
  if (target.scrollHeight - target.scrollTop - target.clientHeight < 100) {
    loadMoreChunks()
  }
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

// 上传文件相关状态
const fileInputRef = ref(null)
const uploading = ref(false)
const uploadProgress = ref(0)

// 触发文件选择
const handleUploadFile = () => {
  if (!selectedKb.value) {
    alert('请先选择一个知识库')
    return
  }
  fileInputRef.value?.click()
}

// 处理文件选择
const handleFileSelect = async (event) => {
  const file = event.target.files[0]
  if (!file) return

  if (!selectedKb.value) {
    alert('请先选择一个知识库')
    return
  }

  // 校验文件大小
  if (file.size > 50 * 1024 * 1024) {
    alert('文件大小不能超过 50MB')
    return
  }

  // 开始上传
  uploading.value = true
  uploadProgress.value = 0

  try {
    const token = localStorage.getItem('access_token')
    const formData = new FormData()
    formData.append('file', file)
    formData.append('chunk_size', 500)
    formData.append('chunk_overlap', 50)

    const response = await axios.post(
      `/api/document/upload/${selectedKb.value.uuid}`,
      formData,
      {
        headers: {
          'Authorization': `Bearer ${token}`,
          'Content-Type': 'multipart/form-data'
        },
        onUploadProgress: (progressEvent) => {
          if (progressEvent.total) {
            uploadProgress.value = Math.round((progressEvent.loaded * 100) / progressEvent.total)
          }
        }
      }
    )

    if (response.data.success) {
      alert(`上传成功！文件已切分为 ${response.data.data.chunk_count} 个切片`)
      // 刷新文件列表和切片列表
      await loadFileList(selectedKb.value.uuid)
      if (activeTab.value === 'chunks') {
        await loadChunkList()
      }
    } else {
      alert(`上传失败：${response.data.msg}`)
    }
  } catch (error) {
    console.error('文件上传失败:', error)
    alert(`上传失败：${error.response?.data?.msg || error.message}`)
  } finally {
    uploading.value = false
    uploadProgress.value = 0
    // 清空文件选择
    if (fileInputRef.value) {
      fileInputRef.value.value = ''
    }
  }
}

// 删除文件确认
const confirmDeleteFile = async (file) => {
  if (!selectedKb.value) return
  if (confirm(`确认删除文件 "${file.file_name}"？`)) {
    try {
      const token = localStorage.getItem('access_token')
      await axios.delete('/api/document/delete', {
        headers: { Authorization: `Bearer ${token}` },
        data: {
          knowledge_uuid: selectedKb.value.uuid,
          document_id: file.id
        }
      })
      showToast('删除成功', 'success')
      await loadFileList(selectedKb.value.uuid)
    } catch (error) {
      console.error('删除文件失败:', error)
      showToast('删除失败', 'error')
    }
  }
}

// 删除知识库确认
const confirmDeleteKb = async () => {
  if (!selectedKb.value) return
  if (confirm(`确认删除知识库 "${selectedKb.value.name}"？\n删除后无法恢复，向量表也会被删除。`)) {
    try {
      const token = localStorage.getItem('access_token')
      await axios.post('/api/knowledge/delete', {
        ids: [selectedKb.value.id]
      }, {
        headers: { Authorization: `Bearer ${token}` }
      })
      showToast('删除成功', 'success')
      selectedKb.value = null
      fileList.value = []
      await loadKbList()
    } catch (error) {
      console.error('删除知识库失败:', error)
      showToast('删除失败', 'error')
    }
  }
}

// 退出登录
const handleLogout = async () => {
  try {
    const token = localStorage.getItem('access_token')
    await axios.post('/api/auth/logout', {}, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
  } catch (error) {
    console.error('退出登录失败:', error)
  } finally {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('token_type')
    localStorage.removeItem('user_info')
    window.location.href = '/login'
  }
}

// Toast 提示
const showToast = (message, type = 'success') => {
  alert(message)
}

// 页面加载
onMounted(() => {
  // 获取用户信息
  const userInfo = localStorage.getItem('user_info')
  if (userInfo) {
    const user = JSON.parse(userInfo)
    username.value = user.name || user.username || '用户'
  }
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
  --primary-color: #6B4EED;
  --primary-hover: #8B6EF0;
  --background-color: #f5f5f5;
  --sidebar-bg: #f8f9fa;
  --text-primary: #374151;
  --text-secondary: #9ca3af;
  --border-color: #e5e7eb;
  --hover-bg: #f9fafb;
  --radius: 8px;
  --radius-lg: 12px;
  --shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.kb-page-container {
  display: flex;
  height: 100%;
  min-height: 0;
  background: var(--background-color);
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  width: 100%;
}

/* 左侧导航栏 */
.left-sidebar {
  display: flex;
  flex-direction: column;
  width: 200px;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border-color);
  flex-shrink: 0;
  transition: all 0.3s ease;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
}

.left-sidebar.collapsed {
  width: 60px;
}

/* Logo区域 */
.logo-section {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 16px 12px;
  border-bottom: 1px solid var(--border-color);
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  flex: 1;
}

.logo-image {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  object-fit: cover;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--primary-color);
}

.toggle-btn {
  width: 28px;
  height: 28px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.toggle-btn:hover {
  background: var(--hover-bg);
  color: var(--text-primary);
}

/* 导航菜单 */
.nav-menu {
  flex: 1;
  padding: 12px 8px;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.nav-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 8px 6px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-primary);
}

.nav-item:hover {
  background: var(--hover-bg);
}

.nav-item.active {
  background: var(--primary-color);
  color: white;
}

.nav-icon {
  font-size: 18px;
  flex-shrink: 0;
  text-align: center;
  line-height: 1;
}

.nav-text {
  font-size: 10px;
  font-weight: 500;
  white-space: nowrap;
}

/* 底部用户区域 */
.user-section {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px;
  border-top: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s;
}

.user-section:hover {
  background: var(--hover-bg);
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-details {
  flex: 1;
  overflow: hidden;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.expand-icon {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 用户菜单 */
.user-menu {
  position: absolute;
  bottom: 70px;
  left: 12px;
  right: 12px;
  background: var(--sidebar-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 4px 0;
  z-index: 10;
}

.user-menu .menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
  cursor: pointer;
  transition: all 0.2s;
}

.user-menu .menu-item:hover {
  background: var(--hover-bg);
}

.user-menu .menu-icon {
  font-size: 16px;
}

.user-menu .menu-text {
  font-size: 14px;
  color: var(--text-primary);
}

/* 右侧主内容 */
.kb-main-content {
  flex: 1;
  overflow: hidden;
}

.kb-container {
  display: flex;
  flex-direction: row;
  width: 100%;
  height: 100%;
  min-height: 0;
  background: var(--background-color);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

/* 左侧知识库列表 */
.kb-list-sidebar {
  width: 320px;
  min-width: 320px;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  min-height: 0;
  height: 100%;
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
  background: white;
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
  background: white;
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
.kb-detail-main {
  flex: 1;
  display: flex;
  flex-direction: column;
  overflow: hidden;
  min-height: 0;
  height: 100%;
}

.detail-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
}

.detail-header h2 {
  margin: 0;
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
}

.detail-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.files-area {
  flex: 1;
  padding: 16px 24px;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 8px;
}

.btn-upload:disabled {
  opacity: 0.7;
  cursor: not-allowed;
}

/* Tab 导航 */
.tabs-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  flex-shrink: 0;
}

.tabs-nav {
  display: flex;
  gap: 8px;
}

.tab-item {
  padding: 6px 16px;
  border-radius: 6px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-secondary);
  transition: all 0.2s;
}

.tab-item:hover {
  background: var(--hover-bg);
}

.tab-item.active {
  background: var(--primary-color);
  color: white;
}

.tab-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-height: 0;
  overflow: hidden;
}

/* 切片工具栏 */
.chunks-toolbar {
  display: flex;
  flex-direction: column;
  gap: 12px;
  margin-bottom: 16px;
  padding-bottom: 16px;
  border-bottom: 1px solid var(--border-color);
  flex-shrink: 0;
}

.chunk-search-box {
  display: flex;
  align-items: center;
  gap: 6px;
  background: white;
  padding: 8px 10px;
  border-radius: var(--radius);
  border: 1px solid var(--border-color);
}

.chunk-search-box input {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 14px;
  color: var(--text-primary);
}

.file-filter-list {
  display: flex;
  gap: 6px;
  flex-wrap: wrap;
}

.file-filter-tag {
  padding: 4px 10px;
  border-radius: 4px;
  background: white;
  border: 1px solid var(--border-color);
  font-size: 12px;
  color: var(--text-secondary);
  cursor: pointer;
  transition: all 0.2s;
}

.file-filter-tag:hover {
  border-color: var(--primary-color);
  color: var(--primary-color);
}

.file-filter-tag.active {
  background: var(--primary-color);
  border-color: var(--primary-color);
  color: white;
}

/* 过滤信息显示 */
.filter-info {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: #f0f7ff;
  border: 1px solid #d0e3ff;
  border-radius: 6px;
  margin-bottom: 12px;
}

.filter-label {
  font-size: 13px;
  color: #666;
}

.filter-file-name {
  font-size: 14px;
  font-weight: 500;
  color: var(--primary-color);
}

.btn-clear-filter {
  margin-left: auto;
  padding: 4px 10px;
  background: white;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 12px;
  color: #666;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-clear-filter:hover {
  background: #f5f5f5;
  border-color: #bbb;
  color: #333;
}

/* 切片列表 */
.chunk-list {
  display: flex;
  flex-direction: column;
  gap: 12px;
  overflow-y: auto;
  max-height: calc(100vh - 320px);
  padding-right: 8px;
}

/* 加载更多提示 */
.load-more {
  text-align: center;
  padding: 20px;
  color: var(--text-secondary);
  font-size: 13px;
}

.chunk-item {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  padding: 12px 16px;
}

.chunk-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.chunk-file-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--primary-color);
}

.chunk-id {
  font-size: 11px;
  color: var(--text-secondary);
  font-family: monospace;
}

.chunk-content {
  font-size: 14px;
  color: var(--text-primary);
  line-height: 1.6;
  word-break: break-word;
  white-space: pre-wrap;
  margin-bottom: 8px;
}

.chunk-meta {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  padding-top: 8px;
  border-top: 1px dashed var(--border-color);
  font-size: 11px;
  color: var(--text-secondary);
}

/* 加载状态 */
.chunk-loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 40px;
  color: var(--text-secondary);
}

.loading-spinner-small {
  width: 20px;
  height: 20px;
  border: 2px solid var(--border-color);
  border-top-color: var(--primary-color);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
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
  overflow-y: auto;
  max-height: calc(100vh - 280px);
  padding-right: 8px;
}

.file-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: var(--sidebar-bg);
  border-radius: var(--radius);
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s;
}

.file-item:hover {
  background: white;
  border-color: var(--primary-color);
  transform: translateX(2px);
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
  width: 280px;
  background: var(--sidebar-bg);
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
  background: white;
  padding: 4px 6px;
  border-radius: 4px;
}

.action-buttons {
  margin-top: 24px;
  padding-top: 16px;
  border-top: 1px solid var(--border-color);
}

.btn-delete-kb {
  width: 100%;
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
  background: rgba(0, 0, 0, 0.5);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 1000;
}

.modal-content {
  background: white;
  border-radius: var(--radius-lg);
  width: 500px;
  max-width: 90vw;
  overflow: hidden;
}

.modal-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
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
  transition: all 0.2s;
}

.form-item input:focus,
.form-item textarea:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(107, 78, 237, 0.1);
}

.form-item textarea {
  resize: vertical;
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
  padding: 16px 24px;
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
@media (max-width: 1200px) {
  .info-sidebar {
    display: none;
  }
}

@media (max-width: 768px) {
  .left-sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 1000;
  }
}
</style>
