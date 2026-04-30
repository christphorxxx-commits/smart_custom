/**
 * Axios请求拦截器配置
 * - 自动添加认证token
 * - 自动处理token过期刷新
 * - 统一错误处理
 */
import axios from 'axios'
import router from '../router'

// 创建axios实例
const request = axios.create({
  baseURL: '/api',
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json'
  }
})

// 标记是否正在刷新token
let isRefreshing = false
// 存储等待刷新token的请求队列
let refreshSubscribers = []

/**
 * 将请求加入刷新等待队列
 * @param {Function} callback - 回调函数
 */
function subscribeTokenRefresh(callback) {
  refreshSubscribers.push(callback)
}

/**
 * 用新token重试所有等待的请求
 * @param {string} token - 新的access token
 */
function onRefreshed(token) {
  refreshSubscribers.forEach(callback => callback(token))
  refreshSubscribers = []
}

/**
 * 清除等待队列（刷新失败时）
 */
function onRefreshFailed() {
  refreshSubscribers = []
}

/**
 * 跳转到登录页
 */
function redirectToLogin() {
  const currentPath = router.currentRoute.value.fullPath
  if (currentPath !== '/login') {
    router.push(`/login?redirect=${encodeURIComponent(currentPath)}`)
  }
}

/**
 * 清除本地存储的token
 */
function clearAuthData() {
  localStorage.removeItem('access_token')
  localStorage.removeItem('refresh_token')
  localStorage.removeItem('token_type')
  localStorage.removeItem('user_info')
}

// 请求拦截器 - 自动添加认证token
request.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('access_token')
    const tokenType = localStorage.getItem('token_type') || 'Bearer'

    if (token) {
      config.headers.Authorization = `${tokenType} ${token}`
    }

    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器 - 处理token过期和统一错误
request.interceptors.response.use(
  (response) => {
    return response
  },
  async (error) => {
    const originalRequest = error.config

    // 如果是401未授权，且不是刷新token的请求
    if (error.response?.status === 401 && !originalRequest._retry) {
      // 如果已经在刷新token了，将当前请求加入等待队列
      if (isRefreshing) {
        return new Promise((resolve) => {
          subscribeTokenRefresh((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`
            resolve(request(originalRequest))
          })
        })
      }

      // 标记正在刷新token
      originalRequest._retry = true
      isRefreshing = true

      const refreshToken = localStorage.getItem('refresh_token')

      // 如果没有refreshToken，直接跳转到登录页
      if (!refreshToken) {
        clearAuthData()
        redirectToLogin()
        return Promise.reject(error)
      }

      try {
        // 调用刷新token接口
        const response = await axios.post('/api/auth/refresh', {
          refresh_token: refreshToken
        })

        const { access_token, refresh_token, token_type } = response.data.data

        // 更新本地存储的token
        localStorage.setItem('access_token', access_token)
        localStorage.setItem('refresh_token', refresh_token)
        localStorage.setItem('token_type', token_type || 'Bearer')

        // 更新当前请求的token
        originalRequest.headers.Authorization = `${token_type || 'Bearer'} ${access_token}`

        // 重试所有等待的请求
        onRefreshed(access_token)

        // 重试当前请求
        return request(originalRequest)
      } catch (refreshError) {
        // 刷新token失败，清除认证数据并跳转到登录页
        onRefreshFailed()
        clearAuthData()
        redirectToLogin()
        return Promise.reject(refreshError)
      } finally {
        isRefreshing = false
      }
    }

    // 其他错误直接抛出
    return Promise.reject(error)
  }
)

export default request
