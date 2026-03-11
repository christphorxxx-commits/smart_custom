<template>
  <div class="login-container">
    <!-- 左侧品牌区域 -->
    <div class="login-brand-section">
      <div class="brand-content">
        <h1 class="brand-title">智能AI助手</h1>
        <p class="brand-description">智能语音交互平台</p>
      </div>
    </div>
    
    <!-- 右侧登录表单区域 -->
    <div class="login-form-section">
      <div class="login-card">
        <div class="login-header">
          <h2>欢迎回来</h2>
          <p>请登录您的账号</p>
        </div>
        
        <div class="login-tabs">
          <button 
            :class="['tab-btn', { active: loginType === 'phone' }]"
            @click="loginType = 'phone'"
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
          <div v-if="loginType === 'phone'" class="form-group">
            <label for="phone">手机号</label>
            <input
              type="tel"
              id="phone"
              v-model="form.phone"
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
              <a href="#" class="register">注册账号</a>
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

const loginType = ref('phone') // 'phone' 或 'email'
const isLoading = ref(false)
const error = ref('')

const form = reactive({
  phone: '',
  email: '',
  password: ''
})

const handleLogin = async () => {
  error.value = ''
  isLoading.value = true
  
  try {
    const loginData = loginType.value === 'phone' 
      ? { phone: form.phone, password: form.password } 
      : { email: form.email, password: form.password }
    
    // 模拟登录请求
    const response = await axios.post('/api/auth/login', loginData)
    
    if (response.data.success) {
      // 登录成功，保存token并跳转
      localStorage.setItem('token', response.data.token)
      localStorage.setItem('user', JSON.stringify(response.data.user))
      
      // 跳转到主页
      window.location.href = '/'
    } else {
      error.value = response.data.message || '登录失败'
    }
  } catch (err) {
    error.value = err.response?.data?.message || '网络错误，请稍后重试'
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
  --qianwen-white: #ffffff;
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
  background: var(--qianwen-white);
  overflow: hidden;
}

/* 左侧品牌区域 */
.login-brand-section {
  flex: 1;
  background: var(--qianwen-purple-bg);
  display: flex;
  align-items: flex-start;
  justify-content: center;
  flex-direction: column;
  padding: 80px 60px;
  min-width: 400px;
  position: relative;
}

.login-brand-section::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 20% 50%, rgba(255, 255, 255, 0.1) 0%, transparent 50%);
  pointer-events: none;
}

.brand-content {
  max-width: 420px;
  color: var(--qianwen-white);
  position: relative;
  z-index: 1;
}

.brand-title {
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 12px;
  line-height: 1.1;
  letter-spacing: -0.5px;
}

.brand-description {
  font-size: 16px;
  font-weight: 400;
  opacity: 0.85;
  line-height: 1.5;
}

/* 右侧登录表单区域 */
.login-form-section {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 60px 40px;
  background: var(--qianwen-white);
  min-width: 450px;
}

.login-card {
  background: var(--qianwen-white);
  border-radius: 0;
  padding: 0;
  width: 100%;
  max-width: 420px;
}

.login-header {
  margin-bottom: 48px;
}

.login-header h2 {
  color: var(--qianwen-gray-dark);
  font-size: 36px;
  font-weight: 700;
  margin-bottom: 12px;
  letter-spacing: -0.5px;
}

.login-header p {
  color: var(--qianwen-gray);
  font-size: 15px;
  font-weight: 400;
}

.login-tabs {
  display: flex;
  margin-bottom: 40px;
  gap: 32px;
  border-bottom: none;
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
}

.tab-btn::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--qianwen-purple-primary);
  transform: scaleX(0);
  transition: transform 0.3s ease;
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
  font-size: 13px;
  color: var(--qianwen-gray-dark);
  font-weight: 600;
  letter-spacing: 0.3px;
  text-transform: uppercase;
}

.form-input {
  padding: 14px 18px;
  border: 1px solid var(--qianwen-gray-light);
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.3s ease;
  background: var(--qianwen-white);
  color: var(--qianwen-gray-dark);
}

.form-input:focus {
  outline: none;
  border-color: var(--qianwen-purple-primary);
  box-shadow: 0 0 0 4px rgba(107, 78, 237, 0.08);
  background: var(--qianwen-white);
}

.form-actions {
  margin-top: 12px;
}

.login-btn {
  width: 100%;
  padding: 16px;
  background: var(--qianwen-purple-primary);
  color: var(--qianwen-white);
  border: none;
  border-radius: 8px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.login-btn:hover:not(:disabled) {
  background: var(--qianwen-purple-dark);
  transform: translateY(-1px);
  box-shadow: 0 8px 20px var(--qianwen-purple-shadow);
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
  gap: 10px;
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
  margin-top: 20px;
  font-size: 14px;
}

.form-links a {
  color: var(--qianwen-purple-primary);
  text-decoration: none;
  transition: all 0.3s ease;
  font-weight: 500;
}

.form-links a:hover {
  color: var(--qianwen-purple-dark);
  text-decoration: underline;
}

.error-message {
  background: #FEF2F2;
  color: #DC2626;
  padding: 14px 18px;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
  margin-top: 12px;
  border: 1px solid #FECACA;
}

/* 响应式设计 */
@media (max-width: 992px) {
  .login-container {
    flex-direction: column;
  }
  
  .login-brand-section {
    min-height: 35vh;
    min-width: 100%;
    padding: 60px 40px;
  }
  
  .login-form-section {
    min-width: 100%;
    padding: 60px 30px;
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
}

@media (max-width: 480px) {
  .login-brand-section {
    padding: 50px 30px;
  }
  
  .login-form-section {
    padding: 50px 24px;
  }
  
  .login-card {
    max-width: 100%;
  }
  
  .login-header h2 {
    font-size: 28px;
  }
  
  .brand-title {
    font-size: 32px;
  }
  
  .brand-description {
    font-size: 14px;
  }
  
  .form-input {
    padding: 13px 16px;
    font-size: 14px;
  }
  
  .login-btn {
    padding: 15px;
    font-size: 15px;
  }
  
  .login-tabs {
    gap: 24px;
  }
}
</style>