<template>
  <div class="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
    <!-- Header -->
    <div class="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-3">
          <BarChart2 class="w-7 h-7 text-blue-500" />
          分析报告
        </h2>
        <p class="text-sm text-gray-500 mt-1">API 使用趋势与性能指标</p>
      </div>
      <div class="flex items-center gap-3">
        <button @click="handleExport" class="flex items-center gap-2 px-3 py-1.5 bg-gray-100 dark:bg-gray-800 rounded-lg text-sm hover:bg-gray-200 dark:hover:bg-gray-700 transition">
          <Download class="w-4 h-4" />
          导出
        </button>
        <select v-model="daysRange" @change="loadData" class="px-3 py-1.5 rounded-lg text-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
          <option :value="7">7 天</option>
          <option :value="14">14 天</option>
          <option :value="30">30 天</option>
          <option :value="90">90 天</option>
        </select>
        <button @click="loadData" :disabled="loading" class="p-2 rounded-lg bg-gray-100 dark:bg-gray-800 hover:bg-gray-200 dark:hover:bg-gray-700 disabled:opacity-50 transition">
          <RefreshCw class="w-4 h-4" :class="{ 'animate-spin': loading }" />
        </button>
      </div>
    </div>

    <!-- Key Metrics -->
    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      <MetricCard
        v-for="metric in keyMetrics"
        :key="metric.label"
        :label="metric.label"
        :value="metric.value"
        :trend="metric.trend"
        :color="metric.color"
        :icon="metric.icon"
      />
    </div>

    <!-- Charts Grid -->
    <div v-if="data" class="grid grid-cols-1 lg:grid-cols-2 gap-6">
      <!-- Request Trends -->
      <ChartCard title="请求趋势">
        <template #actions>
          <div class="flex gap-1">
            <button @click="chartType = 'bar'" :class="chartType === 'bar' ? 'text-blue-500' : 'text-gray-400'">柱状</button>
            <span class="text-gray-300">|</span>
            <button @click="chartType = 'line'" :class="chartType === 'line' ? 'text-blue-500' : 'text-gray-400'">折线</button>
          </div>
        </template>
        <div style="width: 100%; height: 300px;">
          <v-chart :option="requestChartOption" autoresize />
        </div>
      </ChartCard>

      <!-- Error Distribution -->
      <ChartCard title="错误分布">
        <div style="width: 100%; height: 300px;">
          <v-chart :option="errorChartOption" autoresize />
        </div>
      </ChartCard>

      <!-- Provider Pie -->
      <ChartCard title="提供商分布">
        <div style="width: 100%; height: 300px;">
          <v-chart :option="providerChartOption" autoresize />
        </div>
      </ChartCard>

      <!-- Latency Distribution -->
      <ChartCard title="延迟分布">
        <div style="width: 100%; height: 300px;">
          <v-chart :option="latencyChartOption" autoresize />
        </div>
      </ChartCard>
    </div>

    <!-- Model Radar -->
    <ChartCard v-if="data && topModels.length > 0" title="模型性能">
      <template #actions>
        <select v-model="selectedRadarModel" class="text-sm px-2 py-1 rounded bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700">
          <option v-for="m in topModels" :key="m" :value="m">{{ m.split('/')[1] || m }}</option>
        </select>
      </template>
      <div style="width: 100%; height: 350px;">
        <v-chart :option="radarChartOption" autoresize />
      </div>
    </ChartCard>

    <!-- Hourly Heatmap -->
    <ChartCard v-if="data" title="使用热力图">
      <div style="width: 100%; height: 300px;">
        <v-chart :option="heatmapChartOption" autoresize />
      </div>
    </ChartCard>

    <!-- Peak Metrics -->
    <div v-if="data" class="grid grid-cols-1 md:grid-cols-3 gap-6">
      <ChartCard title="RPM 峰值" :subtitle="formatNumber(maxRPM)">
        <div style="width: 100%; height: 180px;">
          <v-chart :option="rpmChartOption" autoresize />
        </div>
      </ChartCard>
      <ChartCard title="TPM 峰值" :subtitle="formatTokens(maxTPM)">
        <div style="width: 100%; height: 180px;">
          <v-chart :option="tpmChartOption" autoresize />
        </div>
      </ChartCard>
      <ChartCard title="RPD 总计" :subtitle="formatNumber(totalRPD)">
        <div style="width: 100%; height: 180px;">
          <v-chart :option="rpdChartOption" autoresize />
        </div>
      </ChartCard>
    </div>

    <!-- Detailed Table -->
    <div class="win-card overflow-hidden">
      <div class="p-4 border-b border-black/5 dark:border-white/5 flex justify-between items-center">
        <h3 class="font-semibold text-gray-900 dark:text-white">详细数据</h3>
        <button @click="showTable = !showTable" class="text-sm text-blue-500">
          {{ showTable ? '收起' : '展开' }}
        </button>
      </div>
      <div v-if="showTable && data" class="overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-black/[0.02] dark:bg-white/[0.02]">
            <tr>
              <th class="text-left p-4 text-[10px] font-bold text-gray-500 uppercase tracking-widest">日期</th>
              <th class="text-right p-4 text-[10px] font-bold text-gray-500 uppercase tracking-widest">请求</th>
              <th class="text-right p-4 text-[10px] font-bold text-gray-500 uppercase tracking-widest">成功</th>
              <th class="text-right p-4 text-[10px] font-bold text-gray-500 uppercase tracking-widest">失败</th>
              <th class="text-right p-4 text-[10px] font-bold text-gray-500 uppercase tracking-widest">成功率</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-black/5 dark:divide-white/5">
            <tr v-for="day in data.overall_trends" :key="day.date" class="hover:bg-black/[0.01] dark:hover:bg-white/[0.01] transition-colors">
              <td class="p-4 font-medium text-gray-900 dark:text-white">{{ day.date }}</td>
              <td class="p-4 text-right text-gray-900 dark:text-white">{{ formatNumber(day.total) }}</td>
              <td class="p-4 text-right text-green-600">{{ formatNumber(day.success) }}</td>
              <td class="p-4 text-right text-red-600">{{ formatNumber(day.total - day.success) }}</td>
              <td class="p-4 text-right">
                <span class="px-2 py-0.5 rounded-full text-xs font-bold"
                  :class="(day.success / day.total * 100) >= 95 ? 'bg-green-500/10 text-green-600' : 'bg-yellow-500/10 text-yellow-600'">
                  {{ ((day.success / day.total) * 100).toFixed(1) }}%
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, LineChart, PieChart, RadarChart, HeatmapChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent, VisualMapComponent } from 'echarts/components'
import VChart from 'vue-echarts'
import { BarChart2, Download, RefreshCw, Activity, CheckCircle, Zap, Target, Clock } from 'lucide-vue-next'
import { getAnalytics, type Analytics } from '@/api'
import { useUIStore } from '@/stores/ui'

