<template>
  <div class="home-container">
    <!-- 左侧导航栏 -->
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

    <!-- 中间导航栏 -->
    <div class="middle-sidebar" v-if="activeNav === 'workbench'">
      <div class="middle-sidebar-header">
        <h3>工作台</h3>
      </div>
      <div class="category-list">
        <div
          class="category-item"
          :class="{ active: activeCategory === 'agent' }"
          @click="handleCategoryClick('agent')"
        >
          <span class="category-icon">🤖</span>
          <span class="category-text">Agent</span>
        </div>
        <div
          class="category-item"
          :class="{ active: activeCategory === 'my-tools' }"
          @click="handleCategoryClick('my-tools')"
        >
          <span class="category-icon">🧰</span>
          <span class="category-text">我的工具</span>
        </div>
        <div
          class="category-item"
          :class="{ active: activeCategory === 'system-tools' }"
          @click="handleCategoryClick('system-tools')"
        >
          <span class="category-icon">🔧</span>
          <span class="category-text">系统工具</span>
        </div>
        <div
          class="category-item"
          :class="{ active: activeCategory === 'template-market' }"
          @click="handleCategoryClick('template-market')"
        >
          <span class="category-icon">📦</span>
          <span class="category-text">模版市场</span>
        </div>
        <div
          class="category-item"
          :class="{ active: activeCategory === 'mcp' }"
          @click="handleCategoryClick('mcp')"
        >
          <span class="category-icon">🔌</span>
          <span class="category-text">MCP服务</span>
        </div>
      </div>
    </div>

    <!-- 右侧内容区域 -->
    <div class="content-area">
      <!-- Agent 列表 -->
      <div v-if="activeCategory === 'agent'" class="agent-content">
        <div class="content-header">
          <h2>我的 Agent</h2>
          <div class="header-actions">
            <button class="btn-new-chat" @click="openCreateModal('chat')">
              <span>+</span>
              <span>新建对话式Agent</span>
            </button>
            <button class="btn-new-workflow" @click="openCreateModal('workflow')">
              <span>+</span>
              <span>新建工作流Agent</span>
            </button>
          </div>
        </div>
        <div class="agent-grid" v-loading="loadingAgents">
          <div
            v-for="agent in agentList"
            :key="agent.id"
            class="agent-card"
            @click="openAgent(agent)"
          >
            <div class="agent-icon" :style="{ background: getDefaultColor(agent.type) }">
              {{ agent.icon || '🤖' }}
            </div>
            <div class="agent-info">
              <h3 class="agent-name">{{ agent.name }}</h3>
              <p class="agent-description">{{ agent.description || '智能对话应用' }}</p>
            </div>
          </div>
        </div>
        <div v-if="!loadingAgents && agentList.length === 0" class="empty-state">
          <div class="empty-icon">📭</div>
          <p>暂无 Agent 应用</p>
        </div>
      </div>

      <!-- 其他分类占位 -->
      <div v-else class="empty-content">
        <div class="placeholder">
          <p>{{ getPlaceholderText() }}</p>
        </div>
      </div>
    </div>

    <!-- 创建 Agent 弹窗 -->
    <div v-if="showCreateModal" class="modal-overlay" @click="closeCreateModal">
      <div class="modal-content" @click.stop>
        <div class="modal-header">
          <h3>新建{{ modalTitle }}</h3>
          <button class="close-btn" @click="closeCreateModal">✕</button>
        </div>
        <div class="modal-body">
          <div class="form-item">
            <label>Agent 名称 <span class="required">*</span></label>
            <input
              v-model="createForm.name"
              type="text"
              placeholder="请输入Agent名称"
            />
          </div>
          <div class="form-item">
            <label>Agent 描述</label>
            <textarea
              v-model="createForm.description"
              placeholder="请输入Agent描述（可选）"
              rows="3"
            ></textarea>
          </div>
          <div class="form-item">
            <label>图标</label>
            <input
              v-model="createForm.icon"
              type="text"
              placeholder="emoji图标，例如 🤖"
            />
          </div>
          <div class="form-item">
            <label class="checkbox-label">
              <input v-model="createForm.is_public" type="checkbox">
              <span>公开分享</span>
            </label>
          </div>
        </div>
        <div class="modal-footer">
          <button class="cancel-btn" @click="closeCreateModal">取消</button>
          <button class="confirm-btn" @click="handleCreate" :disabled="creating">
            {{ creating ? '创建中...' : '确认创建' }}
          </button>
        </div>

        <!-- Toast -->
        <div v-if="toastVisible" class="toast" :class="toastClass">
          {{ toastMessage }}
        </div>
      </div>
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
const activeNav = ref('workbench')
const activeCategory = ref('agent')

