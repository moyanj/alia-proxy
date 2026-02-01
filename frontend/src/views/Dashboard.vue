<template>
  <div class="space-y-8 animate-in fade-in slide-in-from-bottom-4 duration-500">
    <!-- Hero Status Card -->
    <section class="win-card p-8 flex flex-col md:flex-row items-center gap-8 bg-gradient-to-br from-blue-600/5 to-purple-600/5 border-blue-500/10 relative overflow-hidden">
      <div class="absolute top-0 right-0 w-64 h-64 bg-blue-500/10 rounded-full blur-3xl -translate-y-1/2 translate-x-1/3"></div>
      <div class="absolute bottom-0 left-0 w-48 h-48 bg-purple-500/10 rounded-full blur-3xl translate-y-1/3 -translate-x-1/4"></div>
      
      <div class="w-20 h-20 rounded-2xl bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white shadow-xl shadow-blue-500/30 shrink-0 relative z-10">
        <Activity class="w-10 h-10" />
      </div>
      <div class="flex-1 text-center md:text-left relative z-10">
        <h3 class="text-2xl font-bold text-gray-900 dark:text-white mb-1">系统运行状态良好</h3>
        <p class="text-sm text-gray-500 dark:text-gray-400 mb-4">
          已连接 {{ Object.keys(stats?.providers_config || {}).length }} 个提供商，当前模型映射配置正常。
        </p>
        <div class="flex flex-wrap justify-center md:justify-start gap-3">
          <button @click="refreshAll" class="win-btn-primary flex items-center gap-2">
            <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': loading }" />
            刷新状态
          </button>
          <router-link to="/logs" class="px-4 py-1.5 rounded bg-black/5 dark:bg-white/5 border border-black/10 dark:border-white/10 text-sm font-medium hover:bg-black/10 transition-colors">
            查看日志
          </router-link>
        </div>
      </div>
      
      <div class="grid grid-cols-2 gap-4 shrink-0 relative z-10">
        <div class="px-6 py-4 rounded-xl bg-gradient-to-br from-blue-500/10 to-blue-600/5 border border-blue-500/20 text-center backdrop-blur-sm">
          <p class="text-[10px] font-bold text-blue-500/70 uppercase tracking-widest mb-1">总请求数</p>
          <p class="text-2xl font-black text-blue-600 dark:text-blue-400">{{ formatNumber(stats?.total_requests || 0) }}</p>
          <p class="text-[10px] text-gray-400 mt-1">今日 +{{ todayRequests }}</p>
        </div>
        <div class="px-6 py-4 rounded-xl bg-gradient-to-br from-purple-500/10 to-purple-600/5 border border-purple-500/20 text-center backdrop-blur-sm">
          <p class="text-[10px] font-bold text-purple-500/70 uppercase tracking-widest mb-1">活跃模型</p>
          <p class="text-2xl font-black text-purple-600 dark:text-purple-400">{{ Object.keys(stats?.model_counts || {}).length }}</p>
          <p class="text-[10px] text-gray-400 mt-1">共 {{ totalModels }} 个模型</p>
        </div>
      </div>
    </section>

    <!-- Real-time Metrics Grid -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <!-- Success Rate -->
      <div class="win-card p-5 flex items-center gap-4 group hover:scale-[1.02] transition-transform duration-300">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-green-500/20 to-green-600/10 flex items-center justify-center text-green-600 group-hover:scale-110 transition-transform">
          <CheckCircle2 class="w-6 h-6" />
        </div>
        <div>
          <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-0.5">成功率</p>
          <div class="flex items-baseline gap-2">
            <p class="text-xl font-black text-gray-900 dark:text-white">{{ successRate }}%</p>
            <TrendIndicator :value="successRateTrend" />
          </div>
        </div>
        <div class="ml-auto">
          <MiniChart :data="successRateHistory" color="#10b981" />
        </div>
      </div>

      <!-- Avg Latency -->
      <div class="win-card p-5 flex items-center gap-4 group hover:scale-[1.02] transition-transform duration-300">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-orange-500/20 to-orange-600/10 flex items-center justify-center text-orange-600 group-hover:scale-110 transition-transform">
          <Zap class="w-6 h-6" />
        </div>
        <div>
          <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-0.5">平均延迟</p>
          <div class="flex items-baseline gap-2">
            <p class="text-xl font-black text-gray-900 dark:text-white">{{ avgLatency }}s</p>
            <TrendIndicator :value="latencyTrend" inverse />
          </div>
        </div>
        <div class="ml-auto">
          <MiniChart :data="latencyHistory" color="#f59e0b" />
        </div>
      </div>

      <!-- RPM -->
      <div class="win-card p-5 flex items-center gap-4 group hover:scale-[1.02] transition-transform duration-300">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500/20 to-blue-600/10 flex items-center justify-center text-blue-600 group-hover:scale-110 transition-transform">
          <Gauge class="w-6 h-6" />
        </div>
        <div>
          <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-0.5">当前 RPM</p>
          <div class="flex items-baseline gap-2">
            <p class="text-xl font-black text-gray-900 dark:text-white">{{ currentRPM }}</p>
            <span class="text-[10px] text-gray-400">req/min</span>
          </div>
        </div>
        <div class="ml-auto">
          <div class="w-10 h-10 rounded-full border-2 border-blue-500/30 flex items-center justify-center">
            <span class="text-[10px] font-bold text-blue-500">{{ rpmPercentage }}%</span>
          </div>
        </div>
      </div>

      <!-- TPM -->
      <div class="win-card p-5 flex items-center gap-4 group hover:scale-[1.02] transition-transform duration-300">
        <div class="w-12 h-12 rounded-xl bg-gradient-to-br from-purple-500/20 to-purple-600/10 flex items-center justify-center text-purple-600 group-hover:scale-110 transition-transform">
          <BarChart3 class="w-6 h-6" />
        </div>
        <div>
          <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-0.5">当前 TPM</p>
          <div class="flex items-baseline gap-2">
            <p class="text-xl font-black text-gray-900 dark:text-white">{{ formatTokens(currentTPM) }}</p>
          </div>
        </div>
        <div class="ml-auto">
          <div class="w-10 h-10 rounded-full border-2 border-purple-500/30 flex items-center justify-center">
            <span class="text-[10px] font-bold text-purple-500">{{ tpmPercentage }}%</span>
          </div>
        </div>
      </div>
    </div>

    <!-- Detailed Stats Grid -->
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6">
      <!-- Providers List -->
      <section class="lg:col-span-2 space-y-4">
        <div class="flex items-center justify-between px-1">
          <h4 class="text-sm font-bold text-gray-500 uppercase tracking-widest flex items-center gap-2">
            <Server class="w-4 h-4" /> 提供商状态
          </h4>
          <div class="flex items-center gap-2">
            <span class="text-[10px] text-gray-400">{{ healthyProviders }}/{{ totalProviders }} 正常</span>
            <div class="w-16 h-1.5 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
              <div class="h-full bg-green-500 rounded-full transition-all duration-500" :style="{ width: `${(healthyProviders / Math.max(totalProviders, 1)) * 100}%` }"></div>
            </div>
          </div>
        </div>
        <div v-if="providerList.length > 0" class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div 
            v-for="provider in providerList" 
            :key="provider.name" 
            class="win-card p-4 flex items-center justify-between group cursor-pointer hover:border-blue-500/30 transition-all"
          >
            <div class="flex items-center gap-4">
              <div class="w-10 h-10 rounded-lg bg-gradient-to-br from-gray-100 to-gray-50 dark:from-white/10 dark:to-white/5 flex items-center justify-center transition-all"
                :class="provider.status === 'healthy' ? 'text-green-600' : 'text-red-600'">
                <ShieldCheck v-if="provider.status === 'healthy'" class="w-5 h-5" />
                <AlertCircle v-else class="w-5 h-5" />
              </div>
              <div>
                <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ provider.name }}</p>
                <p class="text-[10px] text-gray-500">{{ provider.type }} · {{ provider.requests }} 请求</p>
              </div>
            </div>
            <div class="flex items-center gap-2">
              <div class="text-right mr-2">
                <p class="text-[10px] font-medium" :class="provider.success_rate >= 95 ? 'text-green-600' : 'text-yellow-600'">{{ provider.success_rate.toFixed(1) }}%</p>
                <p class="text-[9px] text-gray-400">{{ provider.avg_latency.toFixed(2) }}s</p>
              </div>
              <div class="w-2 h-2 rounded-full" :class="provider.status === 'healthy' ? 'bg-green-500 shadow-lg shadow-green-500/50' : 'bg-red-500 shadow-lg shadow-red-500/50'"></div>
            </div>
          </div>
        </div>
        <div v-else class="sm:col-span-2 py-12 win-card flex flex-col items-center justify-center text-gray-400 border-dashed">
             <Inbox class="w-8 h-8 mb-2 opacity-20" />
             <p class="text-xs font-medium uppercase tracking-widest">未配置提供商</p>
          </div>
      </section>

      <!-- Token Usage Rank -->
      <section class="space-y-4">
        <h4 class="text-sm font-bold text-gray-500 uppercase tracking-widest px-1 flex items-center gap-2">
          <Cpu class="w-4 h-4" /> Token 消耗排行
        </h4>
        <div class="win-card divide-y divide-black/5 dark:divide-white/5 overflow-hidden">
          <div v-for="(item, index) in stats?.top_models_by_tokens" :key="item.model" class="p-4 hover:bg-black/[0.02] dark:hover:bg-white/[0.02] transition-colors group">
            <div class="flex justify-between items-center mb-2">
              <div class="flex items-center gap-2">
                <span class="text-xs font-bold w-5 h-5 rounded-full flex items-center justify-center"
                  :class="index < 3 ? 'bg-gradient-to-br from-yellow-400 to-orange-500 text-white' : 'text-gray-400 bg-gray-100 dark:bg-white/5'">{{ index + 1 }}</span>
                <span class="text-[13px] font-semibold text-gray-900 dark:text-white truncate max-w-[120px]" :title="item.model">{{ item.model }}</span>
              </div>
              <span class="text-[11px] font-mono font-bold text-blue-600 dark:text-blue-400">{{ formatTokens(item.total_tokens) }}</span>
            </div>
            <div class="w-full bg-black/5 dark:bg-white/5 rounded-full h-1.5 overflow-hidden">
               <div 
                 class="h-full rounded-full transition-all duration-1000 bg-gradient-to-r from-blue-500 to-blue-600"
                 :style="{ width: `${(item.total_tokens / (stats?.top_models_by_tokens[0]?.total_tokens || 1)) * 100}%` }"
               ></div>
            </div>
          </div>
          <div v-if="!stats?.top_models_by_tokens || stats?.top_models_by_tokens.length === 0" class="p-12 text-center text-gray-400">
            暂无排行数据
          </div>
        </div>
      </section>
    </div>

    <!-- Usage Trends -->
    <section class="space-y-4">
       <div class="flex items-center justify-between px-1">
         <h4 class="text-sm font-bold text-gray-500 uppercase tracking-widest flex items-center gap-2">
           <LayoutDashboard class="w-4 h-4" /> 模型负载分布
         </h4>
         <div class="flex items-center gap-2">
           <button @click="viewMode = 'grid'" class="p-1.5 rounded" :class="viewMode === 'grid' ? 'bg-blue-500/10 text-blue-600' : 'text-gray-400 hover:text-gray-600'">
             <LayoutGrid class="w-4 h-4" />
           </button>
           <button @click="viewMode = 'list'" class="p-1.5 rounded" :class="viewMode === 'list' ? 'bg-blue-500/10 text-blue-600' : 'text-gray-400 hover:text-gray-600'">
             <List class="w-4 h-4" />
           </button>
         </div>
       </div>
       
       <!-- Grid View -->
       <div v-if="viewMode === 'grid'" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
          <div v-for="(count, model) in stats?.model_counts" :key="model" class="win-card p-4 relative overflow-hidden group cursor-pointer hover:border-blue-500/30 transition-all">
             <div class="absolute -right-4 -bottom-4 opacity-[0.03] group-hover:scale-110 transition-transform duration-500">
                <Box class="w-20 h-20" />
             </div>
             <div class="flex items-center justify-between mb-3">
                <span class="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider"
                  :class="getProviderColor(model.split('/')[0] || '')">
                  {{ model.split('/')[0] }}
                </span>
                <MoreHorizontal class="w-4 h-4 text-gray-300 opacity-0 group-hover:opacity-100 transition-opacity" />
             </div>
             <h5 class="text-sm font-bold text-gray-900 dark:text-white mb-3 truncate" :title="model">{{ model.split('/')[1] || model }}</h5>
             <div class="flex items-end justify-between">
                <div>
                   <span class="text-2xl font-black text-gray-900 dark:text-white">{{ count }}</span>
                   <span class="text-[10px] text-gray-500 ml-1">Requests</span>
                </div>
                <div class="w-16 h-8 flex items-end gap-0.5">
                   <div v-for="i in 7" :key="i" 
                     :style="{ height: `${getRandomHeight(model, i)}%` }" 
                     class="flex-1 rounded-t-sm transition-all duration-500"
                     :class="getBarColor(i)"></div>
                </div>
             </div>
          </div>
       </div>

       <!-- List View -->
       <div v-else class="win-card overflow-hidden">
         <table class="w-full">
           <thead class="bg-black/[0.02] dark:bg-white/[0.02]">
             <tr>
               <th class="text-left p-4 text-[10px] font-bold text-gray-500 uppercase tracking-widest">模型</th>
               <th class="text-left p-4 text-[10px] font-bold text-gray-500 uppercase tracking-widest">提供商</th>
               <th class="text-right p-4 text-[10px] font-bold text-gray-500 uppercase tracking-widest">请求数</th>
               <th class="text-right p-4 text-[10px] font-bold text-gray-500 uppercase tracking-widest">占比</th>
               <th class="p-4 text-[10px] font-bold text-gray-500 uppercase tracking-widest w-32">趋势</th>
             </tr>
           </thead>
           <tbody class="divide-y divide-black/5 dark:divide-white/5">
             <tr v-for="(count, model) in sortedModels" :key="model" class="hover:bg-black/[0.01] dark:hover:bg-white/[0.01] transition-colors">
               <td class="p-4">
                 <div class="flex items-center gap-2">
                   <span class="text-sm font-semibold text-gray-900 dark:text-white">{{ model.split('/')[1] || model }}</span>
                 </div>
               </td>
               <td class="p-4">
                 <span class="px-2 py-0.5 rounded-full text-[9px] font-bold uppercase tracking-wider"
                   :class="getProviderColor(model.split('/')[0] || '')">
                   {{ model.split('/')[0] }}
                 </span>
               </td>
               <td class="p-4 text-right">
                 <span class="text-sm font-bold text-gray-900 dark:text-white">{{ count }}</span>
               </td>
               <td class="p-4 text-right">
                 <span class="text-sm text-gray-600 dark:text-gray-400">{{ ((count / totalRequests) * 100).toFixed(1) }}%</span>
               </td>
               <td class="p-4">
                 <div class="w-full h-8 flex items-end gap-0.5">
                   <div v-for="i in 7" :key="i" 
                     :style="{ height: `${getRandomHeight(model, i)}%` }" 
                     class="flex-1 rounded-t-sm"
                     :class="getBarColor(i)"></div>
                 </div>
               </td>
             </tr>
           </tbody>
         </table>
       </div>
    </section>

    <!-- Quick Analytics Preview -->
    <section class="space-y-4">
      <h4 class="text-sm font-bold text-gray-500 uppercase tracking-widest px-1 flex items-center gap-2">
        <TrendingUp class="w-4 h-4" /> 最近活动概览
      </h4>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="win-card p-5">
          <div class="flex items-center justify-between mb-4">
            <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">24小时请求趋势</p>
            <router-link to="/analytics" class="text-[10px] text-blue-500 hover:text-blue-600">查看详情 →</router-link>
          </div>
          <div class="h-48">
            <v-chart class="w-full h-full" :option="hourlyTrendOption" autoresize />
          </div>
        </div>
        <div class="win-card p-5">
          <div class="flex items-center justify-between mb-4">
            <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">提供商分布</p>
            <router-link to="/analytics" class="text-[10px] text-blue-500 hover:text-blue-600">查看详情 →</router-link>
          </div>
          <div class="h-48">
            <v-chart class="w-full h-full" :option="providerDistributionOption" autoresize />
          </div>
        </div>
      </div>
    </section>
  </div>