// ECharts setup
use([CanvasRenderer, BarChart, LineChart, PieChart, RadarChart, HeatmapChart, GridComponent, TooltipComponent, LegendComponent, VisualMapComponent])

// State
const ui = useUIStore()
const data = ref<Analytics | null>(null)
const daysRange = ref(7)
const loading = ref(false)
const chartType = ref<'bar' | 'line'>('bar')
const selectedRadarModel = ref('')
const showTable = ref(false)

// Computed colors
const isDark = computed(() => ui.isDark)
const textColor = computed(() => isDark.value ? '#e4e4e7' : '#374151')
const gridColor = computed(() => isDark.value ? 'rgba(255,255,255,0.15)' : 'rgba(0,0,0,0.06)')
const bgColor = computed(() => isDark.value ? '#18181b' : '#ffffff')

// Key metrics
const keyMetrics = computed(() => {
  if (!data.value?.summary) return []
  const { summary } = data.value
  const trends = data.value.overall_trends
  let trend = 0

  if (trends.length >= 2) {
    const [prev, curr] = [trends[trends.length - 2], trends[trends.length - 1]]
    if (prev?.total && curr?.total) {
      trend = ((curr.total - prev.total) / prev.total) * 100
    }
  }

  return [
    {
      label: '总请求',
      value: formatNumber(summary.total_requests),
      trend,
      color: 'blue',
      icon: Activity
    },
    {
      label: '成功率',
      value: `${summary.success_rate.toFixed(1)}%`,
      trend: 0,
      color: 'green',
      icon: CheckCircle
    },
    {
      label: '平均延迟',
      value: `${summary.avg_latency.toFixed(2)}s`,
      trend: 0,
      color: 'orange',
      icon: Zap
    },
    {
      label: '总 Token',
      value: formatTokens(data.value.model_trends.reduce((sum, t) => sum + t.total_tokens, 0)),
      trend: 0,
      color: 'purple',
      icon: Target
    }
  ]
})

