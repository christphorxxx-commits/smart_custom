<template>
  <div class="workflow-chat-container">
    <!-- 侧边栏 (可折叠) -->
    <div class="sidebar" :class="{ collapsed: isSidebarCollapsed }">
      <div class="sidebar-header">
        <div class="app-info" v-if="!isSidebarCollapsed">
          <div class="app-icon" :style="{ background: appInfo.color }" v-if="appInfo">
            {{ appInfo.icon }}
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

// Quick apps list to find current app info
const quickApps = ref([
  { id: 1, name: '智能问答', icon: '💬', color: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)', description: '基于大语言模型的智能问答助手' },
  { id: 2, name: '语音合成', icon: '🔊', color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)', description: '将文本转换为自然语音' },
  { id: 3, name: '文字转语音', icon: '📝', color: 'linear-gradient(135deg, #4ade80 0%, #22c55e 100%)', description: '专业文字转语音服务' },
  { id: 4, name: 'AI绘画', icon: '🎨', color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)', description: 'AI图像生成' },
  { id: 5, name: '代码助手', icon: '💻', color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)', description: '代码编写与调试助手' },
  { id: 6, name: '翻译助手', icon: '🌐', color: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)', description: '多语言翻译服务' }
])

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
    // Streaming request to backend
    const token = localStorage.getItem('access_token')
    const response = await fetch(`/api/workflow/chat/${appId}`, {
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
            messages.value[aiMessageIndex].content += match[2]
          } else if (dataLine.trim()) {
            // 如果没有匹配到，直接追加整行（兼容纯文本）
            messages.value[aiMessageIndex].content += dataLine.trim()
          }
          scrollToBottom()
        }
      }
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

  // Find current app info
  const parsedId = parseInt(appId)
  const found = quickApps.value.find(a => a.id === parsedId)
  if (found) {
    appInfo.value = found
  } else {
    appInfo.value = {
      id: parsedId,
      name: `工作流 ${parsedId}`,
      icon: '🤖',
      color: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
      description: '自定义工作流对话'
    }
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
  --primary-color: #6366f1;
  --primary-hover: #4f46e5;
  --background-color: #ffffff;
  --sidebar-bg: #f7f8fa;
  --text-primary: #1d2129;
  --text-secondary: #86909c;
  --border-color: #e5e7eb;
  --hover-bg: #f2f3f5;
  --user-message-bg: #e6f4ff;
  --user-message-text: #1d2129;
  --assistant-message-bg: #f7f8fa;
  --assistant-message-text: #1d2129;
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
}

.sidebar.collapsed {
  width: 56px;
}

.sidebar-header {
  padding: 16px 12px;
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
  width: 32px;
  height: 32px;
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
  padding: 16px 12px;
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
  padding: 10px 16px;
  width: 100%;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.new-chat-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  background: var(--primary-hover);
}

.new-chat-icon {
  font-size: 16px;
  font-weight: 600;
}

.sidebar-footer {
  padding: 12px;
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
  background: var(--background-color);
  min-width: 0;
  position: relative;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: var(--background-color);
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
  background: linear-gradient(135deg, var(--primary-color) 0%, #8b5cf6 100%);
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
  border-radius: 16px;
  font-size: 15px;
  line-height: 1.6;
  word-wrap: break-word;
  white-space: pre-wrap;
}

.user-message .message-text {
  background: #e6f4ff; /* 淡蓝色 - 用户消息 */
  color: #1d2129;
}

.assistant-message .message-text {
  background: #f5f5f5; /* 淡灰色 - AI回复 */
  color: #1d2129;
}

.message-time {
  font-size: 12px;
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
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}

/* Input area */
.chat-input-area {
  padding: 16px 24px 24px;
  background: var(--background-color);
  border-top: 1px solid var(--border-color);
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  background: var(--hover-bg);
  border: 1px solid var(--border-color);
  border-radius: 12px;
  padding: 12px 16px;
  transition: all 0.2s ease;
}

.input-container:focus-within {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.chat-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 15px;
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
  width: 40px;
  height: 40px;
  padding: 8px 16px;
  background: linear-gradient(135deg, var(--primary-color) 0%, #8b5cf6 100%);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
}

.send-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
  background: var(--primary-hover);
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-icon {
  font-size: 16px;
}

.input-hint {
  font-size: 12px;
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
  background: var(--border-color);
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
    transform: translateX(-100%);
  }

  .chat-header {
    padding: 12px 16px;
  }

  .chat-messages {
    padding: 16px;
  }

  .chat-input-area {
    padding: 12px 16px 16px;
  }

  .message {
    max-width: 90%;
  }
}
</style>
