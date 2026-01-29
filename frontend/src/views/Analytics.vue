<template>
  <div class="space-y-6">
    <!-- Header Controls -->
    <div class="flex justify-between items-center">
      <h2 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
        <LayoutDashboard class="w-6 h-6 text-blue-500" /> 概览
      </h2>
      <div class="flex gap-2">
        <select v-model="days" @change="fetchAnalytics"
          class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-1.5 text-sm outline-none focus:ring-2 focus:ring-blue-500">
          <option :value="7">最近 7 天</option>
          <option :value="14">最近 14 天</option>
          <option :value="30">最近 30 天</option>
          <option :value="90">最近 90 天</option>
        </select>
        <button @click="refreshAll"
          class="p-1.5 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">
          <RefreshCw class="w-5 h-5" :class="{ 'animate-spin': refreshing }" />
        </button>
      </div>
    </div>

    <!-- Overview Charts -->
    <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
        <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">API 请求总数</h3>
        <v-chart class="h-64" :option="requestTrendOption" autoresize />
      </div>
      <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
        <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">API 错误总数</h3>
        <v-chart class="h-64" :option="errorTrendOption" autoresize />
      </div>
    </div>

    <!-- Model Usage Charts -->
    <div class="space-y-4">
      <div class="flex justify-between items-center">
        <h2 class="text-lg font-bold text-gray-900 dark:text-white flex items-center gap-2">
          生成内容和
        </h2>
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-500">模型</span>
          <select v-model="selectedModel"
            class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-1 text-sm outline-none">
            <option value="all">所有模型</option>
            <option v-for="m in availableModels" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>
      </div>
      <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">每个模型的输入 token 数</h3>
          <v-chart class="h-64" :option="tokenUsageOption" autoresize />
        </div>
        <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">每个模型的请求数</h3>
          <v-chart class="h-64" :option="modelRequestOption" autoresize />
        </div>
      </div>
    </div>

    <!-- Rate Limit Peaks -->
    <div class="space-y-4">
      <div class="flex justify-between items-center">
        <h2 class="text-lg font-bold text-gray-900 dark:text-white">速率限制细分</h2>
        <div class="flex items-center gap-2">
          <span class="text-sm text-gray-500">模型</span>
          <select v-model="peakModel"
            class="bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-1 text-sm outline-none">
            <option v-for="m in availableModels" :key="m" :value="m">{{ m }}</option>
          </select>
        </div>
      </div>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">每分钟请求数峰值 (RPM)</h3>
          <v-chart class="h-48" :option="rpmPeakOption" autoresize />
        </div>
        <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">每分钟输入 token 数峰值 (TPM)</h3>
          <v-chart class="h-48" :option="tpmPeakOption" autoresize />
        </div>
        <div class="bg-white dark:bg-gray-800 p-6 rounded-2xl border border-gray-200 dark:border-gray-700 shadow-sm">
          <h3 class="text-sm font-bold text-gray-500 uppercase tracking-wider mb-4">每日请求数峰值 (RPD)</h3>
          <v-chart class="h-48" :option="rpdPeakOption" autoresize />
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart } from 'echarts/charts'
import {
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  DatasetComponent,
  MarkLineComponent,
  MarkAreaComponent
} from 'echarts/components'
import VChart from 'vue-echarts'
import { LayoutDashboard, RefreshCw, Info } from 'lucide-vue-next'
import { getAnalytics, type Analytics } from '@/api'

import { useUIStore } from '@/stores/ui'

// Register ECharts components
use([
  CanvasRenderer,
  BarChart,
  LineChart,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  TitleComponent,
  DatasetComponent,
  MarkLineComponent,
  MarkAreaComponent
])

const ui = useUIStore()
const analytics = ref<Analytics | null>(null)
const days = ref(7)
const refreshing = ref(false)
const selectedModel = ref('all')
const peakModel = ref('')

const availableModels = computed(() => {
  if (!analytics.value) return []
  const models = new Set(analytics.value.model_trends.map(t => t.model))
  return Array.from(models)
})