// Available models
const availableModels = computed(() => {
  if (!data.value) return []
  const models = new Set<string>()
  data.value.model_trends.forEach(t => models.add(`${t.provider}/${t.model}`))
  return Array.from(models)
})

const topModels = computed(() => availableModels.value.slice(0, 5))

// Peak values
const maxRPM = computed(() => {
  if (!data.value) return 0
  return Math.max(...data.value.minute_usage.map(u => u.rpm), 0)
})

const maxTPM = computed(() => {
  if (!data.value) return 0
  return Math.max(...data.value.minute_usage.map(u => u.tpm), 0)
})

const totalRPD = computed(() => {
  if (!data.value) return 0
  return data.value.overall_trends.reduce((sum, d) => sum + d.total, 0)
})

// Chart options
const requestChartOption = computed(() => {
  if (!data.value) return {}
  const trends = data.value.overall_trends

  return {
    tooltip: { trigger: 'axis', backgroundColor: bgColor.value, textStyle: { color: textColor.value } },
    legend: { bottom: 0, textStyle: { color: textColor.value, fontSize: 11 } },
    grid: { left: 40, right: 20, bottom: 40, top: 20, containLabel: true },
    xAxis: {
      type: 'category',
      data: trends.map(d => d.date.slice(5)),
      axisLabel: { color: textColor.value, fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: textColor.value, fontSize: 10 },
      splitLine: { lineStyle: { color: gridColor.value } }
    },
    series: [
      {
        name: '请求',
        type: chartType.value,
        data: trends.map(d => d.total),
        itemStyle: { color: '#3b82f6' },
        barWidth: '60%',
        smooth: true
      },
      {
        name: '成功',
        type: 'line',
        data: trends.map(d => d.success),
        itemStyle: { color: '#10b981' },
        smooth: true
      }
    ]
  }
})

const errorChartOption = computed(() => {
  if (!data.value) return {}
  const errors = data.value.error_trends
  const dates = Array.from(new Set(errors.map(e => e.date))).sort()
  const codes = Array.from(new Set(errors.map(e => e.status_code)))

  return {
    tooltip: { trigger: 'axis', backgroundColor: bgColor.value, textStyle: { color: textColor.value } },
    legend: { bottom: 0, textStyle: { color: textColor.value, fontSize: 11 } },
    grid: { left: 40, right: 20, bottom: 40, top: 20, containLabel: true },
    xAxis: {
      type: 'category',
      data: dates.map(d => d.slice(5)),
      axisLabel: { color: textColor.value, fontSize: 10 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: textColor.value, fontSize: 10 },
      splitLine: { lineStyle: { color: gridColor.value } }
    },
    series: codes.map((code, i) => ({
      name: `${code}`,
      type: 'bar',
      stack: 'total',
      data: dates.map(date => errors.find(e => e.date === date && e.status_code === code)?.count || 0),
      itemStyle: { color: ['#ef4444', '#f59e0b', '#eab308', '#84cc16'][i % 4] }
    }))
  }
})

const providerChartOption = computed(() => {
  if (!data.value) return {}
  const counts = new Map<string, number>()
  data.value.model_trends.forEach(t => counts.set(t.provider, (counts.get(t.provider) || 0) + t.request_count))

  return {
    tooltip: { trigger: 'item', backgroundColor: bgColor.value, textStyle: { color: textColor.value } },
    legend: { orient: 'vertical', right: 0, top: 'center', textStyle: { color: textColor.value, fontSize: 11 } },
    series: [{
      type: 'pie',
      radius: ['40%', '70%'],
      center: ['35%', '50%'],
      label: { show: false },
      data: Array.from(counts.entries()).map(([name, value], i) => ({
        name,
        value,
        itemStyle: { color: ['#3b82f6', '#8b5cf6', '#10b981', '#f59e0b'][i % 4] }
      }))
    }]
  }
})

