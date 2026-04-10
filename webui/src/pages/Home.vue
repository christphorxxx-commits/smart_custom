<template>
  <div class="home-container">
    <!-- 左侧边栏 -->
    <div class="sidebar" :class="{ collapsed: isSidebarCollapsed }">
      <!-- Logo & New Chat -->
      <div class="sidebar-top">
        <div class="logo-section" v-if="!isSidebarCollapsed">
          <div class="logo">
            <div class="logo-icon">🤖</div>
            <span class="logo-text">FastGPT</span>
          </div>
        </div>
        <button class="new-chat-btn" @click="handleNewChat">
          <span class="icon">+</span>
          <span v-if="!isSidebarCollapsed">新对话</span>
        </button>
      </div>

      <!-- 对话列表 -->
      <div class="chat-list-container" v-if="!isSidebarCollapsed">
        <div class="chat-list-header">
          <span class="title">最近对话</span>
        </div>
        <div class="chat-list">
          <div
            class="chat-item"
            :class="{ active: selectedChatId === item.id }"
            v-for="item in recentChats"
            :key="item.id"
            @click="selectChat(item)"
          >
            <span class="chat-icon">💬</span>
            <span class="chat-title">{{ item.title }}</span>
            <span class="chat-time">{{ item.time }}</span>
          </div>
        </div>
      </div>

      <!-- 快捷应用 -->
      <div class="quick-apps" v-if="!isSidebarCollapsed">
        <div class="section-title">快捷应用</div>
        <div class="app-grid">
          <div
            class="app-item"
            v-for="app in quickApps"
            :key="app.id"
            @click="openAppChat(app)"
          >
            <div class="app-icon" :style="{ background: app.color }">
              {{ app.icon }}
            </div>
            <span class="app-name">{{ app.name }}</span>
          </div>
        </div>
      </div>

      <!-- 底部用户信息 -->
      <div class="sidebar-bottom">
        <div class="user-info" @click="toggleUserMenu">
          <div class="user-avatar">
            {{ userInitial }}
          </div>
          <div class="user-details" v-if="!isSidebarCollapsed">
            <div class="user-name">{{ username }}</div>
          </div>
        </div>
        <button class="toggle-sidebar-btn" @click="toggleSidebar">
          <span>{{ isSidebarCollapsed ? '▶' : '◀' }}</span>
        </button>
        <div class="user-menu" v-if="isUserMenuOpen && !isSidebarCollapsed">
          <div class="menu-item" @click="handleLogout">
            <span class="icon">🚪</span>
            <span>退出登录</span>
          </div>
        </div>
      </div>
    </div>

    <!-- 右侧聊天区域 -->
    <div class="main-content">
      <!-- 聊天头部 -->
      <div class="chat-header" v-if="currentChat">
        <h2>{{ currentChat.title }}</h2>
      </div>

      <!-- 消息区域 -->
      <div class="chat-messages" ref="chatMessagesRef">
        <!-- 空状态 -->
        <div class="empty-state" v-if="messages.length === 0">
          <div class="empty-logo">
            <div class="empty-logo-icon">🤖</div>
            <h1>FastGPT</h1>
            <p>知识问答，一键生成，快速开始</p>
          </div>
          <div class="suggestions">
            <div class="suggestion-card" v-for="suggestion in suggestions" @click="sendSuggestion(suggestion)">
              {{ suggestion }}
            </div>
          </div>
        </div>

        <!-- 消息列表 -->
        <div
          class="message"
          :class="{ user: message.role === 'user' }"
          v-for="(message, index) in messages"
          :key="index"
        >
          <div class="message-avatar">
            {{ message.role === 'user' ? userInitial : '🤖' }}
          </div>
          <div class="message-content">
            <div class="message-text">{{ message.content }}</div>
          </div>
        </div>

        <!-- 加载中 -->
        <div class="message assistant" v-if="isLoading">
          <div class="message-avatar">🤖</div>
          <div class="message-content">
            <div class="typing">
              <span></span><span></span><span></span>
            </div>
          </div>
        </div>
      </div>

      <!-- 输入框区域 -->
      <div class="input-container-wrapper">
        <div class="input-container">
          <textarea
            v-model="inputMessage"
            placeholder="输入消息，按Enter发送，Shift+Enter换行"
            @keydown.enter.exact="handleSend"
            @keydown.enter.shift.prevent="inputMessage += '\n'"
            :disabled="isLoading"
          ></textarea>
          <button
            class="send-btn"
            @click="handleSend"
            :disabled="!inputMessage.trim() || isLoading"
          >
            <span>➤</span>
          </button>
        </div>
        <div class="footer-hint">
          FastGPT can make mistakes. Consider checking important information.
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import axios from 'axios'