// Agent 列表
const agentList = ref([])
const loadingAgents = ref(false)

// 创建弹窗状态
const showCreateModal = ref(false)
const creating = ref(false)
const targetType = ref('') // 'chat' | 'workflow'

// 创建表单
const createForm = ref({
  name: '',
  description: '',
  icon: '🤖',
  is_public: false
})

// Toast
const toastVisible = ref(false)
const toastMessage = ref('')
const toastClass = ref('success')

// 用户信息
const username = ref('用户')
const userInitial = computed(() => {
  return username.value.charAt(0).toUpperCase()
})

// 计算弹窗标题
const modalTitle = computed(() => {
  return targetType.value === 'chat' ? '对话式Agent' : '工作流Agent'
})

// 页面加载
onMounted(() => {
  // 获取用户信息
  const userInfo = localStorage.getItem('user_info')
  if (userInfo) {
    const user = JSON.parse(userInfo)
    username.value = user.name || user.username || '用户'
  }

  // 如果选中工作台，加载 Agent 列表
  if (activeNav.value === 'workbench') {
    loadAgentList()
  }
})

// 加载 Agent 列表
const loadAgentList = async () => {
  loadingAgents.value = true
  try {
    const token = localStorage.getItem('access_token')
    const response = await fetch('/api/app/list', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      if (data.success && Array.isArray(data.data)) {
        agentList.value = data.data
      }
    }
  } catch (error) {
    console.error('加载 Agent 列表失败:', error)
  } finally {
    loadingAgents.value = false
  }
}

// 左侧边栏切换
const toggleLeftSidebar = () => {
  isLeftSidebarCollapsed.value = !isLeftSidebarCollapsed.value
}

// 导航点击
const handleNavClick = (nav) => {
  activeNav.value = nav
  if (nav === 'portal') {
    // 点击门户跳转到客户端主页
    window.location.href = '/'
  } else if (nav === 'workbench') {
    // 加载 Agent 列表
    loadAgentList()
  } else if (nav === 'flow-editor') {
    // 跳转到应用编排（创建新应用）
    openCreateModal('workflow')
  }
}

// 分类点击
const handleCategoryClick = (category) => {
  activeCategory.value = category
  if (category === 'agent') {
    loadAgentList()
  }
}

// 打开创建弹窗
const openCreateModal = (type) => {
  targetType.value = type
  // 重置表单
  createForm.value = {
    name: '',
    description: '',
    icon: '🤖',
    is_public: false
  }
  showCreateModal.value = true
}

// 关闭创建弹窗
const closeCreateModal = () => {
  showCreateModal.value = false
  creating.value = false
}

// 显示 Toast
const showToast = (message, type = 'success') => {
  toastMessage.value = message
  toastClass.value = type
  toastVisible.value = true
  setTimeout(() => {
    toastVisible.value = false
  }, 3000)
}

