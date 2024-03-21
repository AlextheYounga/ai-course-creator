import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '@/views/DashboardView.vue'
import PageView from '@/views/PageView.vue'
import CourseContent from '@/views/CourseContent.vue'
import Ping from '@/components/Ping.vue'
import PromptsIndex from '@/views/Prompts/PromptsIndex.vue'
import PromptView from '@/views/Prompts/PromptView.vue'
import OutlinesIndex from '@/views/Outlines/OutlinesIndex.vue'
import OutlineView from '@/views/Outlines/OutlineView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView
    },
    {
      path: '/pages/:id',
      name: 'page',
      component: PageView
    },
    {
      path: '/courses/:id',
      name: 'course',
      component: CourseContent
    },
    {
      path: '/prompts',
      name: 'prompts',
      component: PromptsIndex
    },
    {
      path: '/prompts/:id',
      name: 'prompt',
      component: PromptView
    },
    {
      path: '/outlines',
      name: 'outlines',
      component: OutlinesIndex
    },
    {
      path: '/outlines/:id',
      name: 'outline',
      component: OutlineView
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