const router = useRouter()
const chatMessagesRef = ref(null)

// State
const isSidebarCollapsed = ref(false)
const isUserMenuOpen = ref(false)
const inputMessage = ref('')
const messages = ref([])
const isLoading = ref(false)
const selectedChatId = ref(null)
const currentChat = ref(null)

// User info
const username = ref('用户')
const userInitial = computed(() => {
  return username.value.charAt(0).toUpperCase()
})

// Recent chats
const recentChats = ref([])

// 加载用户聊天列表
const loadRecentChats = async () => {
  try {
    const token = localStorage.getItem('access_token')
    const response = await fetch('/api/ai/list?skip=0&limit=20', {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      if (data.success && Array.isArray(data.data)) {
        recentChats.value = data.data.map(item => ({
          id: item.id,
          title: item.title,
          time: formatTime(item.updated_at),
          messages: []
        }))
      }
    }
  } catch (error) {
    console.error('加载聊天列表失败:', error)
  }
}

// 格式化时间
const formatTime = (dateStr) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diff = now - date
  const minutes = Math.floor(diff / (1000 * 60))
  const hours = Math.floor(diff / (1000 * 60 * 60))
  const days = Math.floor(diff / (1000 * 60 * 60 * 24))

  if (minutes < 60) return '刚刚'
  if (hours < 24) return `${hours}小时前`
  if (days < 7) return `${days}天前`
  return date.toLocaleDateString()
}

// Quick apps
const quickApps = ref([
  { id: 1, name: '智能问答', icon: '💬', color: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)' },
  { id: 2, name: '语音合成', icon: '🔊', color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
  { id: 3, name: '代码助手', icon: '💻', color: 'linear-gradient(135deg, #4ade80 0%, #22c55e 100%)' },
  { id: 4, name: '翻译助手', icon: '🌐', color: 'linear-gradient(135deg, #3b82f6 0%, #06b6d4 100%)' }
])

// Welcome suggestions
const suggestions = ref([
  '帮我写一篇技术博客',
  '解释一下量子计算',
  '写一个Python快速排序',
  '推荐几本好书'
])

// Scroll to bottom
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

// Toggle user menu
const toggleUserMenu = () => {
  isUserMenuOpen.value = !isUserMenuOpen.value
}

// New chat
const handleNewChat = () => {
  messages.value = []
  currentChat.value = null
  selectedChatId.value = null
}

// Select chat
const selectChat = async (chat) => {
  selectedChatId.value = chat.id
  currentChat.value = chat

  // 从后端加载消息历史
  try {
    const token = localStorage.getItem('access_token')
    const response = await fetch(`/api/ai/${chat.id}/messages`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    })
    if (response.ok) {
      const data = await response.json()
      if (data.success && Array.isArray(data.data)) {
        messages.value = data.data.map(item => ({
          role: item.role,
          content: item.content
        }))
      } else {
        messages.value = []
      }
    }
  } catch (error) {
    console.error('加载消息历史失败:', error)
    messages.value = []
  }

  scrollToBottom()
}

// Open workflow chat
const openAppChat = (app) => {
  window.location.href = `/workflow/chat/${app.id}`
}

// Send suggestion
const sendSuggestion = (text) => {
  inputMessage.value = text
  handleSend()
}

