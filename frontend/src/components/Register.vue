<template>
  <div class="login-container">
    <!-- 注册表单区域 -->
    <div class="login-form-section">
      <div class="login-card">
        <div class="login-header">
          <h2>创建账号</h2>
          <p>请填写以下信息完成注册</p>
        </div>
        
        <div class="login-tabs">
          <button 
            :class="['tab-btn', { active: registerType === 'mobile' }]"
            @click="registerType = 'mobile'"
          >
            手机号注册
          </button>
          <button 
            :class="['tab-btn', { active: registerType === 'email' }]"
            @click="registerType = 'email'"
          >
            邮箱注册
          </button>
        </div>
        
        <form @submit.prevent="handleRegister" class="login-form">
          <div class="form-row">
            <div class="form-group">
              <label for="username">用户名</label>
              <input
                type="text"
                id="username"
                v-model="form.username"
                placeholder="请输入用户名"
                class="form-input"
                required
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group" v-if="registerType === 'mobile'">
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
            
            <div class="form-group" v-else>
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
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="password">密码</label>
              <input
                type="password"
                id="password"
                v-model="form.password"
                placeholder="请输入密码（至少6位）"
                class="form-input"
                required
                minlength="6"
              />
            </div>
          </div>
          
          <div class="form-row">
            <div class="form-group">
              <label for="confirmPassword">确认密码</label>
              <input
                type="password"
                id="confirmPassword"
                v-model="form.confirmPassword"
                placeholder="请再次输入密码"
                class="form-input"
                required
                minlength="6"
              />
            </div>
          </div>
          
          <div class="form-actions">
            <button 
              type="submit" 
              class="login-btn"
              :disabled="isLoading"
            >
              <span v-if="!isLoading">注册</span>
              <span v-else class="loading">注册中...</span>
            </button>
            <div class="form-links">
              <a href="/login" class="login-link">已有账号？登录</a>
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

const registerType = ref('mobile') // 'mobile' 或 'email'
const isLoading = ref(false)
const error = ref('')

const form = reactive({
  username: '',
  mobile: '',
  email: '',
  password: '',
  confirmPassword: ''
})

const handleRegister = async () => {
  error.value = ''
  
  // 验证密码是否一致
  if (form.password !== form.confirmPassword) {
    error.value = '两次输入的密码不一致'
    return
  }
  
  // 验证手机号或邮箱至少填写一个
  if (!form.mobile && !form.email) {
    error.value = '手机号和邮箱不能同时为空'
    return
  }
  
  isLoading.value = true
  
  try {
    const registerData = {
      username: form.username,
      password: form.password
    }
    
    // 根据注册类型添加对应字段
    if (registerType.value === 'mobile') {
      registerData.mobile = form.mobile
    } else {
      registerData.email = form.email
    }
    
    // 发送注册请求
    const response = await axios.post('/api/user/register', registerData)
    
    // 注册成功，跳转到登录页
    window.location.href = '/login'
  } catch (err) {
    error.value = err.response?.data?.msg || '网络错误，请稍后重试'
    console.error('注册失败:', err)
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
  background: var(--qianwen-purple-bg);
  margin: 0;
  padding: 0;
  min-height: 100vh;
}

.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: var(--qianwen-purple-bg);
  overflow: hidden;
  padding: 60px;
  position: relative;
}

.login-container::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: radial-gradient(circle at 50% 50%, rgba(255, 255, 255, 0.05) 0%, transparent 70%);
  pointer-events: none;
}

/* 注册表单区域 */
.login-form-section {
  display: flex;
  align-items: center;
  justify-content: center;
  background: transparent;
  position: relative;
  z-index: 1;
}

/* 注册方式切换按钮 */
.login-tabs {
  display: flex;
  margin-bottom: 40px;
  border-radius: 16px;
  background: var(--qianwen-gray-light);
  overflow: hidden;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.tab-btn {
  flex: 1;
  padding: 16px 0;
  background: transparent;
  border: none;
  font-size: 16px;
  font-weight: 600;
  color: var(--qianwen-gray);
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  z-index: 1;
  letter-spacing: 0.5px;
}

.tab-btn:hover {
  color: var(--qianwen-gray-dark);
  background: rgba(107, 78, 237, 0.05);
}

.tab-btn.active {
  color: var(--qianwen-white);
  background: var(--qianwen-purple-primary);
  box-shadow: 0 4px 16px var(--qianwen-purple-shadow);
}

.login-card {
  background: rgba(255, 255, 255, 0.98);
  border-radius: 32px;
  box-shadow: 0 32px 80px rgba(0, 0, 0, 0.2);
  padding: 80px;
  width: 100%;
  max-width: 600px;
  border: 1px solid rgba(255, 255, 255, 0.4);
  position: relative;
  z-index: 1;
  backdrop-filter: blur(30px);
}

.login-header {
  margin-bottom: 60px;
  text-align: center;
}

.login-header h2 {
  color: var(--qianwen-gray-dark);
  font-size: 48px;
  font-weight: 700;
  margin-bottom: 16px;
  letter-spacing: -0.5px;
  line-height: 1.1;
}

.login-header p {
  color: var(--qianwen-gray);
  font-size: 18px;
  font-weight: 400;
  line-height: 1.6;
  max-width: 480px;
  margin: 0 auto;
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 32px;
}

.form-row {
  display: flex;
  gap: 24px;
  align-items: flex-start;
}

.form-group {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 12px;
  min-width: 0;
}

.form-group label {
  font-size: 16px;
  color: var(--qianwen-gray-dark);
  font-weight: 600;
  letter-spacing: 0.3px;
  line-height: 1.4;
}

.form-input {
  padding: 20px 24px;
  border: 1px solid var(--qianwen-gray-light);
  border-radius: 16px;
  font-size: 18px;
  transition: all 0.3s ease;
  background: var(--qianwen-white);
  color: var(--qianwen-gray-dark);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.06);
  min-height: 64px;
}