const latencyChartOption = computed(() => {
  if (!data.value?.latency_distribution) return {}
  const entries = Object.entries(data.value.latency_distribution)

  return {
    tooltip: { trigger: 'axis', backgroundColor: bgColor.value, textStyle: { color: textColor.value } },
    grid: { left: 40, right: 20, bottom: 40, top: 20, containLabel: true },
    xAxis: {
      type: 'category',
      data: entries.map(e => e[0]),
      axisLabel: { color: textColor.value, fontSize: 9, rotate: 30 }
    },
    yAxis: {
      type: 'value',
      axisLabel: { color: textColor.value, fontSize: 10 },
      splitLine: { lineStyle: { color: gridColor.value } }
    },
    series: [{
      type: 'bar',
      data: entries.map(e => e[1]),
      itemStyle: { color: '#10b981' },
      barWidth: '70%'
    }]
  }
})

const radarChartOption = computed(() => {
  if (!data.value || !selectedRadarModel.value) return {}

  const modelData = data.value.model_trends.filter(t => `${t.provider}/${t.model}` === selectedRadarModel.value)
  const agg = modelData.reduce((acc, t) => ({
    requests: acc.requests + t.request_count,
    input: acc.input + t.input_tokens,
    output: acc.output + t.output_tokens,
    total: acc.total + t.total_tokens
  }), { requests: 0, input: 0, output: 0, total: 0 })

  const max = { requests: 1000, input: 100000, output: 100000, total: 200000 }

  return {
    tooltip: { trigger: 'item' },
    radar: {
      indicator: [
        { name: '请求数', max: max.requests },
        { name: '输入 Token', max: max.input },
        { name: '输出 Token', max: max.output },
        { name: '总 Token', max: max.total }
      ],
      axisName: { color: textColor.value, fontSize: 10 }
    },
    series: [{
      type: 'radar',
      data: [{
        value: [agg.requests / max.requests * 100, agg.input / max.input * 100, agg.output / max.output * 100, agg.total / max.total * 100],
        name: selectedRadarModel.value.split('/')[1],
        areaStyle: { color: 'rgba(249, 115, 22, 0.3)' },
        lineStyle: { color: '#f97316', width: 2 }
      }]
    }]
  }
})

const heatmapChartOption = computed(() => {
  if (!data.value?.hourly_trends) return {}

  const heatData: [number, number, number][] = data.value.hourly_trends.map(h => [parseInt(h.hour), 0, h.count])
  const maxValue = Math.max(...heatData.map(d => d[2]), 1) // 至少为 1 避免 visualMap 问题

  return {
    tooltip: { position: 'top', backgroundColor: bgColor.value, textStyle: { color: textColor.value } },
    grid: { left: 80, right: 20, bottom: 50, top: 20 },
    xAxis: {
      type: 'category',
      data: Array.from({ length: 24 }, (_, i) => `${i}:00`),
      splitArea: { show: true },
      axisLabel: { color: textColor.value, fontSize: 9 }
    },
    yAxis: {
      type: 'category',
      data: [''],
      splitArea: { show: true },
      axisLabel: { color: textColor.value, fontSize: 10 }
    },
    visualMap: {
      min: 0,
      max: maxValue,
      calculable: true,
      orient: 'horizontal',
      left: 'center',
      bottom: 10,
      inRange: { color: ['#f0fdf4', '#86efac', '#22c55e', '#15803d'] },
      textStyle: { color: textColor.value }
    },
    series: [{
      type: 'heatmap',
      data: heatData,
      label: { show: false }
    }]
  }
})

const rpmChartOption = computed(() => {
  if (!data.value) return {}
  const usage = data.value.minute_usage.slice(-30)

  return {
    tooltip: { trigger: 'axis', backgroundColor: bgColor.value, textStyle: { color: textColor.value } },
    grid: { left: 0, right: 0, bottom: 0, top: 0 },
    xAxis: { show: false, type: 'category', data: usage.map(u => u.minute) },
    yAxis: { show: false },
    series: [{
      type: 'line',
      data: usage.map(u => u.rpm),
      areaStyle: { color: 'rgba(59, 130, 246, 0.3)' },
      lineStyle: { color: '#3b82f6', width: 2 },
      smooth: true
    }]
  }
})

