<template>
  <div class="min-h-screen bg-gray-50 dark:bg-gray-900 flex flex-col md:flex-row">
    <!-- Sidebar / Nav -->
    <nav class="w-full md:w-64 bg-white dark:bg-gray-800 border-r border-gray-200 dark:border-gray-700 flex-shrink-0">
      <div class="p-6 flex items-center gap-3">
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
    <main class="flex-1 overflow-auto">
      <header
        class="h-16 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 px-6 flex items-center justify-between sticky top-0 z-10">
        <h2 class="text-lg font-semibold text-gray-900 dark:text-white">{{ currentRouteName }}</h2>
        <div class="flex items-center gap-4">
          <button @click="toggleDarkMode" class="p-2 text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg">
            <component :is="isDark ? Sun : Moon" class="w-5 h-5" />
          </button>
        </div>
      </header>

      <div class="p-6">
        <router-view v-slot="{ Component }">
          <transition name="fade" mode="out-in">
            <component :is="Component" />
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
import GlobalUI from './GlobalUI.vue'
import { 

  LayoutDashboard,
  ListTodo,
  ShieldCheck,
  Terminal,
  Sun,
  Moon
} from 'lucide-vue-next'

const route = useRoute()
const isDark = ref(false)

const navItems = [
  { name: '仪表盘', path: '/', icon: LayoutDashboard },
  { name: '请求日志', path: '/logs', icon: ListTodo },
  { name: '提供商配置', path: '/providers', icon: ShieldCheck },
  { name: '演练场', path: '/playground', icon: Terminal },
]

const currentRouteName = computed(() => {
  return navItems.find(item => item.path === route.path)?.name || ''
})

function toggleDarkMode() {
  isDark.value = !isDark.value
  if (isDark.value) {
    document.documentElement.classList.add('dark')
    localStorage.theme = 'dark'
  } else {
    document.documentElement.classList.remove('dark')
    localStorage.theme = 'light'
  }
}

onMounted(() => {
  if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
    isDark.value = true
    document.documentElement.classList.add('dark')
  } else {
    isDark.value = false
    document.documentElement.classList.remove('dark')
  }
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