async function fetchAnalytics() {
  refreshing.value = true
  try {
    analytics.value = await getAnalytics({ days: days.value })
    if (availableModels.value.length > 0 && !peakModel.value) {
      peakModel.value = availableModels.value[0] || ''
    }
  } catch (err) {
    console.error('Failed to fetch analytics:', err)
  } finally {
    refreshing.value = false
  }
}

function refreshAll() {
  fetchAnalytics()
}

// Common chart styles based on theme
const textColor = computed(() => ui.isDark ? '#e5e7eb' : '#374151') // gray-200 : gray-700
const axisColor = computed(() => ui.isDark ? '#4b5563' : '#e5e7eb') // gray-600 : gray-200

// Chart Options
const requestTrendOption = computed(() => {
  if (!analytics.value) return {}
  const data = analytics.value.overall_trends
  return {
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, data: ['请求数', '成功率'], textStyle: { color: textColor.value } },
    grid: { top: 20, left: 40, right: 40, bottom: 40 },
    xAxis: { 
      type: 'category', 
      data: data.map(d => d.date),
      axisLabel: { color: textColor.value },
      axisLine: { lineStyle: { color: axisColor.value } }
    },
    yAxis: [
      { 
        type: 'value', 
        name: '请求数',
        nameTextStyle: { color: textColor.value },
        axisLabel: { color: textColor.value },
        splitLine: { lineStyle: { color: axisColor.value } }
      },
      { 
        type: 'value', 
        name: '成功率', 
        max: 100, 
        axisLabel: { formatter: '{value}%', color: textColor.value },
        nameTextStyle: { color: textColor.value },
        splitLine: { show: false }
      }
    ],
    series: [
      {
        name: '请求数',
        type: 'bar',
        data: data.map(d => d.total),
        itemStyle: { color: '#22d3ee' }
      },
      {
        name: '成功率',
        type: 'line',
        yAxisIndex: 1,
        data: data.map(d => (d.success / d.total * 100).toFixed(1)),
        itemStyle: { color: '#22c55e' },
        lineStyle: { width: 3 }
      }
    ]
  }
})

const errorTrendOption = computed(() => {
  if (!analytics.value) return {}
  const trends = analytics.value.error_trends
  const dates = Array.from(new Set(trends.map(t => t.date))).sort()
  const errorCodes = Array.from(new Set(trends.map(t => t.status_code)))

  return {
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, textStyle: { color: textColor.value } },
    grid: { top: 20, left: 40, right: 20, bottom: 40 },
    xAxis: { 
      type: 'category', 
      data: dates,
      axisLabel: { color: textColor.value },
      axisLine: { lineStyle: { color: axisColor.value } }
    },
    yAxis: { 
      type: 'value',
      axisLabel: { color: textColor.value },
      splitLine: { lineStyle: { color: axisColor.value } }
    },
    series: errorCodes.map(code => ({
      name: `${code}`,
      type: 'bar',
      stack: 'total',
      data: dates.map(date => {
        const item = trends.find(t => t.date === date && t.status_code === code)
        return item ? item.count : 0
      })
    }))
  }
})

const tokenUsageOption = computed(() => {
  if (!analytics.value) return {}
  const trends = analytics.value.model_trends
  const dates = Array.from(new Set(trends.map(t => t.date))).sort()
  const models = selectedModel.value === 'all' ? availableModels.value : [selectedModel.value]

  return {
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, textStyle: { color: textColor.value } },
    grid: { top: 20, left: 60, right: 20, bottom: 40 },
    xAxis: { 
      type: 'category', 
      data: dates,
      axisLabel: { color: textColor.value },
      axisLine: { lineStyle: { color: axisColor.value } }
    },
    yAxis: { 
      type: 'value', 
      axisLabel: { 
        formatter: (v: number) => v >= 1000000 ? (v / 1000000).toFixed(1) + 'M' : v,
        color: textColor.value
      },
      splitLine: { lineStyle: { color: axisColor.value } }
    },
    series: models.map(m => ({
      name: m,
      type: 'line',
      smooth: true,
      data: dates.map(date => {
        const item = trends.find(t => t.date === date && t.model === m)
        return item ? item.input_tokens : 0
      })
    }))
  }
})

