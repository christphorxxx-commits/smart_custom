<template>
  <div class="workflow-chat-container">
    <!-- 侧边栏 (可折叠) -->
    <div class="sidebar" :class="{ collapsed: isSidebarCollapsed }">
      <div class="sidebar-header">
        <div class="app-info" v-if="!isSidebarCollapsed">
          <div class="app-icon" :style="{ background: getDefaultColor(appInfo.type) }" v-if="appInfo">
            {{ appInfo.icon || '🤖' }}
          </div>
          <div class="app-details">
            <h3 class="app-name">{{ appInfo?.name || '工作流对话' }}</h3>
          </div>
        </div>
        <button class="toggle-btn" @click="toggleSidebar" title="展开/收起侧边栏">
          <span class="toggle-icon">{{ isSidebarCollapsed ? '▶' : '◀' }}</span>
        </button>
      </div>

      <div class="sidebar-content" v-if="!isSidebarCollapsed">
        <div class="app-description" v-if="appInfo?.description">
          {{ appInfo.description }}
        </div>

        <button class="new-chat-btn" @click="handleNewChat">
          <span class="new-chat-icon">+</span>
          <span>新对话</span>
        </button>
      </div>

      <div class="sidebar-footer">
        <button class="back-btn" @click="goBack">
          <span class="back-icon">←</span>
          <span v-if="!isSidebarCollapsed">返回主页</span>
        </button>
      </div>
    </div>

    <!-- 主对话区域 -->
    <div class="chat-area">
      <!-- 对话头部 -->
      <div class="chat-header">
        <h2 class="chat-title">{{ appInfo?.name || '工作流对话' }}</h2>
      </div>

      <!-- 对话消息区域 -->
      <div class="chat-messages" ref="chatMessagesRef">
        <!-- 空状态 -->
        <div class="empty-chat" v-if="messages.length === 0">
          <div class="empty-icon">💬</div>
          <h3 class="empty-title">开始新对话</h3>
          <p class="empty-subtitle">发送消息给 {{ appInfo?.name || '工作流' }}</p>
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
            <div class="message-text">{{ msg.content }}</div>
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
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const chatMessagesRef = ref(null)
const appId = route.params.id

// State
const isSidebarCollapsed = ref(false)
const inputMessage = ref('')
const messages = ref([])
const isLoading = ref(false)
const appInfo = ref(null)

// User info
const username = ref('用户')
const userInitial = computed(() => {
  return username.value.charAt(0).toUpperCase()
})

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
          id: parseInt(appId),
          name: data.data.name,
          icon: data.data.icon,
          type: data.data.type,
          description: data.data.description,
          app_id: data.data.app_id
        }
        // 保存app_id用于发送消息
        currentAppUuid.value = data.data.app_id
      }
    }
  } catch (error) {
    console.error('加载应用信息失败:', error)
    // 如果加载失败，使用占位信息
    appInfo.value = {
      id: parseInt(appId),
      name: `工作流 ${appId}`,
      icon: '🤖',
      type: 'workflow',
      description: '自定义工作流对话'
    }
  }
}

// 当前应用的 UUID（用于 chat API）
const currentAppUuid = ref('')

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
  window.location.href = '/'
}

function getDefaultColor(type) {
  const colors = {
    ai: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)',
    workflow: 'linear-gradient(135deg, #6B4EED 0%, #8b5cf6 100%)',
    chat: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)'
  }
  return colors[type] || 'linear-gradient(135deg, #6B4EED 0%, #8b5cf6 100%)'
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

  // Load app info from backend
  loadAppInfo()
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

/* Sidebar */
.sidebar {
  display: flex;
  flex-direction: column;
  width: 260px;
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border-color);
  flex-shrink: 0;
  transition: all 0.3s ease;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
}

.sidebar.collapsed {
  width: 60px;
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
</style>
