import { createApp } from 'vue'
import './style.css'
import App from './App.vue'
import router from './router'
import request from './utils/request'

const app = createApp(App)

// 使用配置好的request实例（带认证拦截器）
app.config.globalProperties.$axios = request
app.config.globalProperties.$http = request

app.use(router)
app.mount('#app')
