import { createRouter, createWebHistory } from 'vue-router'

// Import components
import Login from '../pages/Login.vue'
import Register from '../pages/Register.vue'
import Home from '../pages/Home.vue'
import WorkflowChat from '../pages/WorkflowChat.vue'
import KnowledgeBase from '../pages/KnowledgeBase.vue'

// Route configuration
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
    path: '/workflow/chat/:id',
    name: 'WorkflowChat',
    component: WorkflowChat,
    meta: { requiresAuth: true }
  },
  {
    path: '/knowledge',
    name: 'KnowledgeBase',
    component: KnowledgeBase,
    meta: { requiresAuth: true }
  },
  // Redirect to login page
  {
    path: '/:pathMatch(.*)*',
    redirect: '/login'
  }
]

// Create router instance
const router = createRouter({
  history: createWebHistory(),
  routes
})

// Router guard
router.beforeEach((to, from, next) => {
  // Check if route requires authentication
  if (to.matched.some(record => record.meta.requiresAuth)) {
    // Check if token exists
    const token = localStorage.getItem('access_token')
    if (!token) {
      // No token, redirect to login page
      next({ name: 'Login' })
    } else {
      // Has token, continue
      next()
    }
  } else {
    // No authentication required, proceed directly
    next()
  }
})

export default router