// 确认创建
const handleCreate = async () => {
  if (!createForm.value.name.trim()) {
    showToast('请输入Agent名称', 'error')
    return
  }

  creating.value = true
  try {
    // 构建请求数据
    const requestData = {
      name: createForm.value.name.trim(),
      description: createForm.value.description || null,
      icon: createForm.value.icon || '🤖',
      is_public: createForm.value.is_public,
      type: targetType.value === 'workflow' ? 'WORKFLOW' : 'CHAT'
    }

    // 调用 create 接口
    const response = await axios.post('/api/app/create', requestData)
    if (response.data.success) {
      showToast('创建成功', 'success')
      closeCreateModal()
      // 刷新列表
      loadAgentList()
      // 创建成功后跳转到编辑页面
      const uuid = response.data.data.uuid
      if (targetType.value === 'workflow') {
        router.push(`/workflow/edit/${uuid}`)
      } else {
        router.push(`/chatagent/edit/${uuid}`)
      }
    } else {
      showToast(response.data.msg || '创建失败', 'error')
    }
  } catch (error) {
    console.error('创建失败:', error)
    showToast(error.response?.data?.msg || '网络错误', 'error')
  } finally {
    creating.value = false
  }
}

// 根据 Agent 类型打开对应编辑页面
const openAgent = (agent) => {
  // 使用 uuid (UUID) 进行路由和请求
  if (agent.type === 'WORKFLOW') {
    // 工作流 Agent → 跳转到可视化画板编辑
    router.push(`/workflow/edit/${agent.uuid}`)
  } else if (agent.type === 'CHAT') {
    // 对话式 Agent → 跳转到AI配置页面编辑
    router.push(`/chatagent/edit/${agent.uuid}`)
  } else {
    // 默认 → 直接打开对话
    router.push(`/app/chat/${agent.uuid}`)
  }
}

// 切换用户菜单
const toggleUserMenu = () => {
  isUserMenuExpanded.value = !isUserMenuExpanded.value
}

// 获取占位文字
const getPlaceholderText = () => {
  const placeholders = {
    'agent': '请点击左侧 Agent 分类查看应用列表',
    'my-tools': '我的工具 - 开发中',
    'system-tools': '系统工具 - 开发中',
    'template-market': '模版市场 - 开发中',
    'mcp': 'MCP 服务 - 开发中'
  }
  return placeholders[activeCategory.value] || '开发中...'
}

// 获取默认颜色
function getDefaultColor(type) {
  const colors = {
    WORKFLOW: 'linear-gradient(135deg, #6B4EED 0%, #8b5cf6 100%)',
    CHAT: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)',
    ai: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    workflow: 'linear-gradient(135deg, #6B4EED 0%, #8b5cf6 100%)',
    chat: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
  }
  return colors[type] || 'linear-gradient(135deg, #6B4EED 0%, #8b5cf6 100%)'
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

// Axios拦截器
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

axios.interceptors.response.use(
  response => {
    return response
  },
  error => {
    if (error.response && error.response.status === 401) {
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('token_type')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)
</script>

<style scoped>
/* 全局样式变量 */
:root {
  --primary-color: #6B4EED;
  --primary-hover: #8B6EF0;
  --background-color: #f5f5f5;
  --sidebar-bg: #f8f9fa;
  --text-primary: #374151;
  --text-secondary: #9ca3af;
  --border-color: #e5e7eb;
  --hover-bg: #f9fafb;
}

.home-container {
  display: flex;
  height: 100vh;
  background: var(--background-color);
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  width: 100vw;
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
  box-shadow: 0 0 10px rgba(0, 0, 0, 0, 0.05);
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
  align-items: center;
  gap: 12px;
  padding: 10px 12px;
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
  width: 24px;
  text-align: center;
}

.nav-text {
  font-size: 14px;
  font-weight: 500;
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
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0, 0.1);
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

/* 中间边栏 */
.middle-sidebar {
  width: 180px;
  background: white;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
}

.middle-sidebar-header {
  padding: 20px 16px 16px;
  border-bottom: 1px solid var(--border-color);
}

.middle-sidebar-header h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.category-list {
  flex: 1;
  padding: 12px;
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.category-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 12px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-primary);
}

.category-item:hover {
  background: var(--hover-bg);
}

.category-item.active {
  background: var(--primary-color);
  color: white;
}

.category-icon {
  font-size: 18px;
  flex-shrink: 0;
}

.category-text {
  font-size: 14px;
  font-weight: 500;
}

/* 右侧内容区域 */
.content-area {
  flex: 1;
  overflow-y: auto;
  background: var(--background-color);
  padding: 20px;
}

/* Agent 内容 */
.agent-content {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.content-header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content-header h2 {
  margin: 0;
  font-size: 24px;
  font-weight: 600;
  color: var(--text-primary);
}

.header-actions {
  display: flex;
  gap: 12px;
}

.btn-new-chat,
.btn-new-workflow {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 10px 16px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  border: none;
  transition: all 0.2s;
}

.btn-new-chat {
  background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
  color: white;
}

.btn-new-workflow {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  color: white;
}

.btn-new-chat:hover,
.btn-new-workflow:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(107, 78, 237, 0.3);
}

.header-actions span:first-child {
  font-size: 18px;
  line-height: 1;
}

.agent-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  align-content: start;
}

