<template>
  <div class="workflow-chat-container">
    <!-- 最左侧主导航 (和首页保持一致) -->
    <div class="left-sidebar" :class="{ collapsed: isLeftSidebarCollapsed }">
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

    <!-- 中间配置面板 (编辑模式显示) -->
    <div class="config-panel" v-if="isEditMode">
      <div class="config-panel-header">
        <h3 class="config-title">{{ isCreating ? '新建对话式Agent' : '编辑Agent配置' }}</h3>
      </div>

      <div class="config-panel-content">
        <!-- Agent基本信息 -->
        <div class="config-section">
          <h4 class="section-title">基本信息</h4>

          <div class="config-item">
            <label class="config-label">Agent名称 <span class="required">*</span></label>
            <input
              class="config-input"
              v-model="basicConfig.name"
              type="text"
              placeholder="请输入Agent名称"
            />
          </div>

          <div class="config-item">
            <label class="config-label">Agent描述</label>
            <textarea
              class="config-textarea"
              v-model="basicConfig.description"
              placeholder="请输入Agent描述"
              rows="3"
            ></textarea>
          </div>

          <div class="config-item">
            <label class="config-label">图标</label>
            <input
              class="config-input"
              v-model="basicConfig.icon"
              type="text"
              placeholder="emoji图标，例如 🤖"
            />
          </div>

          <div class="config-item">
            <label class="checkbox-label">
              <input v-model="basicConfig.is_public" type="checkbox">
              <span>公开分享</span>
            </label>
          </div>
        </div>

        <!-- AI配置 -->
        <div class="config-section">
          <h4 class="section-title">AI 配置</h4>

          <div class="config-item">
            <label class="config-label">AI 模型</label>
            <select class="config-select" v-model="llmConfig.model">
              <option value="gpt-4o">gpt-4o</option>
              <option value="gpt-4">gpt-4</option>
              <option value="gpt-3.5-turbo">gpt-3.5-turbo</option>
              <option value="qwen-max">qwen-max</option>
              <option value="qwen-plus">qwen-plus</option>
              <option value="qwen-turbo">qwen-turbo</option>
            </select>
          </div>

          <div class="config-item">
            <label class="config-label">系统提示词</label>
            <textarea
              class="config-textarea"
              v-model="llmConfig.systemPrompt"
              placeholder="输入系统提示词..."
              rows="6"
            ></textarea>
          </div>

          <div class="config-item">
            <label class="config-label">温度 (Temperature)</label>
            <input
              class="config-input"
              v-model.number="llmConfig.temperature"
              type="number"
              min="0"
              max="2"
              step="0.1"
            />
          </div>

          <div class="config-item">
            <label class="config-label">最大 Tokens</label>
            <input
              class="config-input"
              v-model.number="llmConfig.maxTokens"
              type="number"
              min="128"
              max="4096"
              step="128"
            />
          </div>

          <div class="config-item">
            <label class="config-label">关联知识库</label>
            <input
              class="config-input"
              v-model="llmConfig.knowledgeBase"
              type="text"
              placeholder="可选，关联PGVector知识库集合名"
            />
          </div>

          <div class="config-toggle-item">
            <label class="config-toggle-label">工具调用</label>
            <div class="config-toggle-options">
              <button
                class="toggle-btn-option"
                :class="{ active: toolCalling === 'enabled' }"
                @click="toolCalling = 'enabled'"
              >启用</button>
              <button
                class="toggle-btn-option"
                :class="{ active: toolCalling === 'disabled' }"
                @click="toolCalling = 'disabled'"
              >禁用</button>
            </div>
          </div>

          <div class="config-toggle-item">
            <label class="config-toggle-label">文件上传</label>
            <div class="config-toggle-options">
              <button
                class="toggle-btn-option"
                :class="{ active: fileUpload === 'enabled' }"
                @click="fileUpload = 'enabled'"
              >启用</button>
              <button
                class="toggle-btn-option"
                :class="{ active: fileUpload === 'disabled' }"
                @click="fileUpload = 'disabled'"
              >禁用</button>
            </div>
          </div>

          <div class="config-item">
            <label class="config-label">对话开场白</label>
            <textarea
              class="config-textarea"
              v-model="openingMessage"
              placeholder="对话开始时的欢迎语，留空则不显示"
              rows="3"
            ></textarea>
          </div>

          <div class="config-toggle-item">
            <label class="config-toggle-label">语音播放 (TTS)</label>
            <div class="config-toggle-options">
              <button
                class="toggle-btn-option"
                :class="{ active: ttsEnabled === 'enabled' }"
                @click="ttsEnabled = 'enabled'"
              >启用</button>
              <button
                class="toggle-btn-option"
                :class="{ active: ttsEnabled === 'disabled' }"
                @click="ttsEnabled = 'disabled'"
              >禁用</button>
            </div>
          </div>

          <div class="config-toggle-item">
            <label class="config-toggle-label">语音输入 (ASR)</label>
            <div class="config-toggle-options">
              <button
                class="toggle-btn-option"
                :class="{ active: asrEnabled === 'enabled' }"
                @click="asrEnabled = 'enabled'"
              >启用</button>
              <button
                class="toggle-btn-option"
                :class="{ active: asrEnabled === 'disabled' }"
                @click="asrEnabled = 'disabled'"
              >禁用</button>
            </div>
          </div>

          <div class="config-toggle-item">
            <label class="config-toggle-label">猜你想问</label>
            <div class="config-toggle-options">
              <button
                class="toggle-btn-option"
                :class="{ active: suggestedQuestions === 'enabled' }"
                @click="suggestedQuestions = 'enabled'"
              >启用</button>
              <button
                class="toggle-btn-option"
                :class="{ active: suggestedQuestions === 'disabled' }"
                @click="suggestedQuestions = 'disabled'"
              >禁用</button>
            </div>
          </div>
        </div>

        <div class="config-actions">
          <button class="btn-cancel" @click="goBack">取消</button>
          <button class="btn-save" @click="handleSave" :disabled="saving">
            {{ saving ? '保存中...' : (isCreating ? '创建Agent' : '保存修改') }}
          </button>
        </div>
      </div>
    </div>

    <!-- 右侧聊天预览区域 -->
    <div class="chat-area" :class="{ 'chat-area-narrow': isEditMode }">
      <!-- 对话头部 -->
      <div class="chat-header">
        <h2 class="chat-title">{{ appInfo?.name || (isCreating ? '预览对话' : '编辑Agent') }}</h2>
      </div>

      <!-- 对话消息区域 -->
      <div class="chat-messages" ref="chatMessagesRef">
        <!-- 空状态 -->
        <div class="empty-chat" v-if="messages.length === 0">
          <div class="empty-icon">💬</div>
          <h3 class="empty-title">开始新对话</h3>
          <p class="empty-subtitle" v-if="appInfo">发送消息给 {{ appInfo.name }}</p>
          <p class="empty-subtitle" v-else>保存Agent后即可开始对话</p>
        </div>

        <!-- 消息列表 -->
        <div
          class="message"
          :class="{ 'user-message': msg.role === 'user', 'assistant-message': msg.role === 'assistant' }"
          v-for="(msg, index) in messages"
          :key="index"
        >
          <div class="message-avatar">
            {{ msg.role === 'user' ? userInitial : (appInfo?.icon || '🤖') }}
          </div>
          <div class="message-content">
            <div class="message-text" v-html="formatMessageContent(msg.content)"></div>
            <div class="message-time">{{ msg.time }}</div>
          </div>
        </div>

        <!-- 正在加载提示 -->
        <div class="message assistant-message" v-if="isLoading">
          <div class="message-avatar">
            {{ appInfo?.icon || '🤖' }}
          </div>
          <div class="message-content">
            <div class="message-text typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入区域 -->
      <div class="chat-input-area">
        <div class="input-container">
          <textarea
            class="chat-input"
            placeholder="输入消息，按Enter发送"
            v-model="inputMessage"
            @keydown.enter.exact="handleSendMessage"
            @keydown.enter.shift.prevent="inputMessage += '\n'"
            rows="1"
          ></textarea>

          <div class="input-actions">
            <button
              class="send-btn"
              @click="handleSendMessage"
              :disabled="!inputMessage.trim() || isLoading"
            >
              <span class="send-icon">➤</span>
            </button>
          </div>
        </div>
        <div class="input-hint">按Enter发送，Shift+Enter换行</div>
      </div>
    </div>
  </div>

  <!-- Toast 提示 -->
  <div v-if="toastVisible" class="toast" :class="toastClass">
    {{ toastMessage }}
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const chatMessagesRef = ref(null)
const appId = route.params.uuid || route.params.app_id || route.params.id
const isCreating = route.name === 'ChatAgentCreate'

