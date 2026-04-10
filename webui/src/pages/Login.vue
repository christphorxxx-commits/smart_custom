<template>
  <div class="login-container">
    <div class="login-wrapper">
      <div class="login-card">
        <!-- Logo & Title -->
        <div class="login-header">
          <div class="logo">
            <div class="logo-icon">🤖</div>
            <span class="logo-text">FastGPT</span>
          </div>
          <p class="subtitle">登录您的账号，开始AI对话</p>
        </div>

        <!-- Login Tabs -->
        <div class="login-tabs">
          <button
            :class="['tab-btn', { active: loginType === 'password' }]"
            @click="loginType = 'password'"
          >
            密码登录
          </button>
          <button
            :class="['tab-btn', { active: loginType === 'email' }]"
            @click="loginType = 'email'"
          >
            邮箱登录
          </button>
        </div>

        <!-- Login Form -->
        <form @submit.prevent="handleLogin" class="login-form">
          <div class="form-group">
            <label v-if="loginType === 'password'">手机号</label>
            <label v-else>邮箱</label>
            <input
              :type="loginType === 'password' ? 'tel' : 'email'"
              v-model="form.account"
              :placeholder="loginType === 'password' ? '请输入手机号' : '请输入邮箱'"
              class="form-input"
              required
            />
          </div>

          <div class="form-group">
            <label>密码</label>
            <input
              type="password"
              v-model="form.password"
              placeholder="请输入密码"
              class="form-input"
              required
            />
          </div>

          <div class="form-options">
            <label class="checkbox-label">
              <input type="checkbox" v-model="rememberMe" />
              <span>记住登录</span>
            </label>
            <a href="#" class="forgot-link">忘记密码？</a>
          </div>

          <button
            type="submit"
            class="login-btn"
            :disabled="isLoading"
          >
            <span v-if="!isLoading">登录</span>
            <span v-else>
              <span class="loading-spinner"></span>
              登录中...
            </span>
          </button>

          <div class="register-link">
            还没有账号？<router-link to="/register">注册账号</router-link>
          </div>

          <div v-if="error" class="error-message">
            {{ error }}
          </div>
        </form>
      </div>

      <!-- Footer -->
      <div class="login-footer">
        <a href="#" target="_blank">使用条款</a>
        <span>·</span>
        <a href="#" target="_blank">隐私政策</a>
      </div>
    </div>

    <!-- Background decoration -->
    <div class="bg-decoration">
      <div class="blob blob-1"></div>
      <div class="blob blob-2"></div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import axios from 'axios'
import { useRouter } from 'vue-router'

const router = useRouter()
const loginType = ref('password')
const isLoading = ref(false)
const error = ref('')
const rememberMe = ref(false)

const form = reactive({
  account: '',
  password: ''
})

const handleLogin = async () => {
  error.value = ''
  isLoading.value = true

  try {
    const loginData = loginType.value === 'password'
      ? { mobile: form.account, password: form.password }
      : { email: form.account, password: form.password }

    const response = await axios.post('/api/auth/login', loginData)

    // Save tokens
    localStorage.setItem('access_token', response.data.data.access_token)
    localStorage.setItem('refresh_token', response.data.data.refresh_token)
    localStorage.setItem('token_type', response.data.data.token_type)

    // Get user info
    const userInfoRes = await axios.get('/api/user/info', {
      headers: {
        Authorization: `${response.data.data.token_type} ${response.data.data.access_token}`
      }
    })
    localStorage.setItem('user_info', JSON.stringify(userInfoRes.data.data))

    // Redirect to home
    window.location.href = '/'
  } catch (err) {
    error.value = err.response?.data?.msg || '网络错误，请稍后重试'
    console.error('Login failed:', err)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.login-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #f5f7fa 0%, #e8ecf1 100%);
  position: relative;
  overflow: hidden;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
}

.bg-decoration {
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  z-index: 0;
  pointer-events: none;
}

.blob {
  position: absolute;
  border-radius: 50%;
  filter: blur(80px);
  opacity: 0.4;
  animation: float 20s infinite ease-in-out;
}

.blob-1 {
  width: 400px;
  height: 400px;
  background: #6366f1;
  top: -100px;
  left: -100px;
}

.blob-2 {
  width: 350px;
  height: 350px;
  background: #8b5cf6;
  bottom: -80px;
  right: -80px;
  animation-delay: -10s;
}

@keyframes float {
  0%, 100% {
    transform: translate(0, 0) scale(1);
  }
  33% {
    transform: translate(30px, -50px) scale(1.1);
  }
  66% {
    transform: translate(-20px, 20px) scale(0.9);
  }
}

.login-wrapper {
  width: 100%;
  max-width: 420px;
  padding: 24px;
  position: relative;
  z-index: 1;
}

.login-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 40px 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.6);
}