</template>

<script setup lang="ts">
import { defineAsyncComponent, ref, onMounted, computed, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DatasetComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import {
  Activity,
  Cpu,
  Server,
  ShieldCheck,
  AlertCircle,
  RefreshCw,
  LayoutDashboard,
  BarChart3,
  Box,
  Inbox,
  CheckCircle2,
  Zap,
  Gauge,
  LayoutGrid,
  List,
  MoreHorizontal,
  TrendingUp
} from 'lucide-vue-next'
import { useUIStore } from '@/stores/ui'
import {
  getStats,
  getHealth,
  getAnalytics,
  type Stats,
  type Analytics
} from '@/api'
import TrendIndicator from '@/components/TrendIndicator.vue'
import MiniChart from '@/components/MiniChart.vue'

use([
  CanvasRenderer,
  LineChart,
  PieChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  DatasetComponent
])

const ui = useUIStore()
const stats = ref<Stats | null>(null)
const health = ref<any>(null)
const analytics = ref<Analytics | null>(null)
const loading = ref(false)
const viewMode = ref<'grid' | 'list'>('grid')

// --- 将被替换的模拟数据 ---
// const currentRPM = ref(42)
// const currentTPM = ref(12580)
// const rpmPercentage = ref(35)
// const tpmPercentage = ref(42)
// const successRate = ref(98.5)
// const successRateTrend = ref(2.3)
// const avgLatency = ref(0.85)
// const latencyTrend = ref(-0.15)
// const todayRequests = ref(1234)
// const successRateHistory = ref([95, 96, 97, 96, 98, 98.5, 98.5])
// const latencyHistory = ref([1.2, 1.1, 0.95, 0.9, 0.88, 0.85, 0.85])
// ---

const todayRequests = computed(() => {
  if (!analytics.value?.overall_trends) return 0
  const today = new Date().toISOString().split('T')[0]
  const todayData = analytics.value.overall_trends.find(d => d.date === today)
  return todayData?.total || 0
})

const successRate = computed(() => analytics.value?.summary.success_rate.toFixed(1) || '0.0')
const avgLatency = computed(() => analytics.value?.summary?.avg_latency?.toFixed(2) || '0.00')

const currentRPM = computed(() => {
  const usage = analytics.value?.minute_usage
  if (!usage?.length) return 0
  return usage[usage.length - 1]?.rpm ?? 0
})

const currentTPM = computed(() => {
  const usage = analytics.value?.minute_usage
  if (!usage?.length) return 0
  return usage[usage.length - 1]?.tpm ?? 0
})

const rpmPercentage = ref(0)
const tpmPercentage = ref(0)
const successRateTrend = ref(0)
const latencyTrend = ref(0)
const successRateHistory = ref<number[]>([])
const latencyHistory = ref<number[]>([])

watch(analytics, (newData) => {
  if (!newData?.overall_trends) return
  const trends = newData.overall_trends
  if (trends.length >= 2) {
    const last = trends[trends.length - 1]
    const secondLast = trends[trends.length - 2]
    if (last && secondLast && last.total > 0 && secondLast.total > 0) {
      const lastRate = (last.success / last.total) * 100
      const secondLastRate = (secondLast.success / secondLast.total) * 100
      successRateTrend.value = lastRate - secondLastRate
    }
  }
  successRateHistory.value = trends.map(d => d.total > 0 ? (d.success / d.total) * 100 : 0)
  // latencyHistory is not available from backend yet
})


const totalModels = computed(() => stats.value ? Object.keys(stats.value.model_counts).length : 0)
const totalRequests = computed(() => stats.value?.total_requests || 0)
const totalProviders = computed(() => health.value ? Object.keys(health.value.providers).length : 0)
const healthyProviders = computed(() => health.value ? Object.values(health.value.providers).filter(s => s === 'healthy').length : 0)

const providerStats = computed(() => {
  if (!health.value?.providers || !stats.value?.providers_config || !analytics.value?.provider_trends) return {}

  const latestProviderData = new Map<string, any>()
  for (const trend of analytics.value.provider_trends) {
    latestProviderData.set(trend.provider, trend)
  }

  const result: Record<string, { status: string; type: string; requests: number; success_rate: number; avg_latency: number }> = {};
  for (const [name, status] of Object.entries(health.value.providers)) {
    const data = latestProviderData.get(name);
    result[name] = {
      status: status as string,
      type: stats.value?.providers_config[name]?.type || 'Unknown',
      requests: data?.total || 0,
      success_rate: data && data.total > 0 ? (data.success / data.total * 100) : 0,
      avg_latency: data?.avg_latency || 0
    };
  }
  return result;
})

const providerList = computed(() => {
  if (!providerStats.value) return []
  return Object.entries(providerStats.value).map(([name, data]) => {
    return {
      name,
      status: data?.status || 'unhealthy',
      type: data?.type || 'Unknown',
      requests: data?.requests || 0,
      success_rate: data?.success_rate || 0,
      avg_latency: data?.avg_latency || 0,
    }
  })
})

const sortedModels = computed(() => {
  if (!stats.value?.model_counts) return {}
  return Object.entries(stats.value.model_counts)
    .sort(([, a], [, b]) => b - a)
    .reduce((acc, [key, val]) => {
      acc[key] = val
      return acc
    }, {} as Record<string, number>)
})

const textColor = computed(() => ui.isDark ? '#a1a1aa' : '#71717a')
const axisColor = computed(() => ui.isDark ? '#27272a' : '#f4f4f5')

const hourlyTrendOption = computed(() => {
  if (!analytics.value?.hourly_trends) return {}
  
  const hours = Array.from({ length: 24 }, (_, i) => i)
  const dataMap = new Map(analytics.value.hourly_trends.map(h => [parseInt(h.hour), h.count]))
  const data = hours.map(h => dataMap.get(h) || 0)

  return {
    tooltip: { trigger: 'axis', backgroundColor: ui.isDark ? '#18181b' : '#fff', borderColor: axisColor.value, textStyle: { color: ui.isDark ? '#fff' : '#000' } },
    grid: { top: 10, left: 10, right: 10, bottom: 20, containLabel: true },
    xAxis: {
      type: 'category',
      data: hours.map(h => `${h}:00`),
      axisLabel: { color: textColor.value, fontSize: 10 },
      axisLine: { lineStyle: { color: axisColor.value } }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: textColor.value, fontSize: 10 },
      splitLine: { lineStyle: { color: axisColor.value, type: 'dashed' } }
    },
    series: [{
      type: 'line',
      data: data,
      smooth: true,
      symbol: 'none',
      areaStyle: { color: '#3b82f6', opacity: 0.1 },
      lineStyle: { color: '#3b82f6', width: 2 }
    }]
  }
})

