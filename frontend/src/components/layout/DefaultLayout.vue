<template>
  <div class="h-screen overflow-hidden flex flex-col md:flex-row bg-[#f3f3f3] dark:bg-[#202020]">
    <!-- WinUI 3 Navigation View -->
    <aside 
      class="w-full md:w-72 flex flex-col shrink-0 z-50 transition-all duration-300 ease-in-out border-r border-black/5 dark:border-white/5 bg-transparent"
    >
      <!-- Brand / App Info -->
      <div class="p-4 flex items-center gap-3">
        <div class="w-10 h-10 rounded-lg bg-blue-600 flex items-center justify-center text-white shadow-lg shadow-blue-500/20">
          <Box class="w-6 h-6" />
        </div>
        <div class="flex flex-col">
          <span class="text-sm font-semibold text-gray-900 dark:text-white leading-tight">AI Proxy Service</span>
          <span class="text-[10px] text-gray-500 dark:text-gray-400 font-medium">v0.1.0-alpha</span>
        </div>
      </div>

      <!-- Navigation Items -->
      <nav class="flex-1 px-2 space-y-1 overflow-y-auto overflow-x-hidden custom-scrollbar">
        <div v-for="group in groupedNavItems" :key="group.title" class="mb-4">
          <h3 v-if="group.title" class="px-4 py-2 text-[11px] font-bold text-gray-500 dark:text-gray-400 uppercase tracking-widest">
            {{ group.title }}
          </h3>
          <router-link 
            v-for="item in group.items" 
            :key="item.path" 
            :to="item.path"
            class="group relative flex items-center gap-3 px-3 py-2 rounded-md transition-all duration-200"
            :class="[
              $route.path === item.path
                ? 'bg-black/[0.04] dark:bg-white/[0.04] text-gray-900 dark:text-white shadow-sm'
                : 'text-gray-600 dark:text-gray-400 hover:bg-black/[0.02] dark:hover:bg-white/[0.02]'
            ]"
          >
            <!-- Active Indicator Bar -->
            <div 
              class="absolute left-0 w-1 h-4 bg-blue-500 rounded-full transition-all duration-300"
              :class="[$route.path === item.path ? 'opacity-100 scale-y-100' : 'opacity-0 scale-y-0']"
            ></div>
            
            <component 
              :is="item.icon" 
              class="w-4.5 h-4.5 transition-transform group-active:scale-90"
              :class="[$route.path === item.path ? 'text-blue-600 dark:text-blue-400' : '']"
            />
            <span class="text-[13px] font-medium">{{ item.name }}</span>
          </router-link>
        </div>
      </nav>

      <!-- Bottom Actions -->
      <div class="p-3 border-t border-black/5 dark:border-white/5 space-y-1">
        <button 
          @click="ui.toggleTheme"
          class="w-full flex items-center gap-3 px-3 py-2 text-gray-600 dark:text-gray-400 hover:bg-black/[0.02] dark:hover:bg-white/[0.02] rounded-md transition-all text-[13px] font-medium"
        >
          <component :is="ui.isDark ? Sun : Moon" class="w-4.5 h-4.5" />
          <span>{{ ui.isDark ? '浅色模式' : '深色模式' }}</span>
        </button>
      </div>
    </aside>

    <!-- Main Content Area -->
    <main class="flex-1 flex flex-col relative bg-transparent overflow-hidden">
      <!-- Title Bar (Modern Windows style) -->
      <header class="h-14 flex items-center justify-between px-8 shrink-0 z-10">
        <div class="flex flex-col">
          <div class="flex items-center gap-2 text-xs text-gray-500 dark:text-gray-400 mb-0.5">
            <span>系统</span>
            <span class="text-gray-900 dark:text-white font-medium">{{ currentRouteName }}</span>
          </div>
          <h2 class="text-2xl font-bold text-gray-900 dark:text-white tracking-tight">{{ currentRouteName }}</h2>
        </div>
        
        <div class="flex items-center gap-3">
          <div class="flex items-center gap-2 px-3 py-1.5 bg-green-500/10 rounded-full">
            <div class="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span class="text-xs font-bold text-green-600 dark:text-green-400 uppercase tracking-tighter">API Online</span>
          </div>
        </div>
      </header>

      <!-- Scrollable Content -->
      <div class="flex-1 overflow-y-auto px-8 pb-12 pt-4">
        <div class="max-w-6xl mx-auto h-full">
          <router-view v-slot="{ Component }">
            <transition 
              enter-active-class="transition duration-300 ease-out"
              enter-from-class="opacity-0 translate-y-4"
              enter-to-class="opacity-100 translate-y-0"
              leave-active-class="transition duration-200 ease-in"
              leave-from-class="opacity-100"
              leave-to-class="opacity-0"
              mode="out-in"
            >
              <component :is="Component" />
            </transition>
          </router-view>
        </div>
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
  Hash,
  Box,
  Settings,
  HelpCircle,
  Activity
} from 'lucide-vue-next'

const route = useRoute()
const ui = useUIStore()

const groupedNavItems = [
  {
    title: '概览',
    items: [
      { name: '仪表盘', path: '/', icon: LayoutDashboard },
      { name: '分析报告', path: '/analytics', icon: BarChart3 },
      { name: '实时状态', path: '/health', icon: Activity },
    ]
  },
  {
    title: '日志',
    items: [
      { name: '请求日志', path: '/logs', icon: ListTodo },
    ]
  },
  {
    title: '配置',
    items: [
      { name: '提供商配置', path: '/providers', icon: ShieldCheck },
      { name: '模型映射', path: '/mappings', icon: Hash },
    ]
  },
  {
    title: '开发者',
    items: [
      { name: '演练场', path: '/playground', icon: Terminal },
    ]
  }
]

const allNavItems = computed(() => groupedNavItems.flatMap(g => g.items))

const currentRouteName = computed(() => {
  return allNavItems.value.find(item => item.path === route.path)?.name || ''
})

onMounted(() => {
  ui.initTheme()
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(0, 0, 0, 0.05);
  border-radius: 10px;
}
.dark .custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.05);
}
</style>