// Handle send
const handleSend = async () => {
  if (!inputMessage.value.trim() || isLoading.value) return

  const userMessage = {
    role: 'user',
    content: inputMessage.value
  }

  if (!currentChat.value) {
    // Create new chat
    const newId = Date.now()
    currentChat.value = {
      id: newId,
      title: inputMessage.value.slice(0, 20),
      time: '刚刚',
      messages: []
    }
    selectedChatId.value = newId
    recentChats.value.unshift(currentChat.value)
  }

  messages.value.push(userMessage)
  const userInput = inputMessage.value
  inputMessage.value = ''
  scrollToBottom()
  isLoading.value = true

  // Add assistant placeholder
  const assistantIndex = messages.value.length
  messages.value.push({
    role: 'assistant',
    content: ''
  })

  try {
    const token = localStorage.getItem('access_token')
    // 新建对话传null，让后端自动创建
    const chatId = currentChat.value?.id != null ? String(currentChat.value.id) : null
    const response = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      },
      body: JSON.stringify({
        message: userInput,
        chat_id: chatId
      })
    })

    if (!response.ok) {
      throw new Error('API request failed')
    }

    // 处理SSE流式响应
    const reader = response.body.getReader()
    const decoder = new TextDecoder()
    let buffer = ''
    // 正则匹配 data='内容' 或 data="内容"
    const dataRegex = /data\s*=\s*(['"])(.*?)\1/

    while (true) {
      const { done, value } = await reader.read()
      if (done) break

      buffer += decoder.decode(value, { stream: true })

      // 按行分割处理SSE
      const lines = buffer.split('\n')
      // 保留最后不完整的一行到下次处理
      buffer = lines.pop() || ''

      for (const line of lines) {
        // 跳过空行
        if (!line.trim()) continue

        // 提取data字段
        if (line.startsWith('data: ')) {
          const dataLine = line.slice(6)
          // 检查是否是结束标记
          if (dataLine.trim() === '[DONE]') {
            continue
          }
          // 匹配data='实际内容' 提取真实内容
          const match = dataLine.match(dataRegex)
          if (match) {
            // 提取引号中的内容
            messages.value[assistantIndex].content += match[2]
          } else if (dataLine.trim()) {
            // 如果没有匹配到，直接追加整行（兼容纯文本）
            messages.value[assistantIndex].content += dataLine.trim()
          }
          scrollToBottom()
        }
      }
    }

    // Save to current chat
    if (currentChat.value) {
      currentChat.value.messages = messages.value
    }

  } catch (error) {
    console.error('Chat error:', error)
    messages.value[assistantIndex].content = `抱歉，出错了：${error.message}`
  } finally {
    isLoading.value = false
    scrollToBottom()
    // 重新加载聊天列表，更新最新对话排序
    loadRecentChats()
  }
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
    console.error('Logout error:', error)
  } finally {
    localStorage.removeItem('access_token')
    localStorage.removeItem('refresh_token')
    localStorage.removeItem('token_type')
    localStorage.removeItem('user_info')
    window.location.href = '/login'
  }
}