// State
const inputMessage = ref('')
const messages = ref([])
const isLoading = ref(false)
const appInfo = ref(null)
const saving = ref(false)
// PG primary key id for update
const pgId = ref(null)

// Toast
const toastVisible = ref(false)
const toastMessage = ref('')
const toastClass = ref('success')

// Edit mode detection - we are in edit mode if route is ChatAgentCreate or ChatAgentEdit
const isEditMode = ref(route.name === 'ChatAgentCreate' || route.name === 'ChatAgentEdit')

// Left sidebar navigation (same as Home page)
const isLeftSidebarCollapsed = ref(false)
const isUserMenuExpanded = ref(false)
const activeNav = ref('workbench')

// User info
const username = ref('用户')
const userInitial = computed(() => {
  return username.value.charAt(0).toUpperCase()
})

// Toggle left sidebar
const toggleLeftSidebar = () => {
  isLeftSidebarCollapsed.value = !isLeftSidebarCollapsed.value
}

// Navigation click
const handleNavClick = (nav) => {
  activeNav.value = nav
  if (nav === 'portal') {
    // Click portal goes to home
    router.push('/')
  } else if (nav === 'workbench') {
    // Stay on workbench
    router.push('/')
  } else if (nav === 'flow-editor') {
    // Go to workflow editor create
    router.push('/app/create')
  }
}

