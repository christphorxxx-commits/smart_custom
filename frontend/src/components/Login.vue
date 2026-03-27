<template>
  <div class="login-container">
    <!-- 左侧品牌区域 -->
    <div class="login-brand-section">
      <div class="brand-content">
        <div class="brand-logo">
          <div class="logo-icon">🤖</div>
        </div>
        <h1 class="brand-title">智能AI助手</h1>
        <p class="brand-description">智能语音交互平台</p>
        <div class="brand-slogan">
          让语音成为智能交互的新方式
        </div>
      </div>
    </div>
    
    <!-- 右侧登录表单区域 -->
    <div class="login-form-section">
      <div class="login-card">
        <div class="login-header">
          <h2>欢迎登录</h2>
          <p>请输入您的账号信息</p>
        </div>
        
        <div class="login-tabs">
          <button 
            :class="['tab-btn', { active: loginType === 'mobile' }]"
            @click="loginType = 'mobile'"
          >
            手机号登录
          </button>
          <button 
            :class="['tab-btn', { active: loginType === 'email' }]"
            @click="loginType = 'email'"
          >
            邮箱登录
          </button>
        </div>
        
        <form @submit.prevent="handleLogin" class="login-form">
          <div v-if="loginType === 'mobile'" class="form-group">
            <label for="mobile">手机号</label>
            <input
              type="tel"
              id="mobile"
              v-model="form.mobile"
              placeholder="请输入手机号"
              class="form-input"
              required
            />
          </div>
          
          <div v-else class="form-group">
            <label for="email">邮箱</label>
            <input
              type="email"
              id="email"
              v-model="form.email"
              placeholder="请输入邮箱"
              class="form-input"
              required
            />
          </div>
          
          <div class="form-group">
            <label for="password">密码</label>
            <input
              type="password"
              id="password"
              v-model="form.password"
              placeholder="请输入密码"
              class="form-input"
              required
            />
          </div>
          
          <div class="form-actions">
            <button 
              type="submit" 
              class="login-btn"
              :disabled="isLoading"
            >
              <span v-if="!isLoading">登录</span>
              <span v-else class="loading">登录中...</span>
            </button>
            <div class="form-links">
              <a href="#" class="forgot-password">忘记密码？</a>
              <a href="/register" class="register">注册账号</a>
            </div>
          </div>
          
          <div v-if="error" class="error-message">
            {{ error }}
          </div>
        </form>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'

const loginType = ref('mobile') // 'mobile' 或 'email'
const isLoading = ref(false)
const error = ref('')

const form = reactive({
  mobile: '',
  email: '',
  password: ''
})

