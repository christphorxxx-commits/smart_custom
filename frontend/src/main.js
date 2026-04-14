import { createApp } from 'vue'
import axios from 'axios'
import './style.css'
import App from './App.vue'
import router from './router'

// 配置 axios 拦截器，自动添加认证 token
axios.interceptors.request.use(
  config => {
    const token = localStorage.getItem('access_token')
    const tokenType = localStorage.getItem('token_type') || 'Bearer'
    if (token) {
      config.headers.Authorization = `${tokenType} ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

// 响应拦截器处理 401
axios.interceptors.response.use(
  response => response,
  error => {
    if (error.response && error.response.status === 401) {
      // 清除本地存储跳转到登录页
      localStorage.removeItem('access_token')
      localStorage.removeItem('refresh_token')
      localStorage.removeItem('user_info')
      router.push('/login')
    }
    return Promise.reject(error)
  }
)

const app = createApp(App)
app.config.globalProperties.$axios = axios
app.use(router)
app.mount('#app')