.agent-card {
  background: white;
  border-radius: 12px;
  padding: 20px;
  border: 1px solid var(--border-color);
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  gap: 16px;
  align-items: flex-start;
}

.agent-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(107, 78, 237, 0.15);
  border-color: var(--primary-color);
}

.agent-icon {
  width: 48px;
  height: 48px;
  border-radius: 12px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 24px;
  flex-shrink: 0;
}

.agent-info {
  flex: 1;
  overflow: hidden;
}

.agent-name {
  margin: 0 0 6px;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.agent-description {
  margin: 0;
  font-size: 13px;
  color: var(--text-secondary);
  overflow: hidden;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  line-height: 1.4;
}

/* 空状态 */
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 300px;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
  opacity: 0.5;
}

.empty-state p {
  margin: 0;
  font-size: 16px;
}

/* 空内容占位 */
.empty-content {
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
}

.empty-content .placeholder {
  text-align: center;
  color: var(--text-secondary);
}

.empty-content .placeholder p {
  font-size: 16px;
}

/* 响应式 */
@media (max-width: 1024px) {
  .left-sidebar {
    width: 180px;
  }
  .middle-sidebar {
    width: 160px;
  }
  .agent-grid {
    grid-template-columns: repeat(auto-fill, minmax(240px, 1fr));
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
  .left-sidebar.collapsed {
    left: -60px;
  }
  .middle-sidebar {
    width: 140px;
  }
  .content-area {
    padding: 12px;
  }
  .agent-grid {
    grid-template-columns: 1fr;
    gap: 12px;
  }
}

/* 创建弹窗 */
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
  border-bottom: 1px solid var(--border-color);
}

.modal-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
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
  background: var(--hover-bg);
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
  color: var(--text-primary);
  margin-bottom: 8px;
}

.form-item .required {
  color: #ef4444;
}

.form-item input,
.form-item textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
  box-sizing: border-box;
}

.form-item input:focus,
.form-item textarea:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(107, 78, 237, 0.1);
}

.form-item input::placeholder,
.form-item textarea::placeholder {
  color: var(--text-secondary);
}

.form-item textarea {
  resize: vertical;
}

.form-item .checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
}

.form-item .checkbox-label input {
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
  border: 1px solid var(--border-color);
  background: white;
  border-radius: 8px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.2s;
}

.cancel-btn:hover {
  background: var(--hover-bg);
}

.confirm-btn {
  padding: 10px 24px;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
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
  box-shadow: 0 4px 12px rgba(107, 78, 237, 0.35);
}

.confirm-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

/* Toast */
.toast {
  position: fixed;
  bottom: 24px;
  left: 50%;
  transform: translateX(-50%);
  padding: 12px 24px;
  border-radius: 8px;
  color: white;
  font-size: 14px;
  z-index: 1001;
  animation: fadeInUp 0.3s ease;
}

.toast.success {
  background: #10b981;
}

.toast.error {
  background: #ef4444;
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