const handleLogin = async () => {
  error.value = ''
  isLoading.value = true

  try {
    const loginData = loginType.value === 'mobile'
      ? { mobile: form.mobile, password: form.password }
      : { email: form.email, password: form.password }

    // 发送登录请求
    const response = await axios.post('/api/auth/login', loginData)

    // 保存token
    localStorage.setItem('access_token', response.data.data.access_token)
    localStorage.setItem('refresh_token', response.data.data.refresh_token)
    localStorage.setItem('token_type', response.data.data.token_type)

    // 获取用户信息
    const userInfoRes = await axios.get('/api/user/info', {
      headers: {
        Authorization: `${response.data.data.token_type} ${response.data.data.access_token}`
      }
    })
    localStorage.setItem('user_info', JSON.stringify(userInfoRes.data.data))

    // 跳转到主页
    window.location.href = '/'
  } catch (err) {
    error.value = err.response?.data?.msg || '网络错误，请稍后重试'
    console.error('登录失败:', err)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
/* 千问紫色主题变量 */
:root {
  --qianwen-purple-primary: #6B4EED;
  --qianwen-purple-light: #8B6EF0;
  --qianwen-purple-dark: #5035CC;
  --qianwen-purple-bg: linear-gradient(135deg, #6B4EED 0%, #8B6EF0 100%);
  --qianwen-purple-border: #D4C5F9;
  --qianwen-purple-shadow: rgba(107, 78, 237, 0.25);
  --qianwen-white: #ff02fc;
  --qianwen-gray-light: #f0f0f5;
  --qianwen-gray: #888899;
  --qianwen-gray-dark: #333344;
}

/* 全局样式重置 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

body {
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

.login-container {
  min-height: 100vh;
  display: flex;
  background: var(--qianwen-purple-bg);
  overflow: hidden;
}

/* 左侧品牌区域 */
.login-brand-section {
  flex: 1;
  background: rgba(180, 79, 175, 0.05);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  flex-direction: column;
  padding: 80px 60px;
  min-width: 450px;
  position: relative;
  backdrop-filter: blur(10px);
}

.login-brand-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 50%, rgba(180, 79, 175, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.brand-content {
  max-width: 450px;
  color: var(--qianwen-white);
  position: relative;
  z-index: 1;
}

.brand-logo {
  margin-bottom: 32px;
}

.logo-icon {
  width: 80px;
  height: 80px;
  background: rgba(180, 79, 175, 0.2);
  border-radius: 20px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 40px;
  backdrop-filter: blur(10px);
  border: 1px solid rgba(180, 79, 175, 0.3);
}

.brand-title {
  font-size: 56px;
  font-weight: 700;
  margin-bottom: 16px;
  line-height: 1.1;
  letter-spacing: -0.5px;
}

.brand-description {
    font-size: 18px;
    font-weight: 400;
    opacity: 0.85;
    line-height: 1.5;
    margin-bottom: 24px;
  }

  .brand-slogan {
    font-size: 16px;
    font-weight: 500;
    opacity: 0.75;
    line-height: 1.4;
    margin-bottom: 48px;
    max-width: 400px;
  }

  /* 装饰元素 */
  .login-brand-section::after {
    content: '';
    position: absolute;
    bottom: 40px;
    right: 60px;
    width: 200px;
    height: 200px;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.1) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
  }

  .login-brand-section::before {
    content: '';
    position: absolute;
    top: 60px;
    left: 60px;
    width: 150px;
    height: 150px;
    background: radial-gradient(circle, rgba(255, 255, 255, 0.08) 0%, transparent 70%);
    border-radius: 50%;
    pointer-events: none;
  }

/* 右侧登录表单区域 */
.login-form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 80px 60px;
  background: transparent;
  min-width: 500px;
  position: relative;
}

.login-form-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 80% 50%, rgba(255, 255, 255, 0.05) 0%, transparent 60%);
  pointer-events: none;
}

.login-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 24px;
  box-shadow: 0 24px 64px rgba(0, 0, 0, 0.15);
  padding: 64px;
  width: 100%;
  max-width: 480px;
  border: 1px solid rgba(255, 255, 255, 0.3);
  position: relative;
  z-index: 1;
  backdrop-filter: blur(20px);
}

.login-header {
  margin-bottom: 48px;
  text-align: center;
}

.login-header h2 {
  color: var(--qianwen-gray-dark);
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 12px;
  letter-spacing: -0.3px;
}

.login-header p {
  color: var(--qianwen-gray);
  font-size: 15px;
  font-weight: 400;
  line-height: 1.5;
}

.login-tabs {
  display: flex;
  margin-bottom: 40px;
  gap: 32px;
  border-bottom: 1px solid var(--qianwen-gray-light);
  padding-bottom: 16px;
}

.tab-btn {
  padding: 12px 0;
  border: none;
  background: none;
  font-size: 16px;
  color: var(--qianwen-gray);
  cursor: pointer;
  position: relative;
  transition: all 0.3s ease;
  font-weight: 500;
  flex: 1;
  text-align: center;
}

.tab-btn::after {
  content: '';
  position: absolute;
  bottom: -17px;
  left: 20%;
  right: 20%;
  height: 3px;
  background: var(--qianwen-purple-primary);
  transform: scaleX(0);
  transition: transform 0.3s ease;
  border-radius: 2px;
}

.tab-btn:hover {
  color: var(--qianwen-purple-primary);
}

.tab-btn.active {
  color: var(--qianwen-purple-primary);
  font-weight: 600;
}

.tab-btn.active::after {
  transform: scaleX(1);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 28px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.form-group label {
  font-size: 14px;
  color: var(--qianwen-gray-dark);
  font-weight: 600;
  letter-spacing: 0.3px;
}

.form-input {
  padding: 16px 20px;
  border: 1px solid var(--qianwen-gray-light);
  border-radius: 12px;
  font-size: 16px;
  transition: all 0.3s ease;
  background: var(--qianwen-white);
  color: var(--qianwen-gray-dark);
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.04);
}

