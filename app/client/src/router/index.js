import { createRouter, createWebHistory } from 'vue-router'
import DashboardView from '@/views/DashboardView.vue'
import PageView from '@/views/PageView.vue'
import CourseContent from '@/views/CourseContent.vue'
import Ping from '@/components/Ping.vue'
import PromptIndex from '@/views/Prompts/PromptIndex.vue'
import PromptView from '@/views/Prompts/PromptView.vue'
import OutlineIndex from '@/views/Outlines/OutlineIndex.vue'
import OutlineEdit from '@/views/Outlines/OutlineEdit.vue'
import OutlineNew from '@/views/Outlines/OutlineNew.vue'
import GenerationForm from '@/views/GenerationForm.vue'
import TopicsIndex from '../views/TopicsIndex.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      name: 'dashboard',
      component: DashboardView
    },
    {
      path: '/topics',
      name: 'topics',
      component: TopicsIndex
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
      component: PromptIndex
    },
    {
      path: '/prompts/:id',
      name: 'prompt',
      component: PromptView
    },
    {
      path: '/outlines/new',
      name: 'outlines.new',
      component: OutlineNew
    },
    {
      path: '/outlines/:id',
      name: 'outline',
      component: OutlineEdit
    },
    {
      path: '/outlines',
      name: 'outlines',
      component: OutlineIndex
    },
    {
      path: '/generate',
      name: 'generate',
      component: GenerationForm
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
    
    // default redirect to home page
    { path: '/:pathMatch(.*)*', redirect: '/' }
  ]
})

export default router
