<template>
  <div class="home-container">
    <!-- 左侧边栏 -->
    <div class="sidebar" :class="{ collapsed: isSidebarCollapsed }">
      <!-- 顶部标题和控制区域 -->
      <div class="sidebar-header">
        <div class="header-content">
          <div class="logo" v-if="!isSidebarCollapsed">
            <img src="../assets/bwen.jpg" alt="白问" class="logo-image" />
            <span class="logo-text">白问</span>
          </div>
          <div class="header-actions">
            <button class="action-btn search-btn" @click="toggleSearch" title="搜索">
              <span class="action-icon">🔍</span>
            </button>
            <button class="action-btn toggle-btn" @click="toggleSidebar" title="展开/收起">
              <span class="action-icon">{{ isSidebarCollapsed ? '▶' : '◀' }}</span>
            </button>
          </div>
        </div>
        <!-- 搜索框 -->
        <div class="search-container" v-if="isSearchActive && !isSidebarCollapsed">
          <input 
            type="text" 
            class="search-input" 
            placeholder="搜索对话..."
            v-model="searchQuery"
          />
        </div>
      </div>
      
      <!-- 新对话按钮 -->
      <button class="new-chat-btn" @click="handleNewChat">
        <span class="new-chat-icon">+</span>
        <span v-if="!isSidebarCollapsed">新对话</span>
      </button>

      <!-- 快捷应用区域 -->
      <div class="quick-apps" v-if="!isSidebarCollapsed">
        <div class="section-header">
          <span class="section-title">快捷应用</span>
        </div>
        <div class="app-grid">
          <div
            class="app-item"
            v-for="app in quickApps"
            :key="app.id"
            @click="handleAppClick(app)"
            :title="app.name"
          >
            <div class="app-icon" :style="{ background: app.color }">
              {{ app.icon }}
            </div>
            <span class="app-name">{{ app.name }}</span>
          </div>
        </div>
      </div>

      <!-- 对话分组 -->
      <div class="chat-groups" v-if="!isSidebarCollapsed">
        <div class="group-header" @click="toggleGroups">
          <span class="group-title">对话分组</span>
          <span class="group-toggle">{{ isGroupsExpanded ? '▼' : '▶' }}</span>
        </div>
        <div class="group-list" v-if="isGroupsExpanded">
          <div class="group-item">
            <span class="group-name">默认分组</span>
          </div>
          <div class="group-item">
            <span class="group-name">工作</span>
          </div>
          <div class="group-item">
            <span class="group-name">生活</span>
          </div>
        </div>
      </div>
      
      <!-- 最近对话 -->
      <div class="recent-chats">
        <div class="section-header" v-if="!isSidebarCollapsed">
          <span class="section-title">最近对话</span>
        </div>
        <div class="chat-list">
          <div 
            class="chat-item" 
            :class="{ active: selectedChat.value === index }"
            v-for="(chat, index) in recentChats" 
            :key="index"
            @click="handleChatClick(index)"
          >
            <div class="chat-icon" v-if="!isSidebarCollapsed">💬</div>
            <div class="chat-content" v-if="!isSidebarCollapsed">
              <span class="chat-title">{{ chat.title }}</span>
              <span class="chat-time">{{ chat.time }}</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 应用中心按钮 -->
      <div class="app-center-section" v-if="!isSidebarCollapsed">
        <div class="app-center-btn" @click="handleAppCenter">
          <span class="app-center-icon">🧩</span>
          <span class="app-center-text">应用中心</span>
        </div>
      </div>

      <!-- 用户信息 -->
      <div class="user-section">
        <div class="user-info" @click="toggleUserMenu">
          <div class="user-avatar">
            {{ userInitial }}
          </div>
          <div class="user-details" v-if="!isSidebarCollapsed">
            <div class="user-name">{{ username }}</div>
            <div class="user-uuid" v-if="!isUserMenuExpanded">{{ userUUID }}</div>
          </div>
        </div>
        <!-- 用户菜单 -->
        <div class="user-menu" v-if="isUserMenuExpanded && !isSidebarCollapsed">
          <div class="menu-item">
            <span class="menu-icon">👤</span>
            <span class="menu-text">个人资料</span>
          </div>
          <div class="menu-item">
            <span class="menu-icon">⚙️</span>
            <span class="menu-text">设置</span>
          </div>
          <div class="menu-item logout" @click="handleLogout">
            <span class="menu-icon">🚪</span>
            <span class="menu-text">退出登录</span>
          </div>
        </div>
      </div>
    </div>
    
    <!-- 右侧对话区域 -->
    <div class="chat-area">
      <!-- 对话头部 -->
      <div class="chat-header">
        <h2 class="chat-title">AI对话</h2>
        <div class="chat-actions">
          <button class="action-btn" title="设置">⚙️</button>
          <button class="action-btn" title="分享">📤</button>
        </div>
      </div>
      
      <!-- 对话消息区域 -->
      <div class="chat-messages">
        <!-- 空对话提示 -->
        <div class="empty-chat" v-if="messages.length === 0">
          <div class="empty-icon">🤖</div>
          <h3 class="empty-title">开始新对话</h3>
          <p class="empty-subtitle">输入消息或使用语音输入与AI助手交流</p>
        </div>
        
        <!-- 对话消息 -->
        <div 
          class="message" 
          :class="{ 'user-message': msg.role === 'user', 'assistant-message': msg.role === 'assistant' }"
          v-for="(msg, index) in messages" 
          :key="index"
        >
          <div class="message-avatar">
            {{ msg.role === 'user' ? userInitial : '🤖' }}
          </div>
          <div class="message-content">
            <div class="message-text">{{ msg.content }}</div>
            <div class="message-time">{{ msg.time }}</div>
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
              class="action-btn asr-btn" 
              :class="{ active: isASREnabled }"
              @click="toggleASR"
              title="语音识别"
            >
              <span class="action-icon">🎤</span>
            </button>
            <button 
              class="action-btn tts-btn" 
              :class="{ active: isTTSEnabled }"
              @click="toggleTTS"
              title="语音播放"
            >
              <span class="action-icon">🔊</span>
            </button>
            <button 
              class="send-btn" 
              @click="handleSendMessage"
              :disabled="!inputMessage.trim()"
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
import { ref, computed, onMounted } from 'vue'
import axios from 'axios'