.form-input:focus {
  outline: none;
  border-color: var(--qianwen-purple-primary);
  box-shadow: 0 0 0 3px rgba(107, 78, 237, 0.1);
  background: var(--qianwen-white);
}

.form-actions {
  margin-top: 16px;
}

.login-btn {
  width: 100%;
  padding: 16px;
  background: var(--qianwen-purple-primary);
  color: var(--qianwen-white);
  border: none;
  border-radius: 12px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  margin-bottom: 20px;
}

.login-btn:hover:not(:disabled) {
  background: var(--qianwen-purple-dark);
  transform: translateY(-1px);
  box-shadow: 0 8px 24px var(--qianwen-purple-shadow);
}

.login-btn:disabled {
  background: var(--qianwen-gray-light);
  color: var(--qianwen-gray);
  cursor: not-allowed;
  transform: none;
  box-shadow: none;
}

.loading {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.loading::before {
  content: '';
  width: 18px;
  height: 18px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: var(--qianwen-white);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.form-links {
  display: flex;
  justify-content: space-between;
  font-size: 14px;
}

.form-links a {
  color: var(--qianwen-purple-primary);
  text-decoration: none;
  transition: all 0.3s ease;
  font-weight: 500;
  padding: 8px 0;
}

.form-links a:hover {
  color: var(--qianwen-purple-dark);
  text-decoration: underline;
}

.error-message {
  background: #FEF2F2;
  color: #DC2626;
  padding: 14px 18px;
  border-radius: 10px;
  font-size: 14px;
  text-align: center;
  border: 1px solid #FECACA;
  margin-top: 16px;
  animation: fadeIn 0.3s ease;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 */
@media (max-width: 1200px) {
  .login-container {
    flex-direction: column;
  }
  
  .login-brand-section {
    min-height: 40vh;
    min-width: 100%;
    padding: 60px 40px;
  }
  
  .login-form-section {
    min-width: 100%;
    padding: 60px 40px;
  }
  
  .brand-title {
    font-size: 48px;
  }
  
  .brand-description {
    font-size: 16px;
  }
  
  .login-header h2 {
    font-size: 36px;
  }
  
  .login-card {
    max-width: 450px;
  }
}

@media (max-width: 768px) {
  .login-brand-section {
    padding: 50px 30px;
  }
  
  .login-form-section {
    padding: 50px 30px;
  }
  
  .brand-title {
    font-size: 40px;
  }
  
  .brand-description {
    font-size: 15px;
  }
  
  .login-header h2 {
    font-size: 32px;
  }
  
  .login-card {
    padding: 48px;
    max-width: 100%;
  }
  
  .logo-icon {
    width: 70px;
    height: 70px;
    font-size: 36px;
  }
  
  .feature-icon {
    width: 36px;
    height: 36px;
    font-size: 16px;
  }
  
  .feature-item {
    font-size: 15px;
  }
}

@media (max-width: 480px) {
  .login-brand-section {
    padding: 40px 24px;
  }
  
  .login-form-section {
    padding: 40px 24px;
  }
  
  .brand-title {
    font-size: 32px;
  }
  
  .brand-description {
    font-size: 14px;
  }
  
  .login-header h2 {
    font-size: 28px;
  }
  
  .login-card {
    padding: 36px;
  }
  
  .login-tabs {
    gap: 24px;
  }
  
  .form-input {
    padding: 14px 16px;
    font-size: 15px;
  }
  
  .login-btn {
    padding: 16px;
    font-size: 16px;
  }
  
  .logo-icon {
    width: 60px;
    height: 60px;
    font-size: 32px;
  }
  
  .feature-icon {
    width: 32px;
    height: 32px;
    font-size: 14px;
  }
  
  .feature-item {
    font-size: 14px;
  }
  
  .brand-features {
    gap: 16px;
  }
  
  .brand-description {
    margin-bottom: 32px;
  }
  
  .brand-logo {
    margin-bottom: 24px;
  }
}
</style>