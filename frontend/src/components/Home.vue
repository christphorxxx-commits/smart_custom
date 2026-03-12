<template>
  <div class="home-container">
    <!-- 左侧边栏 -->
    <div class="sidebar">
      <!-- 顶部应用区域 -->
      <div class="sidebar-apps">
        <div class="sidebar-header">
          <div class="logo">
            <span class="logo-icon">🤖</span>
            <span class="logo-text">智能AI助手</span>
          </div>
        </div>
        
        <div class="apps-section">
          <div class="section-title">应用</div>
          <div class="apps-list">
            <div class="app-item active">
              <span class="app-icon">💬</span>
              <span class="app-name">智能对话</span>
            </div>
            <div class="app-item">
              <span class="app-icon">📝</span>
              <span class="app-name">写作助手</span>
            </div>
            <div class="app-item">
              <span class="app-icon">🎨</span>
              <span class="app-name">图像生成</span>
            </div>
            <div class="app-item">
              <span class="app-icon">📊</span>
              <span class="app-name">数据分析</span>
            </div>
          </div>
        </div>
      </div>
      
      <!-- 底部对话记录区域 -->
      <div class="sidebar-history">
        <div class="history-header">
          <span class="history-title">对话记录</span>
          <button class="new-chat-btn" @click="handleNewChat">
            <span class="new-chat-icon">+</span>
            新建对话
          </button>
        </div>
        <div class="history-list">
          <div class="history-item active">
            <span class="history-text">智能语音识别测试</span>
            <span class="history-time">刚刚</span>
          </div>
          <div class="history-item">
            <span class="history-text">自然语言处理对话</span>
            <span class="history-time">2小时前</span>
          </div>
          <div class="history-item">
            <span class="history-text">实时响应测试</span>
            <span class="history-time">昨天</span>
          </div>
          <div class="history-item">
            <span class="history-text">AI助手使用指南</span>
            <span class="history-time">3天前</span>
          </div>
        </div>
        
        <!-- 用户信息 -->
        <div class="user-section">
          <div class="user-info">
            <div class="user-avatar">U</div>
            <div class="user-details">
              <div class="user-name">用户</div>
              <div class="user-email">user@example.com</div>
            </div>
          </div>
          <button class="logout-btn" @click="handleLogout">
            <span class="logout-icon">→</span>
            退出
          </button>
        </div>
      </div>
    </div>
    
    <!-- 右侧对话区域 -->
    <div class="chat-area">
      <!-- 对话头部 -->
      <div class="chat-header">
        <h2 class="chat-title">智能对话</h2>
        <div class="chat-actions">
          <button class="action-btn" title="设置">⚙️</button>
          <button class="action-btn" title="分享">📤</button>
        </div>
      </div>
      
      <!-- 对话消息区域 -->
      <div class="chat-messages">
        <div class="message user-message">
          <div class="message-avatar user-avatar">U</div>
          <div class="message-content">
            <div class="message-text">你好，我想了解一下智能语音识别的功能</div>
            <div class="message-time">10:30</div>
          </div>
        </div>
        
        <div class="message assistant-message">
          <div class="message-avatar assistant-avatar">🤖</div>
          <div class="message-content">
            <div class="message-text">您好！智能语音识别功能可以通过麦克风实时将您的语音转换为文字，然后由AI助手进行理解和响应。您可以通过点击输入框右侧的麦克风按钮开始语音输入。</div>
            <div class="message-time">10:30</div>
          </div>
        </div>
        
        <div class="message user-message">
          <div class="message-avatar user-avatar">U</div>
          <div class="message-content">
            <div class="message-text">那如何使用语音播放功能呢？</div>
            <div class="message-time">10:31</div>
          </div>
        </div>
        
        <div class="message assistant-message">
          <div class="message-avatar assistant-avatar">🤖</div>
          <div class="message-content">
            <div class="message-text">语音播放功能（TTS）可以将AI助手的回复转换为语音播放出来。您可以点击输入框右侧的扬声器按钮来开启或关闭语音播放功能。</div>
            <div class="message-time">10:31</div>
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
import { ref } from 'vue'
import axios from 'axios'

const inputMessage = ref('')
const isASREnabled = ref(false)
const isTTSEnabled = ref(false)

const handleLogout = () => {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('token_type')
  window.location.href = '/login'
}

const handleNewChat = () => {
  console.log('新建对话')
}

const handleSendMessage = () => {
  if (!inputMessage.value.trim()) return
  console.log('发送消息:', inputMessage.value)
  inputMessage.value = ''
}

const toggleASR = () => {
  isASREnabled.value = !isASREnabled.value
  console.log('ASR状态:', isASREnabled.value)
}

const toggleTTS = () => {
  isTTSEnabled.value = !isTTSEnabled.value
  console.log('TTS状态:', isTTSEnabled.value)
}

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
.home-container {
  display: flex;
  height: 100vh;
  background: #f5f5f5;
  overflow: hidden;
}

/* 左侧边栏 */
.sidebar {
  display: flex;
  flex-direction: column;
  width: 280px;
  background: white;
  border-right: 1px solid #e5e7eb;
  flex-shrink: 0;
}

.sidebar-apps {
  flex: 0 0 auto;
  padding: 16px;
  border-bottom: 1px solid #e5e7eb;
}

.sidebar-header {
  margin-bottom: 20px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 10px;
}

.logo-icon {
  font-size: 28px;
}

.logo-text {
  font-size: 18px;
  font-weight: 600;
  color: #6B4EED;
}

.apps-section {
  display: flex;
  flex-direction: column;
  gap: 12px;
}

.section-title {
  font-size: 12px;
  color: #9ca3af;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.apps-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.app-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #374151;
}

.app-item:hover {
  background: #f9fafb;
}

