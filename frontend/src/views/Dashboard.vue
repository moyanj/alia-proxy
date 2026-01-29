<template>
  <div class="space-y-6">
    <!-- Stat Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <div v-for="stat in summaryStats" :key="stat.label" class="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
        <div class="flex items-center justify-between mb-4">
          <div class="p-2 bg-blue-50 dark:bg-blue-900/30 rounded-lg text-blue-600 dark:text-blue-400">
            <component :is="stat.icon" class="w-6 h-6" />
          </div>
        </div>
        <p class="text-sm text-gray-500 dark:text-gray-400 font-medium">{{ stat.label }}</p>
        <h3 class="text-2xl font-bold text-gray-900 dark:text-white mt-1">{{ stat.value }}</h3>
      </div>
    </div>

    <!-- Charts / Details -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Provider Distribution -->
      <div class="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
        <h4 class="text-base font-semibold text-gray-900 dark:text-white mb-6">提供商分布</h4>
        <div class="space-y-4">
          <div v-for="(count, provider) in stats?.provider_counts" :key="provider" class="space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-gray-700 dark:text-gray-300 font-medium">{{ provider }}</span>
              <span class="text-gray-500">{{ count }} 次请求</span>
            </div>
            <div class="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2">
              <div 
                class="bg-blue-600 h-2 rounded-full transition-all duration-500" 
                :style="{ width: `${(count / (stats?.total_requests || 1)) * 100}%` }"
              ></div>
            </div>
          </div>
          <div v-if="!stats?.provider_counts || Object.keys(stats.provider_counts).length === 0" class="text-center py-8 text-gray-400">
            暂无数据
          </div>
        </div>
      </div>

      <!-- Model Distribution -->
      <div class="bg-white dark:bg-gray-800 p-6 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm">
        <h4 class="text-base font-semibold text-gray-900 dark:text-white mb-6">模型分布</h4>
        <div class="space-y-4">
          <div v-for="(count, model) in stats?.model_counts" :key="model" class="space-y-2">
            <div class="flex justify-between text-sm">
              <span class="text-gray-700 dark:text-gray-300 font-medium">{{ model }}</span>
              <span class="text-gray-500">{{ count }} 次请求</span>
            </div>
            <div class="w-full bg-gray-100 dark:bg-gray-700 rounded-full h-2">
              <div 
                class="bg-purple-600 h-2 rounded-full transition-all duration-500" 
                :style="{ width: `${(count / (stats?.total_requests || 1)) * 100}%` }"
              ></div>
            </div>
          </div>
          <div v-if="!stats?.model_counts || Object.keys(stats.model_counts).length === 0" class="text-center py-8 text-gray-400">
            暂无数据
          </div>
        </div>
      </div>
    </div>

    <!-- Daily Trends -->
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h4 class="text-base font-semibold text-gray-900 dark:text-white">用量趋势 (最近7天)</h4>
      </div>
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50 dark:bg-gray-900/50 text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">
              <th class="px-6 py-4 font-semibold">日期</th>
              <th class="px-6 py-4 font-semibold">模型</th>
              <th class="px-6 py-4 font-semibold">请求数</th>
              <th class="px-6 py-4 font-semibold">输入 Tokens</th>
              <th class="px-6 py-4 font-semibold">输出 Tokens</th>
              <th class="px-6 py-4 font-semibold">总计</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700 text-sm">
            <tr v-for="trend in analytics?.daily_trends" :key="`${trend.date}-${trend.model}`" class="hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors">
              <td class="px-6 py-4 text-gray-700 dark:text-gray-300">{{ trend.date }}</td>
              <td class="px-6 py-4 font-medium text-gray-900 dark:text-white">{{ trend.model }}</td>
              <td class="px-6 py-4 text-gray-600 dark:text-gray-400">{{ trend.request_count }}</td>
              <td class="px-6 py-4 text-gray-600 dark:text-gray-400">{{ trend.input_tokens }}</td>
              <td class="px-6 py-4 text-gray-600 dark:text-gray-400">{{ trend.output_tokens }}</td>
              <td class="px-6 py-4 font-semibold text-blue-600 dark:text-blue-400">{{ trend.total_tokens }}</td>
            </tr>
            <tr v-if="!analytics?.daily_trends || analytics.daily_trends.length === 0" class="text-center">
              <td colspan="6" class="py-12 text-gray-400">暂无趋势数据</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- Health Check Status -->
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
        <h4 class="text-base font-semibold text-gray-900 dark:text-white">系统健康状态</h4>
        <button @click="fetchHealth" :disabled="loadingHealth" class="text-sm text-blue-600 dark:text-blue-400 hover:underline disabled:opacity-50">
          {{ loadingHealth ? '检查中...' : '立即刷新' }}
        </button>
      </div>
      <div class="divide-y divide-gray-200 dark:divide-gray-700">
        <div v-for="(status, name) in health?.providers" :key="name" class="p-4 flex items-center justify-between">
          <div class="flex items-center gap-3">
            <div class="w-2 h-2 rounded-full" :class="status === 'healthy' ? 'bg-green-500' : 'bg-red-500'"></div>
            <span class="text-sm font-medium text-gray-700 dark:text-gray-300">{{ name }}</span>
          </div>
          <span class="text-xs px-2 py-1 rounded-full font-medium" 
            :class="status === 'healthy' ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400' : 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'">
            {{ status === 'healthy' ? '正常' : '异常' }}
          </span>
        </div>
        <div v-if="!health?.providers || Object.keys(health.providers).length === 0" class="p-8 text-center text-gray-400">
          未检测到提供商配置
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { useUIStore } from '@/stores/ui'
import { 
  getStats, 
  getHealth, 
  getAnalytics,
  type Stats,
  type Analytics
} from '@/api'
import { 
  Activity, 
  Cpu, 
  Server, 
  Clock,
  Zap
} from 'lucide-vue-next'

const ui = useUIStore()
const stats = ref<Stats | null>(null)
const analytics = ref<Analytics | null>(null)
const health = ref<any>(null)
const loadingHealth = ref(false)

const summaryStats = computed(() => [
  { label: '总请求数', value: analytics.value?.summary.total_requests || stats.value?.total_requests || 0, icon: Activity },
  { label: '平均成功率', value: (analytics.value?.summary.success_rate.toFixed(1) || '0.0') + '%', icon: Zap },
  { label: '平均响应耗时', value: (analytics.value?.summary.avg_latency.toFixed(2) || '0.00') + 's', icon: Clock },
  { label: '活跃模型数', value: Object.keys(stats.value?.model_counts || {}).length, icon: Cpu },
])

async function fetchStats() {
  try {
    stats.value = await getStats()
  } catch (err) {
    console.error('Failed to fetch stats:', err)
  }
}

async function fetchAnalytics() {
  try {
    analytics.value = await getAnalytics({ days: 7 })
  } catch (err) {
    console.error('Failed to fetch analytics:', err)
  }
}

async function fetchHealth() {
  loadingHealth.value = true
  try {
    health.value = await getHealth()
  } catch (err) {
    console.error('Failed to fetch health:', err)
  } finally {
    loadingHealth.value = false
  }
}

onMounted(() => {
  fetchStats()
  fetchAnalytics()
  fetchHealth()
})
</script>