// 侧边栏状态
const isSidebarCollapsed = ref(false)
const isSearchActive = ref(false)
const isGroupsExpanded = ref(false)
const isUserMenuExpanded = ref(false)
const searchQuery = ref('')

// 对话状态
const inputMessage = ref('')
const isASREnabled = ref(false)
const isTTSEnabled = ref(false)
const messages = ref([]) // 空对话，后续从后端获取

// 用户信息
const username = ref('用户')
const userUUID = ref('')
const userInitial = computed(() => {
  return username.value.charAt(0).toUpperCase()
})

// 页面加载时获取用户信息
onMounted(() => {
  const userInfo = localStorage.getItem('user_info')
  if (userInfo) {
    const user = JSON.parse(userInfo)
    username.value = user.name || user.username || '用户'
    userUUID.value = user.uuid || ''
  }
  // 加载最近对话列表
  loadRecentChats()
  // 加载用户可用的应用列表
  loadQuickApps()
})

// 最近对话列表
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
          time: formatTime(item.updated_at)
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

// 快捷应用列表（从后端App表获取）
const quickApps = ref([])

// 加载用户可用的应用列表
const loadQuickApps = async () => {
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
        quickApps.value = data.data.map(item => ({
          id: item.app_id,
          name: item.name || item.app_name,
          icon: item.icon || '🤖',
          color: item.color || 'linear-gradient(135deg, #6B4EED 0%, #8b5cf6 100%)'
        }))
        // 始终保留工作流编排入口在最后
        quickApps.value.push({
          id: 7,
          name: '工作流编排',
          icon: '⚙️',
          color: 'linear-gradient(135deg, #6B4EED 0%, #8b5cf6 100%)'
        })
      }
    }
  } catch (error) {
    console.error('加载应用列表失败:', error)
    // 加载失败时使用默认列表
    quickApps.value = [
      { id: 1, name: '智能问答', icon: '💬', color: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' },
      { id: 2, name: '语音合成', icon: '🔊', color: 'linear-gradient(135deg, #f093fb 0%, #f5576c 100%)' },
      { id: 3, name: '文字转语音', icon: '📝', color: 'linear-gradient(135deg, #4facfe 0%, #00f2fe 100%)' },
      { id: 4, name: 'AI绘画', icon: '🎨', color: 'linear-gradient(135deg, #43e97b 0%, #38f9d7 100%)' },
      { id: 5, name: '代码助手', icon: '💻', color: 'linear-gradient(135deg, #fa709a 0%, #fee140 100%)' },
      { id: 6, name: '翻译助手', icon: '🌐', color: 'linear-gradient(135deg, #a8edea 0%, #fed6e3 100%)' },
      { id: 7, name: '工作流编排', icon: '⚙️', color: 'linear-gradient(135deg, #6B4EED 0%, #8b5cf6 100%)' }
    ]
  }
}