.login-header {
  text-align: center;
  margin-bottom: 32px;
}

.logo {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
  margin-bottom: 12px;
}

.logo-icon {
  width: 40px;
  height: 40px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  border-radius: 10px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 22px;
}

.logo-text {
  font-size: 28px;
  font-weight: 700;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.subtitle {
  color: #64748b;
  font-size: 14px;
  margin: 0;
}

.login-tabs {
  display: flex;
  background: #f1f5f9;
  border-radius: 12px;
  padding: 4px;
  margin-bottom: 28px;
}

.tab-btn {
  flex: 1;
  padding: 10px 16px;
  border: none;
  background: transparent;
  border-radius: 8px;
  font-size: 14px;
  font-weight: 500;
  color: #64748b;
  cursor: pointer;
  transition: all 0.2s ease;
}

.tab-btn:hover {
  color: #334155;
}

.tab-btn.active {
  background: white;
  color: #1e293b;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
}

.login-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-size: 14px;
  font-weight: 500;
  color: #334155;
}

.form-input {
  padding: 12px 16px;
  border: 1px solid #e2e8f0;
  border-radius: 10px;
  font-size: 15px;
  background: white;
  color: #1e293b;
  transition: all 0.2s ease;
  outline: none;
}

.form-input:focus {
  border-color: #6366f1;
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-input::placeholder {
  color: #94a3b8;
}

.form-options {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.checkbox-label {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 14px;
  color: #64748b;
  cursor: pointer;
}

.checkbox-label input {
  cursor: pointer;
}

.forgot-link {
  font-size: 14px;
  color: #6366f1;
  text-decoration: none;
}

.forgot-link:hover {
  text-decoration: underline;
}

.login-btn {
  margin-top: 8px;
  padding: 14px 24px;
  background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
  color: white;
  border: none;
  border-radius: 10px;
  font-size: 16px;
  font-weight: 600;
  cursor: pointer;
  transition: all 0.2s ease;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
}

.login-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.35);
}

.login-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
  transform: none;
}

.loading-spinner {
  width: 16px;
  height: 16px;
  border: 2px solid rgba(255, 255, 255, 0.3);
  border-top-color: white;
  border-radius: 50%;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

.register-link {
  text-align: center;
  font-size: 14px;
  color: #64748b;
  margin-top: 8px;
}

.register-link a,
.register-link router-link {
  color: #6366f1;
  font-weight: 500;
  text-decoration: none;
}

.register-link a:hover,
.register-link router-link:hover {
  text-decoration: underline;
}

.error-message {
  background: #fef2f2;
  color: #dc2626;
  padding: 12px 16px;
  border-radius: 8px;
  font-size: 14px;
  text-align: center;
  border: 1px solid #fecaca;
}

.login-footer {
  margin-top: 24px;
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.login-footer a {
  color: #64748b;
  text-decoration: none;
}

.login-footer a:hover {
  color: #6366f1;
}

/* Responsive */
@media (max-width: 640px) {
  .login-wrapper {
    padding: 16px;
  }

  .login-card {
    padding: 32px 24px;
  }

  .blob-1 {
    width: 250px;
    height: 250px;
  }

  .blob-2 {
    width: 200px;
    height: 200px;
  }
}
</style>
