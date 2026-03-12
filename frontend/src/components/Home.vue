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
  min-height: 100vh;
  background: linear-gradient(135deg, #6B4EED 0%, #8B6EF0 100%);
  color: white;
}

.home-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 40px;
  background: rgba(255, 255, 255, 0.1);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid rgba(255, 255, 255, 0.2);
}

.logo {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  font-size: 32px;
}

.logo-text {
  font-size: 24px;
  font-weight: 700;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 20px;
}

.welcome-text {
  font-size: 16px;
  opacity: 0.8;
}

.logout-btn {
  padding: 8px 16px;
  background: rgba(255, 255, 255, 0.2);
  color: white;
  border: 1px solid rgba(255, 255, 255, 0.3);
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.3s ease;
}

.logout-btn:hover {
  background: rgba(255, 255, 255, 0.3);
  transform: translateY(-1px);
}

.home-content {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 40px;
  padding: 80px 40px;
  flex-wrap: wrap;
}

.feature-card {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 20px;
  padding: 40px;
  text-align: center;
  width: 300px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.feature-card:hover {
  background: rgba(255, 255, 255, 0.15);
  transform: translateY(-10px);
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.1);
}

.feature-icon {
  font-size: 48px;
  margin-bottom: 20px;
}

.feature-card h3 {
  font-size: 20px;
  font-weight: 600;
  margin-bottom: 12px;
}

.feature-card p {
  font-size: 14px;
  opacity: 0.8;
  line-height: 1.5;
}

@media (max-width: 768px) {
  .home-header {
    padding: 16px 24px;
  }
  
  .logo-text {
    font-size: 20px;
  }
  
  .home-content {
    padding: 40px 24px;
    gap: 24px;
  }
  
  .feature-card {
    width: 100%;
    max-width: 300px;
    padding: 32px;
  }
}
</style>