import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '@/views/DashboardView.vue'
import PageView from '@/views/PageView.vue'
import Ping from '@/components/Ping.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView
    },
    {
      path: '/page/:id',
      name: 'page',
      component: PageView
    },
    {
      path: '/ping',
      name: 'ping',
      component: Ping
      /* NOTE:
      * route level code-splitting
      * this generates a separate chunk (About.[hash].js) for this route
      * component: () => import('@/views/AboutView.vue')
      */ 
    },
  ]
})

export default router