.app-item.active {
  background: linear-gradient(135deg, #6B4EED 0%, #8B6EF0 100%);
  color: white;
}

.app-icon {
  font-size: 18px;
}

.app-name {
  font-size: 14px;
  font-weight: 500;
}

.sidebar-history {
  flex: 1;
  display: flex;
  flex-direction: column;
  padding: 16px;
  overflow: hidden;
}

.history-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}

.history-title {
  font-size: 12px;
  color: #9ca3af;
  font-weight: 500;
  text-transform: uppercase;
  letter-spacing: 0.5px;
}

.new-chat-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: linear-gradient(135deg, #6B4EED 0%, #8B6EF0 100%);
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
}

.new-chat-btn:hover {
  transform: translateY(-1px);
  box-shadow: 0 4px 12px rgba(107, 78, 237, 0.3);
}

.new-chat-icon {
  font-size: 16px;
  font-weight: 600;
}

.history-list {
  flex: 1;
  overflow-y: auto;
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 12px 16px;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #374151;
}

.history-item:hover {
  background: #f9fafb;
}

.history-item.active {
  background: #f3f0ff;
  color: #6B4EED;
}

.history-text {
  font-size: 14px;
  font-weight: 500;
  flex: 1;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.history-time {
  font-size: 12px;
  color: #9ca3af;
  margin-left: 12px;
}

.user-section {
  margin-top: auto;
  padding-top: 16px;
  border-top: 1px solid #e5e7eb;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 12px;
}

.user-avatar {
  width: 36px;
  height: 36px;
  border-radius: 50%;
  background: linear-gradient(135deg, #6B4EED 0%, #8B6EF0 100%);
  color: white;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 14px;
  font-weight: 600;
}

.user-details {
  flex: 1;
  overflow: hidden;
}

.user-name {
  font-size: 14px;
  font-weight: 600;
  color: #374151;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.user-email {
  font-size: 12px;
  color: #9ca3af;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logout-btn {
  display: flex;
  align-items: center;
  gap: 6px;
  padding: 8px 12px;
  background: #f9fafb;
  color: #6b7280;
  border: 1px solid #e5e7eb;
  border-radius: 6px;
  font-size: 12px;
  font-weight: 500;
  cursor: pointer;
  transition: all 0.2s ease;
  width: 100%;
}

.logout-btn:hover {
  background: #f3f4f6;
  color: #374151;
}

.logout-icon {
  font-size: 14px;
}

/* 右侧对话区域 */
.chat-area {
  flex: 1;
  display: flex;
  flex-direction: column;
  background: #fafafa;
}

.chat-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px 24px;
  background: white;
  border-bottom: 1px solid #e5e7eb;
}

.chat-title {
  font-size: 18px;
  font-weight: 600;
  color: #374151;
}

.chat-actions {
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
  color: #6b7280;
}

.action-btn:hover {
  background: #f9fafb;
  color: #374151;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 24px;
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.message {
  display: flex;
  gap: 12px;
  max-width: 80%;
}

.user-message {
  align-self: flex-start;
}

.assistant-message {
  align-self: flex-end;
  flex-direction: row-reverse;
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

.user-avatar {
  background: linear-gradient(135deg, #6B4EED 0%, #8B6EF0 100%);
  color: white;
}

.assistant-avatar {
  background: #f3f0ff;
  color: #6B4EED;
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
  color: #374151;
}

.user-message .message-text {
  background: white;
  border: 1px solid #e5e7eb;
}

.assistant-message .message-text {
  background: linear-gradient(135deg, #6B4EED 0%, #8B6EF0 100%);
  color: white;
}

.message-time {
  font-size: 11px;
  color: #9ca3af;
  padding: 0 4px;
}

.chat-input-area {
  padding: 20px 24px;
  background: white;
  border-top: 1px solid #e5e7eb;
}

.input-container {
  display: flex;
  gap: 12px;
  align-items: flex-end;
  background: #f9fafb;
  border: 1px solid #e5e7eb;
  border-radius: 12px;
  padding: 12px;
  transition: all 0.2s ease;
}

.input-container:focus-within {
  border-color: #6B4EED;
  box-shadow: 0 0 0 3px rgba(107, 78, 237, 0.1);
}

.chat-input {
  flex: 1;
  border: none;
  background: transparent;
  font-size: 14px;
  color: #374151;
  resize: none;
  min-height: 24px;
  max-height: 120px;
  font-family: inherit;
}

.chat-input:focus {
  outline: none;
}

.chat-input::placeholder {
  color: #9ca3af;
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
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s ease;
  color: #6b7280;
}

.asr-btn:hover,
.tts-btn:hover {
  background: #e5e7eb;
  color: #374151;
}

.asr-btn.active,
.tts-btn.active {
  background: linear-gradient(135deg, #6B4EED 0%, #8B6EF0 100%);
  color: white;
  border-color: #6B4EED;
}

.action-icon {
  font-size: 18px;
}

.send-btn {
  padding: 8px 16px;
  background: linear-gradient(135deg, #6B4EED 0%, #8B6EF0 100%);
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
  color: #9ca3af;
  text-align: center;
  margin-top: 8px;
}

/* 滚动条样式 */
.chat-messages::-webkit-scrollbar,
.history-list::-webkit-scrollbar {
  width: 6px;
}

.chat-messages::-webkit-scrollbar-track,
.history-list::-webkit-scrollbar-track {
  background: transparent;
}

.chat-messages::-webkit-scrollbar-thumb,
.history-list::-webkit-scrollbar-thumb {
  background: #d1d5db;
  border-radius: 3px;
}

.chat-messages::-webkit-scrollbar-thumb:hover,
.history-list::-webkit-scrollbar-thumb:hover {
  background: #9ca3af;
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
    display: none;
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