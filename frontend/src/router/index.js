import { createRouter, createWebHistory } from 'vue-router'

// 导入组件
import Login from '../components/Login.vue'
import Register from '../components/Register.vue'
import Home from '../components/Home.vue'
import WorkflowChat from '../components/WorkflowChat.vue'
import WorkflowEditorPage from '../pages/WorkflowEditorPage.vue'
import KnowledgeBase from '../pages/KnowledgeBase.vue'

// 路由配置
const routes = [
  {
    path: '/',
    name: 'Home',
    component: Home,
    meta: { requiresAuth: true }
  },
  {
    path: '/login',
    name: 'Login',
    component: Login
  },
  {
    path: '/register',
    name: 'Register',
    component: Register
  },
  {
    path: '/app/chat/:id',
    name: 'AppChat',
    component: WorkflowChat,
    meta: { requiresAuth: true }
  },
  {
    path: '/workflow/create',
    name: 'WorkflowCreate',
    component: WorkflowEditorPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/workflow/edit/:uuid',
    name: 'WorkflowEdit',
    component: WorkflowEditorPage,
    meta: { requiresAuth: true }
  },
  {
    path: '/chatagent/create',
    name: 'ChatAgentCreate',
    component: WorkflowChat,
    meta: { requiresAuth: true }
  },
  {
    path: '/chatagent/edit/:uuid',
    name: 'ChatAgentEdit',
    component: WorkflowChat,
    meta: { requiresAuth: true }
  },
  {
    path: '/knowledge',
    name: 'KnowledgeBase',
    component: KnowledgeBase,
    meta: { requiresAuth: true }
  },
  // 重定向到登录页
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

// 创建路由实例
const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  // 检查路由是否需要认证
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // 检查是否有token
    const token = localStorage.getItem('access_token')
    if (!token) {
      // 没有token，重定向到登录页
      next({ name: 'Login' })
    } else {
      // 有token，继续访问
      next()
    }
  } else {
    // 不需要认证的路由，直接访问
    next()
  }
})

export default router