const modelRequestOption = computed(() => {
  if (!analytics.value) return {}
  const trends = analytics.value.model_trends
  const dates = Array.from(new Set(trends.map(t => t.date))).sort()
  const models = selectedModel.value === 'all' ? availableModels.value : [selectedModel.value]

  return {
    tooltip: { trigger: 'axis' },
    legend: { bottom: 0, textStyle: { color: textColor.value } },
    grid: { top: 20, left: 40, right: 20, bottom: 40 },
    xAxis: { 
      type: 'category', 
      data: dates,
      axisLabel: { color: textColor.value },
      axisLine: { lineStyle: { color: axisColor.value } }
    },
    yAxis: { 
      type: 'value',
      axisLabel: { color: textColor.value },
      splitLine: { lineStyle: { color: axisColor.value } }
    },
    series: models.map(m => ({
      name: m,
      type: 'line',
      smooth: true,
      data: dates.map(date => {
        const item = trends.find(t => t.date === date && t.model === m)
        return item ? item.request_count : 0
      })
    }))
  }
})

const rpmPeakOption = computed(() => {
  if (!analytics.value || !peakModel.value) return {}
  const data = analytics.value.minute_usage.filter(u => u.model === peakModel.value)
  return {
    tooltip: { trigger: 'axis' },
    grid: { top: 10, left: 40, right: 10, bottom: 20 },
    xAxis: { type: 'category', data: data.map(d => d.minute.split(' ')[1]), axisLabel: { show: false } },
    yAxis: { 
      type: 'value',
      axisLabel: { color: textColor.value },
      splitLine: { lineStyle: { color: axisColor.value } }
    },
    series: [{
      type: 'line',
      areaStyle: { opacity: 0.1 },
      data: data.map(d => d.rpm),
      markLine: {
        silent: true,
        lineStyle: { color: '#ef4444', type: 'dashed' },
        data: [{ yAxis: 1000, label: { position: 'start', formatter: 'Limit' } }]
      }
    }]
  }
})

const tpmPeakOption = computed(() => {
  if (!analytics.value || !peakModel.value) return {}
  const data = analytics.value.minute_usage.filter(u => u.model === peakModel.value)
  return {
    tooltip: { trigger: 'axis' },
    grid: { top: 10, left: 60, right: 10, bottom: 20 },
    xAxis: { type: 'category', data: data.map(d => d.minute.split(' ')[1]), axisLabel: { show: false } },
    yAxis: { 
      type: 'value', 
      axisLabel: { 
        formatter: (v: number) => v >= 1000000 ? (v / 1000000).toFixed(1) + 'M' : v,
        color: textColor.value
      },
      splitLine: { lineStyle: { color: axisColor.value } }
    },
    series: [{
      type: 'line',
      areaStyle: { opacity: 0.1 },
      data: data.map(d => d.tpm),
      markLine: {
        silent: true,
        lineStyle: { color: '#ef4444', type: 'dashed' },
        data: [{ yAxis: 1000000, label: { position: 'start', formatter: 'Limit' } }]
      }
    }]
  }
})

const rpdPeakOption = computed(() => {
  if (!analytics.value || !peakModel.value) return {}
  const data = analytics.value.model_trends.filter(u => u.model === peakModel.value)
  return {
    tooltip: { trigger: 'axis' },
    grid: { top: 10, left: 40, right: 10, bottom: 20 },
    xAxis: { type: 'category', data: data.map(d => d.date), axisLabel: { show: false } },
    yAxis: { 
      type: 'value',
      axisLabel: { color: textColor.value },
      splitLine: { lineStyle: { color: axisColor.value } }
    },
    series: [{
      type: 'line',
      areaStyle: { opacity: 0.1 },
      data: data.map(d => d.request_count),
      markLine: {
        silent: true,
        lineStyle: { color: '#ef4444', type: 'dashed' },
        data: [{ yAxis: 10000, label: { position: 'start', formatter: 'Limit' } }]
      }
    }]
  }
})

onMounted(() => {
  fetchAnalytics()
})
</script>

<style scoped>
.h-64 {
  height: 16rem;
}

.h-48 {
  height: 12rem;
}
</style>
