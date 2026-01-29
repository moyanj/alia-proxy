import { createRouter, createWebHistory } from 'vue-router'
import DefaultLayout from '@/components/layout/DefaultLayout.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      component: DefaultLayout,
      children: [
        {
          path: '',
          name: 'dashboard',
          component: () => import('../views/Dashboard.vue'),
        },
        {
          path: 'analytics',
          name: 'analytics',
          component: () => import('../views/Analytics.vue'),
        },
        {
          path: 'logs',
          name: 'logs',
          component: () => import('../views/Logs.vue'),
        },
        {
          path: 'providers',
          name: 'providers',
          component: () => import('../views/Providers.vue'),
        },
        {
          path: 'mappings',
          name: 'mappings',
          component: () => import('../views/Mappings.vue'),
        },
        {
          path: 'playground',
          name: 'playground',
          component: () => import('../views/Playground.vue'),
        },
      ],
    },
  ],
})

export default router