// On mount
onMounted(() => {
  const userInfo = localStorage.getItem('user_info')
  if (userInfo) {
    const user = JSON.parse(userInfo)
    username.value = user.name || user.username || '用户'
  }
  // 加载最近对话列表
  loadRecentChats()
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
  --sidebar-width: 260px;
  --sidebar-collapsed-width: 56px;
  --sidebar-bg: #f7f8fa;
  --border-color: #e5e7eb;
  --text-primary: #1d2129;
  --text-secondary: #86909c;
  --text-disabled: #c9cdd4;
  --bg-primary: #ffffff;
  --bg-secondary: #f7f8fa;
  --primary-color: #6366f1;
  --primary-hover: #4f46e5;
  --hover-bg: #f2f3f5;
  --radius: 8px;
  --radius-lg: 12px;
  --shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
  --user-message-bg: #e6f4ff;
  --user-message-text: #1d2129;
  --assistant-message-bg: #f7f8fa;
  --assistant-message-text: #1d2129;
}

.home-container {
  display: flex;
  height: 100vh;
  background: var(--bg-primary);
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  overflow: hidden;
}

/* Sidebar */
.sidebar {
  width: var(--sidebar-width);
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  flex-shrink: 0;
}

.sidebar.collapsed {
  width: var(--sidebar-collapsed-width);
}

.sidebar-top {
  padding: 16px 12px;
  border-bottom: 1px solid var(--border-color);
}

.logo-section {
  margin-bottom: 12px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
}

.logo-icon {
  width: 32px;
  height: 32px;
  background: linear-gradient(135deg, var(--primary-color) 0%, #8b5cf6 100%);
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.logo-text {
  font-size: 20px;
  font-weight: 700;
  color: var(--text-primary);
  background: linear-gradient(135deg, var(--primary-color) 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.new-chat-btn {
  width: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  padding: 10px 16px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius);
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s;
}

.new-chat-btn:hover {
  background: var(--primary-hover);
}

.new-chat-btn .icon {
  font-size: 16px;
  line-height: 1;
}

/* Chat list */
.chat-list-container {
  flex: 1;
  overflow-y: auto;
  padding: 12px;
}

.chat-list-header {
  margin-bottom: 8px;
}

.chat-list-header .title {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.chat-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chat-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 10px 8px;
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.2s;
}

.chat-item:hover {
  background: var(--hover-bg);
}

.chat-item.active {
  background: var(--hover-bg);
}

.chat-item .chat-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.chat-item .chat-title {
  flex: 1;
  font-size: 13px;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.chat-item .chat-time {
  font-size: 12px;
  color: var(--text-secondary);
  flex-shrink: 0;
}

/* Quick apps */
.quick-apps {
  padding: 12px;
  border-top: 1px solid var(--border-color);
}

.section-title {
  font-size: 12px;
  font-weight: 500;
  color: var(--text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: 10px;
}

.app-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 8px;
}

.app-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 10px 8px;
  background: var(--bg-primary);
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.2s;
  border: 1px solid transparent;
}

.app-item:hover {
  background: var(--hover-bg);
  border-color: var(--primary-color);
}

.app-item .app-icon {
  width: 28px;
  height: 28px;
  border-radius: 6px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  color: white;
}

.app-item .app-name {
  font-size: 11px;
  color: var(--text-primary);
  text-align: center;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  width: 100%;
}

/* Sidebar bottom */
.sidebar-bottom {
  padding: 12px;
  border-top: 1px solid var(--border-color);
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 8px;
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.2s;
}

.user-info:hover {
  background: var(--hover-bg);
}

.user-avatar {
  width: 32px;
  height: 32px;
  border-radius: 50%;
  background: linear-gradient(135deg, var(--primary-color) 0%, #8b5cf6 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
  flex-shrink: 0;
}

.user-details .user-name {
  font-size: 13px;
  font-weight: 500;
  color: var(--text-primary);
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.toggle-sidebar-btn {
  position: absolute;
  right: 12px;
  top: 50%;
  transform: translateY(-50%);
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
}

.toggle-sidebar-btn:hover {
  background: var(--hover-bg);
}

.user-menu {
  position: absolute;
  bottom: 100%;
  left: 12px;
  right: 12px;
  background: var(--bg-primary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius);
  box-shadow: var(--shadow);
  margin-bottom: 8px;
  overflow: hidden;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 10px 12px;
  cursor: pointer;
  transition: all 0.2s;
  color: var(--text-primary);
}

.menu-item:hover {
  background: var(--hover-bg);
}

.menu-item .icon {
  font-size: 14px;
}

.menu-item span {
  font-size: 13px;
}

/* Main content */
.main-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
  background: var(--bg-primary);
}

.chat-header {
  padding: 16px 24px;
  border-bottom: 1px solid var(--border-color);
}

.chat-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: var(--text-primary);
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
}

/* Empty state */
.empty-state {
  height: 100%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  color: var(--text-secondary);
}

.empty-logo {
  text-align: center;
  margin-bottom: 40px;
}

.empty-logo-icon {
  width: 80px;
  height: 80px;
  background: linear-gradient(135deg, var(--primary-color) 0%, #8b5cf6 100%);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  margin: 0 auto 16px;
}

.empty-logo h1 {
  margin: 0 0 8px;
  font-size: 32px;
  font-weight: 700;
  color: var(--text-primary);
}

.empty-logo p {
  margin: 0;
  font-size: 16px;
  color: var(--text-secondary);
}

.suggestions {
  display: grid;
  grid-template-columns: repeat(2, 240px);
  gap: 16px;
}

.suggestion-card {
  padding: 16px 20px;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  cursor: pointer;
  transition: all 0.2s;
  font-size: 14px;
  color: var(--text-primary);
}

.suggestion-card:hover {
  border-color: var(--primary-color);
  background: white;
  box-shadow: var(--shadow);
}

/* Messages */
.message {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  max-width: 80%;
}

.message.user {
  align-self: flex-end;
  flex-direction: row-reverse;
  margin-left: auto;
}

.message:not(.user) {
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

.message:not(.user) .message-avatar {
  background: linear-gradient(135deg, var(--primary-color) 0%, #8b5cf6 100%);
  color: white;
}

.message.user .message-avatar {
  background: var(--primary-color);
  color: white;
}

.message-content {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.message-text {
  padding: 12px 16px;
  border-radius: 16px;
  font-size: 15px;
  line-height: 1.6;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.message.user .message-text {
  background: #e6f4ff; /* 淡蓝色 - 用户消息 */
  color: #1d2129;
}

.message:not(.user) .message-text {
  background: #f5f5f5; /* 淡灰色 - AI回复 */
  color: #1d2129;
}

/* Typing indicator */
.typing {
  display: flex;
  gap: 4px;
  padding: 12px 16px;
}

.typing span {
  width: 8px;
  height: 8px;
  background: var(--text-secondary);
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
  0%, 80%, 100% { transform: scale(0); }
  40% { transform: scale(1); }
}

/* Input area */
.input-container-wrapper {
  padding: 16px 24px 24px;
  border-top: 1px solid var(--border-color);
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  background: var(--bg-secondary);
  border: 1px solid var(--border-color);
  border-radius: var(--radius-lg);
  padding: 12px 16px;
  transition: all 0.2s;
}

.input-container:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.input-container textarea {
  flex: 1;
  border: none;
  outline: none;
  background: transparent;
  font-size: 15px;
  color: var(--text-primary);
  font-family: inherit;
  resize: none;
  min-height: 24px;
  max-height: 200px;
  line-height: 1.5;
}

.input-container textarea::placeholder {
  color: var(--text-secondary);
}

.send-btn {
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: var(--radius);
  cursor: pointer;
  transition: all 0.2s;
  flex-shrink: 0;
}

.send-btn:hover:not(:disabled) {
  background: var(--primary-hover);
}

.send-btn:disabled {
  background: var(--text-disabled);
  cursor: not-allowed;
}

.send-btn span {
  font-size: 18px;
  line-height: 1;
}

.footer-hint {
  text-align: center;
  font-size: 12px;
  color: var(--text-secondary);
  margin-top: 8px;
}

/* Scrollbar */
.chat-list-container::-webkit-scrollbar,
.chat-messages::-webkit-scrollbar {
  width: 6px;
}

.chat-list-container::-webkit-scrollbar-track,
.chat-messages::-webkit-scrollbar-track {
  background: transparent;
}

.chat-list-container::-webkit-scrollbar-thumb,
.chat-messages::-webkit-scrollbar-thumb {
  background: var(--border-color);
  border-radius: 3px;
}

.chat-list-container::-webkit-scrollbar-thumb:hover,
.chat-messages::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

/* Responsive */
@media (max-width: 768px) {
  .sidebar {
    position: fixed;
    top: 0;
    left: 0;
    height: 100vh;
    z-index: 100;
  }

  .sidebar.collapsed {
    transform: translateX(-100%);
  }

  .suggestions {
    grid-template-columns: 1fr;
    gap: 12px;
  }

  .message {
    max-width: 90%;
  }

  .chat-messages {
    padding: 16px;
  }

  .input-container-wrapper {
    padding: 12px 16px 16px;
  }
}
</style>