const tpmChartOption = computed(() => {
  if (!data.value) return {}
  const usage = data.value.minute_usage.slice(-30)

  return {
    tooltip: { trigger: 'axis', backgroundColor: bgColor.value, textStyle: { color: textColor.value } },
    grid: { left: 0, right: 0, bottom: 0, top: 0 },
    xAxis: { show: false, type: 'category', data: usage.map(u => u.minute) },
    yAxis: { show: false },
    series: [{
      type: 'line',
      data: usage.map(u => u.tpm),
      areaStyle: { color: 'rgba(16, 185, 129, 0.3)' },
      lineStyle: { color: '#10b981', width: 2 },
      smooth: true
    }]
  }
})

const rpdChartOption = computed(() => {
  if (!data.value) return {}
  const trends = data.value.overall_trends

  return {
    tooltip: { trigger: 'axis', backgroundColor: bgColor.value, textStyle: { color: textColor.value } },
    grid: { left: 0, right: 0, bottom: 0, top: 0 },
    xAxis: { show: false, type: 'category', data: trends.map(d => d.date) },
    yAxis: { show: false },
    series: [{
      type: 'line',
      data: trends.map(d => d.total),
      areaStyle: { color: 'rgba(245, 158, 11, 0.3)' },
      lineStyle: { color: '#f59e0b', width: 2 },
      smooth: true
    }]
  }
})

// Functions
async function loadData() {
  loading.value = true
  try {
    const result = await getAnalytics({ days: daysRange.value })
    data.value = result

    const models = topModels.value
    if (models.length > 0 && !selectedRadarModel.value) {
      selectedRadarModel.value = models[0] ?? ''
    }
  } catch (error) {
    console.error('Failed to load analytics:', error)
  } finally {
    loading.value = false
  }
}

function handleExport() {
  if (!data.value) return

  const blob = new Blob([JSON.stringify(data.value, null, 2)], { type: 'application/json' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `analytics-${daysRange.value}days-${new Date().toISOString().split('T')[0]}.json`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

function formatNumber(n: number): string {
  return n.toLocaleString()
}

function formatTokens(n: number): string {
  if (n >= 1000000) return (n / 1000000).toFixed(1) + 'M'
  if (n >= 1000) return (n / 1000).toFixed(1) + 'K'
  return n.toString()
}

// Lifecycle
onMounted(() => {
  loadData()
})
</script>

<script lang="ts">
// Sub-components
import { defineComponent, h } from 'vue'

const MetricCard = defineComponent({
  props: ['label', 'value', 'trend', 'color', 'icon'],
  setup(props) {
    const colorMap: Record<string, string> = {
      blue: 'from-blue-500 to-blue-600',
      green: 'from-green-500 to-green-600',
      orange: 'from-orange-500 to-orange-600',
      purple: 'from-purple-500 to-purple-600'
    }
    return () => h('div', { class: 'win-card p-5' }, [
      h('div', { class: 'flex items-center gap-4' }, [
        h('div', { class: `w-12 h-12 rounded-xl bg-gradient-to-br ${colorMap[props.color]} text-white flex items-center justify-center shadow-lg shadow-black/5` }, [
          h(props.icon, { class: 'w-6 h-6' })
        ]),
        h('div', { class: 'flex-1' }, [
          h('p', { class: 'text-[10px] font-bold text-gray-400 uppercase tracking-wider mb-0.5' }, props.label),
          h('p', { class: 'text-2xl font-bold text-gray-900 dark:text-white tracking-tight' }, props.value)
        ]),
        props.trend !== undefined ? h('span', { class: `text-xs font-bold ${props.trend >= 0 ? 'text-green-500' : 'text-red-500'}` },
          `${props.trend > 0 ? '+' : ''}${props.trend.toFixed(1)}%`
        ) : null
      ])
    ])
  }
})

const ChartCard = defineComponent({
  props: ['title', 'subtitle'],
  setup(props, { slots }) {
    return () => h('div', { class: 'win-card overflow-hidden' }, [
      h('div', { class: 'p-5 border-b border-black/5 dark:border-white/5 flex justify-between items-center' }, [
        h('div', {}, [
          h('h4', { class: 'text-xs font-bold text-gray-500 uppercase tracking-widest' }, props.title),
          props.subtitle ? h('p', { class: 'text-xl font-bold text-gray-900 dark:text-white mt-1' }, props.subtitle) : null
        ]),
        slots.actions?.()
      ]),
      h('div', { class: 'p-4' }, slots.default?.())
    ])
  }
})

export { MetricCard, ChartCard }
</script>