// Toggle user menu
const toggleUserMenu = () => {
  isUserMenuExpanded.value = !isUserMenuExpanded.value
}

// Logout
const handleLogout = async () => {
  try {
    const token = localStorage.getItem('access_token')
    await axios.post('/api/auth/logout', {}, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
  } catch (error) {
    console.error('Logout failed:', error)
  } finally {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('token_type')
    localStorage.removeItem('user_info')
    window.location.href = '/login'
  }
}

// Basic config
const basicConfig = ref({
  name: '',
  description: '',
  icon: '🤖',
  is_public: false
})

// LLM config
const llmConfig = ref({
  model: 'qwen-max',
  systemPrompt: 'You are a helpful assistant.',
  temperature: 0.7,
  maxTokens: 2048,
  knowledgeBase: ''
})

// Feature toggles
const toolCalling = ref('disabled')
const fileUpload = ref('disabled')
const ttsEnabled = ref('disabled')
const asrEnabled = ref('disabled')
const suggestedQuestions = ref('disabled')
const openingMessage = ref('')

// 当前应用的 UUID（用于 chat API）
let currentAppUuid = ref('')

// 获取应用信息
const loadAppInfo = async () => {
  try {
    const token = localStorage.getItem('access_token')
    const response = await fetch(`/api/app/${appId}`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      if (data.success && data.data) {
        appInfo.value = {
          id: data.data.pg_id,
          name: data.data.name,
          icon: data.data.icon,
          type: data.data.type,
          description: data.data.description,
          app_id: data.data.app_id,
          config: null
        }
        // 保存pg_id用于更新
        pgId.value = data.data.pg_id
        // 保存app_id用于发送消息
        currentAppUuid.value = data.data.app_id

        // 如果是编辑模式，从顶层字段填充表单（新数据结构：所有配置展开在顶层）
        if (isEditMode.value) {
          // 基本信息直接从顶层读取
          Object.assign(basicConfig.value, {
            name: data.data.name || '',
            description: data.data.description || '',
            icon: data.data.icon || '🤖',
            is_public: data.data.is_public || false
          })

          // LLM 配置从顶层读取
          if (data.data.llmConfig) {
            Object.assign(llmConfig.value, data.data.llmConfig)
          } else if (data.data.nodes && data.data.nodes.length > 0) {
            // 从nodes中提取llm配置（兼容）
            const llmNode = data.data.nodes.find(n => n.type === 'llm')
            if (llmNode && llmNode.config) {
              Object.assign(llmConfig.value, llmNode.config)
            }
          }

          // 功能开关从顶层读取
          fileUpload.value = data.data.enableFileUpload ? 'enabled' : 'disabled'
          ttsEnabled.value = data.data.enableTTS ? 'enabled' : 'disabled'
          asrEnabled.value = data.data.enableASR ? 'enabled' : 'disabled'
          suggestedQuestions.value = data.data.guessedQuestions ? 'enabled' : 'disabled'
          toolCalling.value = data.data.enableToolCall ? 'enabled' : 'disabled'
          openingMessage.value = data.data.openingMessage || ''
        } else if (data.data.nodes && data.data.nodes.length > 0) {
          // 非编辑模式，只需要提取llm配置
          const llmNode = data.data.nodes.find(n => n.type === 'llm')
          if (llmNode && llmNode.config) {
            Object.assign(llmConfig.value, llmNode.config)
          }
        }
      }
    }
  } catch (error) {
    console.error('加载应用信息失败:', error)
    // 如果加载失败，使用占位信息
    appInfo.value = {
      id: parseInt(appId),
      name: `Agent ${appId}`,
      icon: '🤖',
      type: 'chat',
      description: '对话式Agent'
    }
  }
}

// Scroll to bottom of chat
const scrollToBottom = () => {
  nextTick(() => {
    if (chatMessagesRef.value) {
      chatMessagesRef.value.scrollTop = chatMessagesRef.value.scrollHeight
    }
  })
}

// Toggle sidebar
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

// New chat
const handleNewChat = () => {
  messages.value = []
}

// Go back to home
const goBack = () => {
  router.push('/')
}

// Show toast
function showToast(message, type = 'success') {
  toastMessage.value = message
  toastClass.value = type
  toastVisible.value = true
  setTimeout(() => {
    toastVisible.value = false
  }, 3000)
}

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

// 格式化消息内容，保留换行和缩进，转义HTML
function formatMessageContent(content) {
  if (!content) return ''
  // 转义 HTML 防止 XSS
  content = content
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
  // 将换行转换为 <br>
  content = content.replace(/\n/g, '<br>')
  return content
}

// Save Agent
const handleSave = async () => {
  if (!basicConfig.value.name.trim()) {
    showToast('请输入Agent名称', 'error')
    return
  }

  saving.value = true
  try {
    // 新数据结构：所有配置展开到顶层（适配后端 UpdateChatAgentSchema）
    const requestData = {
      app_id: isCreating ? null : pgId.value,
      uuid: appId, // appId 就是路由参数中的 uuid
      name: basicConfig.value.name,
      description: basicConfig.value.description,
      icon: basicConfig.value.icon,
      is_public: basicConfig.value.is_public,
      type: 'CHAT',
      // LLM 配置直接展开
      llmConfig: {
        model: llmConfig.value.model,
        systemPrompt: llmConfig.value.systemPrompt,
        temperature: llmConfig.value.temperature,
        maxTokens: llmConfig.value.maxTokens
      },
      // 对话式 Agent 特有配置
      enableKnowledgeBase: false,
      knowledgeBaseConfig: null,
      // 功能开关直接展开（转换 enabled/disabled -> boolean）
      enableFileUpload: fileUpload.value === 'enabled',
      enableTTS: ttsEnabled.value === 'enabled',
      enableASR: asrEnabled.value === 'enabled',
      guessedQuestions: suggestedQuestions.value === 'enabled',
      enableToolCall: toolCalling.value === 'enabled',
      openingMessage: openingMessage.value
    }

    let response
    if (isCreating) {
      // Create new
      response = await axios.post('/api/app/create', requestData)
    } else {
      // Update existing - unified update interface
      response = await axios.post('/api/app/update', requestData)
    }

    if (response.data.success) {
      showToast(isCreating ? '创建成功！' : '保存成功！', 'success')
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

// Send message
const handleSendMessage = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const userMessage = {
    role: 'user',
    content: inputMessage.value,
    time: new Date().toLocaleTimeString()
  }

  messages.value.push(userMessage)
  const userInput = inputMessage.value
  inputMessage.value = ''
  scrollToBottom()

  // Add placeholder for assistant
  const aiResponse = {
    role: 'assistant',
    content: '',
    time: new Date().toLocaleTimeString()
  }
  messages.value.push(aiResponse)
  const aiMessageIndex = messages.value.length - 1
  isLoading.value = true

  try {
    // Streaming request to backend - use app_uuid (not PG id)
    const chatAppId = currentAppUuid.value || appId
    const token = localStorage.getItem('access_token')
    const response = await fetch(`/api/app/chat/${chatAppId}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        message: userInput
      })
    })

    if (!response.ok) {
      throw new Error('API request failed')
    }

    // Process SSE streaming response
    const reader = response.body.getReader()
    const decoder = new TextDecoder()

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      const chunk = decoder.decode(value, { stream: true })
      // Parse SSE format: each line is "data: tokenText\n\n"
      const lines = chunk.split('\n')
      for (const line of lines) {
        if (line.startsWith('data: ')) {
          const token = line.slice(6)
          // Backend already outputs correct raw text, just append directly
          messages.value[aiMessageIndex].content += token
        }
      }
      scrollToBottom()
    }

  } catch (error) {
    console.error('Chat failed:', error)
    messages.value[aiMessageIndex].content = `抱歉，处理您的请求时出现了错误：${error.message}`
  } finally {
    isLoading.value = false
    scrollToBottom()
  }
}

// On mount
onMounted(() => {
  // Get user info
  const userInfo = localStorage.getItem('user_info')
  if (userInfo) {
    const user = JSON.parse(userInfo)
    username.value = user.name || user.username || '用户'
  }

  // Load app info from backend if we have an id
  if (appId) {
    loadAppInfo()
  }
})

// Axios interceptor for auth
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

.workflow-chat-container {
  display: flex;
  height: 100vh;
  background: var(--background-color);
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  width: 100vw;
}

/* 最左侧主导航 (和首页一致) */
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

/* 第二栏：配置面板 */
.config-panel {
  width: 420px;
  background: white;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow-y: auto;
}

/* Middle Config Panel */
.config-panel {
  width: 420px;
  background: white;
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  flex-shrink: 0;
  overflow-y: auto;
}

.config-panel-header {
  padding: 16px 20px;
  border-bottom: 1px solid var(--border-color);
  background: white;
}

.config-title {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.config-panel-content {
  flex: 1;
  padding: 20px;
}

.config-section {
  margin-bottom: 28px;
}

.section-title {
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0 0 16px 0;
  padding-bottom: 8px;
  border-bottom: 1px solid #f0f0f0;
}

.config-item {
  margin-bottom: 16px;
}

.config-label {
  display: block;
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.config-label .required {
  color: #ef4444;
}

.config-input,
.config-select {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
  box-sizing: border-box;
  background: white;
}

.config-input:focus,
.config-select:focus,
.config-textarea:focus {
  outline: none;
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.config-textarea {
  width: 100%;
  padding: 10px 14px;
  border: 1px solid #e2e8f0;
  border-radius: 8px;
  font-size: 14px;
  transition: all 0.2s;
  box-sizing: border-box;
  resize: vertical;
  font-family: inherit;
}

.config-toggle-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: 16px;
}

.config-toggle-label {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

.config-toggle-options {
  display: flex;
  gap: 4px;
  background: #f3f4f6;
  border-radius: 8px;
  padding: 2px;
}

.toggle-btn-option {
  padding: 6px 16px;
  font-size: 14px;
  border: none;
  background: transparent;
  color: #6b7280;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s;
}

.toggle-btn-option.active {
  background: white;
  color: var(--primary-color);
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  font-weight: 500;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 14px;
  color: var(--text-primary);
}

.checkbox-label input {
  width: auto;
  cursor: pointer;
}

.config-actions {
  display: flex;
  gap: 12px;
  justify-content: flex-end;
  padding-top: 12px;
  border-top: 1px solid #f0f0f0;
}

.btn-cancel,
.btn-save {
  padding: 10px 24px;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-cancel {
  background: white;
  border: 1px solid #e2e8f0;
  color: var(--text-secondary);
}

.btn-cancel:hover {
  background: #f9fafb;
}

.btn-save {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  color: white;
  border: none;
}

.btn-save:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(107, 78, 237, 0.35);
}

.btn-save:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.app-info {
  display: flex;
  align-items: center;
  gap: 12px;
  flex: 1;
}

.app-icon {
  width: 40px;
  height: 40px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
}

.app-details h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: var(--text-primary);
}

.toggle-btn {
  width: 36px;
  height: 36px;
  padding: 0;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.toggle-btn:hover {
  background: var(--hover-bg);
  color: var(--text-primary);
}

.toggle-icon {
  font-size: 14px;
}

.sidebar-content {
  flex: 1;
  padding: 16px;
}

.app-description {
  font-size: 14px;
  color: var(--text-secondary);
  line-height: 1.5;
  margin-bottom: 20px;
  padding: 12px;
  background: white;
  border-radius: 8px;
  border: 1px solid var(--border-color);
}

.new-chat-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  width: 100%;
  background: white;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  font-size: 14px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.new-chat-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  border-color: var(--primary-color);
}

.new-chat-icon {
  font-size: 16px;
  font-weight: 600;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid var(--border-color);
}

.back-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 14px;
  width: 100%;
  background: transparent;
  color: var(--text-secondary);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.back-btn:hover {
  background: var(--hover-bg);
  color: var(--text-primary);
}

/* Chat Area */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fafafa;
  min-width: 0;
  position: relative;
  transition: all 0.3s ease;
}

.chat-area-narrow {
  flex: 1;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid var(--border-color);
}

.chat-title {
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
  margin: 0;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: relative;
}

/* Empty state */
.empty-chat {
  position: absolute;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  text-align: center;
  color: var(--text-secondary);
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-title {
  font-size: 20px;
  font-weight: 600;
  color: var(--text-primary);
  margin-bottom: 8px;
}

.empty-subtitle {
  font-size: 14px;
  color: var(--text-secondary);
}

/* Messages */
.message {
  display: flex;
  gap: 12px;
  max-width: 80%;
}

.user-message {
  align-self: flex-end;
  flex-direction: row-reverse;
}

.assistant-message {
  align-self: flex-start;
}

.message-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-message .message-avatar {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  color: white;
}

.assistant-message .message-avatar {
  background: #f3f0ff;
  color: var(--primary-color);
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-text {
  padding: 12px 16px;
  border-radius: 12px;
  font-size: 14px;
  line-height: 1.5;
  color: var(--text-primary);
  white-space: pre-wrap;
}

.user-message .message-text {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  color: white;
}

.assistant-message .message-text {
  background: white;
  border: 1px solid var(--border-color);
  color: var(--text-primary);
}

.message-time {
  font-size: 11px;
  color: var(--text-secondary);
  padding: 0 4px;
}

/* Typing indicator */
.typing {
  display: flex;
  gap: 4px;
  padding: 8px 12px;
}

.typing span {
  width: 8px;
  height: 8px;
  background: rgba(255, 255, 255, 0.7);
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing span:nth-child(2) {
  animation-delay: -0.16s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* Input area */
.chat-input-area {
  padding: 20px 24px;
  background: white;
  border-top: 1px solid var(--border-color);
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  background: var(--hover-bg);
  border: 1px solid var(--primary-color);
  border-radius: 12px;
  padding: 12px;
  transition: all 0.2s ease;
  box-shadow: 0 0 0 3px rgba(107, 78, 237, 0.1);
}

.input-container:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(107, 78, 237, 0.2);
}

.chat-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: var(--text-primary);
  resize: none;
  min-height: 24px;
  max-height: 120px;
  font-family: inherit;
  outline: none;
}

.chat-input::placeholder {
  color: var(--text-secondary);
}

.input-actions {
  display: flex;
  gap: 8px;
  align-items: center;
}

.send-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(107, 78, 237, 0.3);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-icon {
  font-size: 16px;
}

.input-hint {
  font-size: 11px;
  color: var(--text-secondary);
  text-align: center;
  margin-top: 8px;
}

/* Scrollbar */
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

/* Responsive */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    left: 0;
    top: 0;
    height: 100vh;
    z-index: 1000;
    box-shadow: 2px 0 10px rgba(0, 0, 0, 0.1);
  }

  .sidebar.collapsed {
    left: -60px;
  }

  .chat-header {
    padding: 12px 16px;
  }

  .chat-messages {
    padding: 16px;
  }

  .chat-input-area {
    padding: 16px;
  }

  .message {
    max-width: 90%;
  }
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
  z-index: 2000;
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
