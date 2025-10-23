import { createRouter, createWebHistory } from 'vue-router'
import type { RouteRecordRaw } from 'vue-router'

// 路由配置
import AppView from '../view/AppView.vue'
import LoginView from '../view/LoginView.vue'

// 定义路由
const routes: Array<RouteRecordRaw> = [
  {
    path: '/',
    name: 'Chat',
    component: AppView,
    meta: { requiresAuth: true }
  },  
  {
    path: '/login',
    name: 'Login',
    component: LoginView
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const isLoggedIn = localStorage.getItem('isLoggedIn') === 'true'

  if (to.meta.requiresAuth && !isLoggedIn) {
    // 需要登录但未登录，重定向到登录页
    next({ name: 'Login' })
  } else if ((to.name === 'Login') && isLoggedIn) {
    // 已登录用户访问登录页，重定向到主页
    next({ name: 'Chat' })
  } else {
    next()
  }
})

export default router
