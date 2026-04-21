<template>
  <div class="workflow-chat-container">
    <!-- 侧边栏 (可折叠) -->
    <div class="sidebar" :class="{ collapsed: isSidebarCollapsed }">
      <div class="sidebar-header">
        <div class="app-info" v-if="!isSidebarCollapsed">
          <div class="app-icon" :style="{ background: appInfo?.color }" v-if="appInfo">
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
</template>

<script setup>
import { ref, computed, onMounted, nextTick } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import axios from 'axios'

const route = useRoute()
const router = useRouter()
const chatMessagesRef = ref(null)
const pgAppId = route.params.id  // PG app table primary key
const mongoAppId = ref(null)  // MongoDB app uuid for chat

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

// 格式化消息内容，保留换行和缩进，转换markdown代码块
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
    const response = await fetch(`/api/app/chat/${mongoAppId.value}`, {
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
          try {
            // 直接JSON解析
            const token = JSON.parse(dataLine)
            messages.value[aiMessageIndex].content += token
          } catch (e) {
            // JSON解析失败，尝试提取 data='content' 格式 (ServerSentEvent输出)
            const dataRegex = /data\s*=\s*(['"])(.*?)\1/
            const match = dataLine.match(dataRegex)
            if (match) {
              messages.value[aiMessageIndex].content += match[2]
            } else if (dataLine.trim()) {
              messages.value[aiMessageIndex].content += dataLine.trim()
            }
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
onMounted(async () => {
  // Get user info
  const userInfo = localStorage.getItem('user_info')
  if (userInfo) {
    const user = JSON.parse(userInfo)
    username.value = user.name || user.username || '用户'
  }

  // Load app list and find current app info
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
        // Find current app in list by PG id
        const currentPgId = parseInt(pgAppId)
        const found = data.data.find(a => a.id === currentPgId)
        if (found) {
          appInfo.value = {
            id: found.id,
            name: found.name,
            icon: found.icon || '🤖',
            color: found.type === 'workflow'
              ? 'linear-gradient(135deg, #6B4EED 0%, #8b5cf6 100%)'
              : getDefaultColor(found.type),
            description: found.description
          }
          mongoAppId.value = found.app_id
        }
      }
    }
  } catch (error) {
    console.error('加载应用信息失败:', error)
    appInfo.value = {
      id: parseInt(pgAppId),
      name: `工作流 ${pgAppId}`,
      icon: '🤖',
      color: 'linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%)',
      description: '自定义工作流对话'
    }
  }
})
</script>

<style scoped>
.workflow-chat-container {
  display: flex;
  height: 100vh;
  background: #f8f9fa;
}

.sidebar {
  width: 280px;
  background: white;
  border-right: 1px solid #e5e7eb;
  transition: width 0.3s ease;
  display: flex;
  flex-direction: column;
}

.sidebar.collapsed {
  width: 50px;
}

.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.app-info {
  display: flex;
  align-items: center;
  gap: 12px;
}

.app-icon {
  width: 40px;
  height: 40px;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
  font-size: 20px;
}

.app-details h3 {
  margin: 0;
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
}

.toggle-btn {
  width: 32px;
  height: 32px;
  border: none;
  background: #f3f4f6;
  border-radius: 6px;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
}

.toggle-btn:hover {
  background: #e5e7eb;
}

.sidebar-content {
  flex: 1;
  padding: 16px;
  overflow-y: auto;
}

.app-description {
  font-size: 14px;
  color: #6b7280;
  line-height: 1.5;
  margin-bottom: 16px;
}

.new-chat-btn {
  width: 100%;
  padding: 10px;
  background: var(--primary-color);
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 14px;
  font-weight: 500;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 6px;
}

.new-chat-btn:hover {
  opacity: 0.9;
}

.new-chat-icon {
  font-size: 16px;
  line-height: 1;
}

.sidebar-footer {
  padding: 16px;
  border-top: 1px solid #e5e7eb;
}

.back-btn {
  width: 100%;
  padding: 10px;
  background: #f3f4f6;
  border: 1px solid #d1d5db;
  border-radius: 8px;
  cursor: pointer;
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
}

.back-btn:hover {
  background: #e5e7eb;
}

.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #f9fafb;
}

.chat-header {
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

.chat-header h2 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #1f2937;
}

.chat-messages {
  flex: 1;
  padding: 24px;
  overflow-y: auto;
}

.empty-chat {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  color: #6b7280;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.empty-title {
  margin: 0 0 8px 0;
  font-size: 24px;
  color: #374151;
}

.empty-subtitle {
  margin: 0;
  font-size: 14px;
}

.message {
  display: flex;
  gap: 12px;
  margin-bottom: 24px;
  max-width: 80%;
}

.message.user-message {
  margin-left: auto;
  flex-direction: row-reverse;
}

.message-avatar {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  background: var(--primary-color);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
  font-size: 16px;
}

.message-content {
  flex: 1;
}

.message-text {
  padding: 12px 16px;
  background: white;
  border-radius: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.1);
  line-height: 1.6;
  color: #374151;
  white-space: pre-wrap;
}

.message.user-message .message-text {
  background: var(--primary-color);
  color: white;
}

.message-time {
  font-size: 12px;
  color: #9ca3af;
  margin-top: 4px;
}

.message.user-message .message-time {
  text-align: right;
  color: #d1d5db;
}

.chat-input-area {
  padding: 16px 24px;
  background: white;
  border-top: 1px solid #e5e7eb;
}

.input-container {
  position: relative;
  display: flex;
  gap: 12px;
  align-items: flex-end;
}

.chat-input {
  flex: 1;
  min-height: 40px;
  max-height: 200px;
  padding: 10px 14px;
  border: 1px solid #d1d5db;
  border-radius: 20px;
  font-size: 14px;
  line-height: 1.5;
  resize: vertical;
  outline: none;
  transition: border-color 0.2s;
}

.chat-input:focus {
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(107, 78, 237, 0.1);
}

.input-actions {
  flex-shrink: 0;
}

.send-btn {
  width: 40px;
  height: 40px;
  border-radius: 50%;
  border: none;
  background: var(--pride);
  background: var(--primary-color);
  color: white;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: opacity 0.2s;
}

.send-btn:hover:not(:disabled) {
  opacity: 0.9;
}

.send-btn:disabled {
  opacity: 0.5;
  cursor: not-allowed;
}

.send-icon {
  font-size: 18px;
  line-height: 1;
}

.input-hint {
  margin-top: 8px;
  font-size: 12px;
  color: #9ca3af;
  text-align: center;
}

.typing span {
  display: inline-block;
  width: 8px;
  height: 8px;
  margin: 0 2px;
  background: #9ca3af;
  border-radius: 50%;
  animation: typing 1.4s infinite ease-in-out both;
}

.typing span:nth-child(1) {
  animation-delay: -0.32s;
}

.typing span:nth-child(2) {
  animation-delay: -0.16s;
}

.typing span:nth-child(3) {
  animation-delay: 0s;
}

@keyframes typing {
  0%, 80%, 100% {
    transform: scale(0);
  }
  40% {
    transform: scale(1);
  }
}
</style>
