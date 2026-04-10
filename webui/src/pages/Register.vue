<template>
  <div class="register-container">
    <div class="register-wrapper">
      <div class="register-card">
        <!-- Logo & Title -->
        <div class="register-header">
          <div class="logo">
            <div class="logo-icon">🤖</div>
            <span class="logo-text">FastGPT</span>
          </div>
          <p class="subtitle">创建账号，开启智能AI体验</p>
        </div>

        <!-- Register Form -->
        <form @submit.prevent="handleRegister" class="register-form">
          <div class="form-group">
            <label>用户名</label>
            <input
              type="text"
              v-model="form.username"
              placeholder="请输入用户名"
              class="form-input"
              required
            />
          </div>

          <div class="form-group">
            <label>手机号</label>
            <input
              type="tel"
              v-model="form.mobile"
              placeholder="请输入手机号"
              class="form-input"
              required
            />
          </div>

          <div class="form-group">
            <label>密码</label>
            <input
              type="password"
              v-model="form.password"
              placeholder="请输入密码（至少6位）"
              class="form-input"
              required
              minlength="6"
            />
          </div>

          <div class="form-group">
            <label>确认密码</label>
            <input
              type="password"
              v-model="form.confirmPassword"
              placeholder="请再次输入密码"
              class="form-input"
              required
              minlength="6"
            />
          </div>

          <div class="agreement">
            <label class="checkbox-label">
              <input type="checkbox" v-model="agreeTerms" required />
              <span>我已阅读并同意 <a href="#" target="_blank">使用条款</a> 和 <a href="#" target="_blank">隐私政策</a></span>
            </label>
          </div>

          <button
            type="submit"
            class="register-btn"
            :disabled="isLoading || !agreeTerms"
          >
            <span v-if="!isLoading">注册</span>
            <span v-else>
              <span class="loading-spinner"></span>
              注册中...
            </span>
          </button>

          <div class="login-link">
            已有账号？<router-link to="/login">立即登录</router-link>
          </div>

          <div v-if="error" class="error-message">
            {{ error }}
          </div>
        </form>
      </div>

      <!-- Footer -->
      <div class="register-footer">
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
const isLoading = ref(false)
const error = ref('')
const agreeTerms = ref(false)

const form = reactive({
  username: '',
  mobile: '',
  password: '',
  confirmPassword: ''
})

const handleRegister = async () => {
  error.value = ''

  // Validate password
  if (form.password !== form.confirmPassword) {
    error.value = '两次输入的密码不一致'
    return
  }

  if (form.password.length < 6) {
    error.value = '密码长度至少6位'
    return
  }

  isLoading.value = true

  try {
    const registerData = {
      username: form.username,
      mobile: form.mobile,
      password: form.password
    }

    await axios.post('/api/user/register', registerData)

    // Registration success, redirect to login
    window.location.href = '/login'
  } catch (err) {
    error.value = err.response?.data?.msg || '网络错误，请稍后重试'
    console.error('Registration failed:', err)
  } finally {
    isLoading.value = false
  }
}
</script>

<style scoped>
.register-container {
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

.register-wrapper {
  width: 100%;
  max-width: 420px;
  padding: 24px;
  position: relative;
  z-index: 1;
}

.register-card {
  background: rgba(255, 255, 255, 0.8);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 40px 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.6);
}

.register-header {
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

.register-form {
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

.agreement {
  margin-top: 4px;
}

.checkbox-label {
  display: flex;
  align-items: flex-start;
  gap: 6px;
  font-size: 13px;
  color: #64748b;
  cursor: pointer;
  line-height: 1.4;
}

.checkbox-label input {
  cursor: pointer;
  margin-top: 2px;
}

.checkbox-label a {
  color: #6366f1;
  text-decoration: none;
}

.checkbox-label a:hover {
  text-decoration: underline;
}

.register-btn {
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

.register-btn:hover:not(:disabled) {
  transform: translateY(-1px);
  box-shadow: 0 8px 20px rgba(99, 102, 241, 0.35);
}

.register-btn:disabled {
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

.login-link {
  text-align: center;
  font-size: 14px;
  color: #64748b;
  margin-top: 8px;
}

.login-link a,
.login-link router-link {
  color: #6366f1;
  font-weight: 500;
  text-decoration: none;
}

.login-link a:hover,
.login-link router-link:hover {
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

.register-footer {
  margin-top: 24px;
  text-align: center;
  color: #94a3b8;
  font-size: 13px;
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 12px;
}

.register-footer a {
  color: #64748b;
  text-decoration: none;
}

.register-footer a:hover {
  color: #6366f1;
}

/* Responsive */
@media (max-width: 640px) {
  .register-wrapper {
    padding: 16px;
  }

  .register-card {
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
