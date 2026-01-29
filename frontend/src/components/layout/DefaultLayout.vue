<template>
  <div class="h-screen overflow-hidden bg-gray-50 dark:bg-gray-900 flex flex-col md:flex-row">
    <!-- Sidebar / Nav -->
    <nav class="w-full md:w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 shrink-0 h-full overflow-y-auto">
      <div class="p-6 flex items-center gap-3 sticky top-0 bg-white dark:bg-gray-800 z-10">
        <div class="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center text-white font-bold">A</div>
        <h1 class="text-xl font-bold text-gray-900 dark:text-white">AI Proxy</h1>
      </div>

      <div class="px-4 py-2 space-y-1">
        <router-link v-for="item in navItems" :key="item.path" :to="item.path"
          class="flex items-center gap-3 px-4 py-3 text-sm font-medium rounded-lg transition-colors" :class="[
            $route.path === item.path
              ? 'bg-blue-50 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400'
              : 'text-gray-600 dark:text-gray-400 hover:bg-gray-100 dark:hover:bg-gray-700/50'
          ]">
          <component :is="item.icon" class="w-5 h-5" />
          {{ item.name }}
        </router-link>
      </div>
    </nav>

    <!-- Main Content -->
    <main class="flex-1 h-full overflow-hidden flex flex-col">
      <header
        class="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 flex items-center justify-between shrink-0">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">{{ currentRouteName }}</h2>
        <div class="flex items-center gap-4">
          <button @click="ui.toggleTheme" class="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
            <component :is="ui.isDark ? Sun : Moon" class="w-5 h-5" />
          </button>
        </div>
      </header>

      <div class="flex-1 overflow-y-auto p-6">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" class="h-full" />
          </transition>
        </router-view>
      </div>
    </main>
    <GlobalUI />
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { useUIStore } from '@/stores/ui'
import GlobalUI from './GlobalUI.vue'
import {
  LayoutDashboard,
  BarChart3,
  ListTodo,
  ShieldCheck,
  Terminal,
  Sun,
  Moon,
  Hash
} from 'lucide-vue-next'

const route = useRoute()
const ui = useUIStore()

const navItems = [
  { name: '仪表盘', path: '/', icon: LayoutDashboard },
  { name: '分析报告', path: '/analytics', icon: BarChart3 },
  { name: '请求日志', path: '/logs', icon: ListTodo },
  { name: '提供商配置', path: '/providers', icon: ShieldCheck },
  { name: '模型映射', path: '/mappings', icon: Hash },
  { name: '演练场', path: '/playground', icon: Terminal },
]

const currentRouteName = computed(() => {
  return navItems.find(item => item.path === route.path)?.name || ''
})

onMounted(() => {
  ui.initTheme()
})
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