.form-input:focus {
  outline: none;
  border-color: var(--qianwen-purple-primary);
  box-shadow: 0 0 0 4px rgba(107, 78, 237, 0.15);
  background: var(--qianwen-white);
  transform: translateY(-1px);
}

.form-actions {
  margin-top: 24px;
  display: flex;
  flex-direction: column;
  gap: 24px;
}

.login-btn {
  width: 100%;
  padding: 20px;
  background: var(--qianwen-purple-primary);
  color: var(--qianwen-white);
  border: none;
  border-radius: 16px;
  font-size: 18px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
  min-height: 64px;
  display: flex;
  align-items: center;
  justify-content: center;
  letter-spacing: 1px;
  text-transform: uppercase;
}

.login-btn:hover:not(:disabled) {
  background: var(--qianwen-purple-dark);
  transform: translateY(-2px);
  box-shadow: 0 12px 32px var(--qianwen-purple-shadow);
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
  gap: 16px;
}

.loading::before {
  content: '';
  width: 24px;
  height: 24px;
  border: 3px solid rgba(255, 255, 255, 0.3);
  border-top-color: var(--qianwen-white);
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.form-links {
  display: flex;
  justify-content: center;
  font-size: 16px;
  padding: 8px 0;
}

.form-links a {
  color: var(--qianwen-purple-primary);
  text-decoration: none;
  transition: all 0.3s ease;
  font-weight: 600;
  padding: 12px 0;
  position: relative;
}

.form-links a:hover {
  color: var(--qianwen-purple-dark);
}

.form-links a::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 2px;
  background: var(--qianwen-purple-primary);
  transform: scaleX(0);
  transform-origin: left;
  transition: transform 0.3s ease;
}

.form-links a:hover::after {
  transform: scaleX(1);
}

.error-message {
  background: #FEF2F2;
  color: #DC2626;
  padding: 18px 24px;
  border-radius: 12px;
  font-size: 16px;
  text-align: center;
  border: 1px solid #FECACA;
  margin-top: 24px;
  animation: fadeIn 0.3s ease;
  box-shadow: 0 4px 12px rgba(220, 38, 38, 0.1);
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(-12px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

/* 响应式设计 - 电脑端 */
@media (min-width: 1200px) {
  .login-card {
    max-width: 640px;
    padding: 96px;
  }
  
  .login-header h2 {
    font-size: 56px;
  }
  
  .form-input {
    padding: 24px 28px;
    font-size: 20px;
    min-height: 72px;
  }
  
  .login-btn {
    padding: 24px;
    font-size: 20px;
    min-height: 72px;
  }
}

/* 响应式设计 - 平板和小屏幕电脑 */
@media (max-width: 1199px) {
  .login-container {
    padding: 40px;
  }
  
  .login-card {
    max-width: 520px;
    padding: 64px;
  }
  
  .login-header h2 {
    font-size: 40px;
  }
  
  .form-input {
    padding: 18px 22px;
    font-size: 16px;
    min-height: 56px;
  }
  
  .login-btn {
    padding: 18px;
    font-size: 16px;
    min-height: 56px;
  }
}

/* 响应式设计 - 移动端 */
@media (max-width: 768px) {
  .login-container {
    padding: 30px;
  }
  
  .login-card {
    padding: 48px;
    max-width: 100%;
  }
  
  .login-header h2 {
    font-size: 36px;
  }
  
  .form-row {
    flex-direction: column;
    gap: 24px;
  }
  
  .form-input {
    padding: 16px 20px;
    font-size: 16px;
    min-height: 52px;
  }
  
  .login-btn {
    padding: 16px;
    font-size: 16px;
    min-height: 52px;
  }
  
  .login-tabs {
    margin-bottom: 32px;
  }
  
  .tab-btn {
    padding: 14px 0;
    font-size: 14px;
  }
  
  .login-header {
    margin-bottom: 48px;
  }
  
  .login-form {
    gap: 24px;
  }
}

@media (max-width: 480px) {
  .login-container {
    padding: 24px;
  }
  
  .login-card {
    padding: 36px;
  }
  
  .login-header h2 {
    font-size: 28px;
  }
  
  .login-header p {
    font-size: 16px;
  }
  
  .form-input {
    padding: 14px 18px;
    font-size: 15px;
    min-height: 48px;
  }
  
  .login-btn {
    padding: 14px;
    font-size: 15px;
    min-height: 48px;
  }
  
  .login-tabs {
    margin-bottom: 24px;
  }
  
  .tab-btn {
    padding: 12px 0;
    font-size: 13px;
  }
  
  .login-header {
    margin-bottom: 40px;
  }
  
  .login-form {
    gap: 20px;
  }
}
</style>