// 当前选中的对话
const selectedChat = ref(0)

// 侧边栏控制
const toggleSidebar = () => {
  isSidebarCollapsed.value = !isSidebarCollapsed.value
}

const toggleSearch = () => {
  isSearchActive.value = !isSearchActive.value
}

const toggleGroups = () => {
  isGroupsExpanded.value = !isGroupsExpanded.value
}

const toggleUserMenu = () => {
  isUserMenuExpanded.value = !isUserMenuExpanded.value
}

// 对话项点击事件
const handleChatClick = (index) => {
  selectedChat.value = index
}

// 快捷应用点击事件
const handleAppClick = (app) => {
  console.log('点击了快捷应用:', app.name)
  if (app.id === 7) {
    // 跳转到工作流编辑器
    window.location.href = '/workflow/create'
  } else {
    // 跳转到对应workflow聊天页面 /workflow/chat/{app.id}
    window.location.href = `/workflow/chat/${app.id}`
  }
}

// 应用中心点击事件
const handleAppCenter = () => {
  console.log('点击了应用中心')
  // 后期可以跳转到应用中心页面
}

// 对话操作
const handleNewChat = () => {
  messages.value = []
  console.log('新建对话')
}

const handleSendMessage = async () => {
  if (!inputMessage.value.trim()) return

  const newMessage = {
    role: 'user',
    content: inputMessage.value,
    time: new Date().toLocaleTimeString()
  }

  messages.value.push(newMessage)
  inputMessage.value = ''

  // 添加AI回复的占位符
  const aiResponse = {
    role: 'assistant',
    content: '',
    time: new Date().toLocaleTimeString()
  }
  const aiMessageIndex = messages.value.length
  messages.value.push(aiResponse)

  try {
    // 调用后端AI对话接口(SSE)
    const response = await fetch('/api/ai/chat', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${localStorage.getItem('access_token')}`
      },
      body: JSON.stringify({
        message: newMessage.content,
        chat_id: null
      })
    })

    if (!response.ok) {
      throw new Error('API请求失败')
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
            messages.value[aiMessageIndex].content += match[2]
          } else if (dataLine.trim()) {
            // 如果没有匹配到，直接追加整行（兼容纯文本）
            messages.value[aiMessageIndex].content += dataLine.trim()
          }
        }
      }
    }

  } catch (error) {
    console.error('AI对话失败:', error)
    messages.value[aiMessageIndex].content = `抱歉，处理您的请求时出现了错误：${error.message}`
  } finally {
    // 重新加载聊天列表，更新最新对话排序
    loadRecentChats()
  }
}

// 语音功能
const toggleASR = () => {
  isASREnabled.value = !isASREnabled.value
  console.log('ASR状态:', isASREnabled.value)
}

const toggleTTS = () => {
  isTTSEnabled.value = !isTTSEnabled.value
  console.log('TTS状态:', isTTSEnabled.value)
}

// 退出登录
const handleLogout = async () => {
  try {
    // 调用后端退出接口
    const token = localStorage.getItem('access_token')
    await axios.post('/api/auth/logout', {}, {
      headers: {
        Authorization: `Bearer ${token}`
      }
    })
  } catch (error) {
    console.error('退出登录失败:', error)
  } finally {
    // 清除本地存储
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
  --sidebar-bg: #f8f9fa; /* 比纯白色灰一点点的颜色 */
  --text-primary: #374151;
  --text-secondary: #9ca3af;
  --border-color: #e5e7eb;
  --hover-bg: #f9fafb;
  --input-border: #d1d5db; /* 输入框静态时的边框颜色 */
}

.home-container {
  display: flex;
  height: 100vh;
  background: var(--background-color);
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  width: 100vw;
}

/* 左侧边栏 */
.sidebar {
  display: flex;
  flex-direction: column;
  width: 220px; /* 约占屏幕的五分之一 */
  background: var(--sidebar-bg);
  border-right: 1px solid var(--border-color);
  flex-shrink: 0;
  transition: all 0.3s ease;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar.collapsed .header-actions {
  justify-content: flex-end;
}

.sidebar.collapsed .search-btn {
  display: none;
}

/* 侧边栏头部 */
.sidebar-header {
  padding: 16px;
  border-bottom: 1px solid var(--border-color);
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.logo {
  flex: 1;
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-image {
  width: 32px;
  height: 32px;
  border-radius: 8px;
  object-fit: cover;
}

.logo-text {
  font-size: 24px; /* 标题“白问”最大 */
  font-weight: 700;
  color: var(--primary-color);
  font-family: 'Microsoft YaHei', sans-serif;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.action-btn {
  padding: 8px;
  background: transparent;
  border: none;
  border-radius: 6px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-secondary);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px; /* 其余字体大小均一致 */
}

.action-btn:hover {
  background: var(--hover-bg);
  color: var(--text-primary);
}

.action-icon {
  font-size: 16px;
}

/* 搜索框 */
.search-container {
  margin-top: 12px;
}

.search-input {
  width: 100%;
  padding: 8px 12px;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  font-size: 14px;
  background: var(--hover-bg);
  transition: all 0.2s ease;
}

.search-input:focus {
  outline: none;
  border-color: var(--primary-color);
  box-shadow: 0 0 0 3px rgba(107, 78, 237, 0.1);
}

/* 新对话按钮 */
.new-chat-btn {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 12px 16px;
  margin: 16px;
  background: white;
  color: var(--text-primary);
  border: 1px solid var(--border-color);
  border-radius: 10px;
  font-size: 16px; /* “新对话”按钮其次 */
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

/* 快捷应用 */
.quick-apps {
  margin: 0 16px;
  border-top: 1px solid var(--border-color);
  padding-top: 16px;
}

.quick-apps .section-header {
  margin-bottom: 12px;
}

.quick-apps .section-title {
  font-size: 14px;
  color: var(--text-secondary);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.app-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 8px;
}

.app-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 6px;
  padding: 8px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.app-item:hover {
  background: var(--hover-bg);
  transform: translateY(-2px);
}

.app-icon {
  width: 36px;
  height: 36px;
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 16px;
  color: white;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.app-name {
  font-size: 11px;
  color: var(--text-primary);
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 100%;
}

.new-chat-icon {
  font-size: 18px;
  font-weight: 600;
}

/* 对话分组 */
.chat-groups {
  margin: 0 16px;
  border-top: 1px solid var(--border-color);
  padding-top: 16px;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.group-header:hover {
  background: var(--hover-bg);
}

.group-title {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
}

.group-toggle {
  font-size: 12px;
  color: var(--text-secondary);
  transition: all 0.2s ease;
}

.group-list {
  margin-top: 8px;
  padding-left: 12px;
}

.group-item {
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.group-item:hover {
  background: var(--hover-bg);
}

.group-name {
  font-size: 14px;
  color: var(--text-primary);
}

/* 最近对话 */
.recent-chats {
  flex: 1;
  overflow: hidden;
  margin: 16px;
  border-top: 1px solid var(--border-color);
  padding-top: 16px;
}

.section-header {
  margin-bottom: 12px;
}

.section-title {
  font-size: 14px; /* 其余字体大小均一致 */
  color: var(--text-secondary);
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.chat-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.chat-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px; /* 最近对话中每一栏的大小调整，不需要那么大 */
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-primary);
}

.chat-item:hover {
  background: #e9ecef; /* 颜色更深一点的灰色 */
}

.chat-item.active {
  background: var(--sidebar-bg); /* 与左侧栏背景一样的颜色 */
  color: var(--text-primary);
  border-left: 3px solid var(--primary-color);
}

.chat-icon {
  font-size: 12px; /* 调整图标大小 */
  flex-shrink: 0;
}

.chat-content {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 2px; /* 调整间距 */
}

.chat-item .chat-content .chat-title {
  font-size: 14px !important; /* 与“最近对话”一样的大小 */
  font-weight: 400 !important;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  line-height: 1.2;
}

.chat-time {
  font-size: 12px;
  color: var(--text-secondary);
}

/* 应用中心 */
.app-center-section {
  margin: 0 16px;
  border-top: 1px solid var(--border-color);
  padding-top: 16px;
}

.app-center-btn {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 10px;
  cursor: pointer;
  transition: all 0.2s ease;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.app-center-btn:hover {
  background: var(--hover-bg);
  border-color: var(--primary-color);
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.app-center-icon {
  font-size: 18px;
}

.app-center-text {
  font-size: 14px;
  font-weight: 500;
  color: var(--text-primary);
}

/* 用户信息 */
.user-section {
  margin: 16px;
  border-top: 1px solid var(--border-color);
  padding-top: 16px;
  position: relative;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 8px 12px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
}

.user-info:hover {
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
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  border: 2px solid white;
}

.user-details {
  flex: 1;
  overflow: hidden;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: var(--text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-uuid {
  font-size: 12px;
  color: var(--text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

/* 用户菜单 */
.user-menu {
  position: absolute;
  bottom: 100%;
  left: 0;
  right: 0;
  background: var(--sidebar-bg);
  border: 1px solid var(--border-color);
  border-radius: 8px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  padding: 8px 0;
  margin-bottom: 8px;
  z-index: 100;
}

.menu-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 10px 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  font-size: 14px;
  color: var(--text-primary);
}

.menu-item:hover {
  background: var(--hover-bg);
}

.menu-item.logout {
  color: #ef4444;
}

.menu-icon {
  font-size: 16px;
  flex-shrink: 0;
}

/* 右侧对话区域 */
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
}

.chat-actions {
  display: flex;
  gap: 8px;
}

/* 对话消息区域 */
.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
  position: relative;
}

/* 空对话提示 */
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

/* 消息样式 */
.message {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  max-width: 80%;
}

.user-message {
  align-self: flex-end;
  flex-direction: row-reverse;
  margin-left: auto;
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
  background: #6B4EED;
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
  font-size: 14px;
  line-height: 1.5;
  color: var(--text-primary);
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
  font-size: 11px;
  color: var(--text-secondary);
  padding: 0 4px;
}

/* 输入区域 */
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
  border: 1px solid var(--primary-color); /* 紫色常亮 */
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
}

.chat-input:focus {
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

.asr-btn,
.tts-btn {
  padding: 8px;
  background: #f3f4f6;
  border: 1px solid var(--border-color);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: var(--text-secondary);
}

.asr-btn:hover,
.tts-btn:hover {
  background: var(--border-color);
  color: var(--text-primary);
}

.asr-btn.active,
.tts-btn.active {
  background: linear-gradient(135deg, var(--primary-color) 0%, var(--primary-hover) 100%);
  color: white;
  border-color: var(--primary-color);
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

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar,
.chat-list::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track,
.chat-list::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb,
.chat-list::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover,
.chat-list::-webkit-scrollbar-thumb:hover {
  background: var(--text-secondary);
}

/* 响应式设计 */
@media (max-width: 1024px) {
  .sidebar {
    width: 240px;
  }
  
  .message {
    max-width: 90%;
  }
}

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
}
</style>