const providerDistributionOption = computed(() => {
  const colors = ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b', '#ef4444']
  const data = Object.entries(stats.value?.provider_counts || {}).map(([name, count], i) => ({
    name,
    value: count,
    itemStyle: { color: colors[i % colors.length] }
  }))
  
  return {
    tooltip: { trigger: 'item', backgroundColor: ui.isDark ? '#18181b' : '#fff', textStyle: { color: ui.isDark ? '#fff' : '#000' } },
    legend: { bottom: 0, textStyle: { color: textColor.value, fontSize: 10 } },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['50%', '45%'],
      avoidLabelOverlap: false,
      itemStyle: { borderRadius: 6, borderColor: ui.isDark ? '#18181b' : '#fff', borderWidth: 2 },
      label: { show: false },
      data
    }]
  }
})

async function fetchStats() {
  try {
    stats.value = await getStats()
  } catch (err) {
    console.error('Failed to fetch stats:', err)
  }
}

async function fetchHealth() {
  try {
    health.value = await getHealth()
  } catch (err) {
    console.error('Failed to fetch health:', err)
  }
}

async function fetchAnalytics() {
  try {
    analytics.value = await getAnalytics({ days: 1 })
  } catch (err) {
    console.error('Failed to fetch analytics:', err)
  }
}

async function refreshAll() {
  loading.value = true
  await Promise.all([fetchStats(), fetchHealth(), fetchAnalytics()])
  loading.value = false
}

function formatTokens(n: number) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return n.toString()
}

function formatNumber(n: number) {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return n.toString()
}

function getProviderColor(provider: string) {
  const colors: Record<string, string> = {
    openai: 'bg-green-500/10 text-green-600',
    anthropic: 'bg-purple-500/10 text-purple-600',
    ollama: 'bg-orange-500/10 text-orange-600',
    azure: 'bg-blue-500/10 text-blue-600'
  }
  return colors[provider.toLowerCase()] || 'bg-gray-500/10 text-gray-600'
}

function getRandomHeight(model: string, index: number) {
  // Generate consistent pseudo-random heights based on model name and index
  const seed = model.charCodeAt(0) + index
  return 20 + (seed % 80)
}

function getBarColor(index: number) {
  const colors = ['bg-blue-500', 'bg-blue-400', 'bg-blue-300', 'bg-blue-400', 'bg-blue-500', 'bg-blue-600', 'bg-blue-500']
  return colors[index % colors.length]
}

onMounted(() => {
  refreshAll()
})
</script>
