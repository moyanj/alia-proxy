<template>
  <div class="space-y-6">
    <!-- Filters -->
    <div class="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-wrap gap-4 items-end">
      <div class="space-y-1.5 flex-1 min-w-[200px]">
        <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">提供商</label>
        <select v-model="filters.provider" class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
          <option value="">全部</option>
          <option v-for="p in providers" :key="p" :value="p">{{ p }}</option>
        </select>
      </div>
      <div class="space-y-1.5 flex-1 min-w-[200px]">
        <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">模型 (模糊搜索)</label>
        <input v-model="filters.model" type="text" placeholder="例如: gpt-4" class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
      </div>
      <div class="space-y-1.5 w-32">
        <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">状态码</label>
        <input v-model.number="filters.status_code" type="number" placeholder="200" class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
      </div>
      <div class="flex gap-2">
        <button @click="fetchLogs" class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
          <Search class="w-4 h-4" /> 搜索
        </button>
        <button @click="resetFilters" class="bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 px-4 py-2 rounded-lg text-sm font-medium transition-colors">
          重置
        </button>
      </div>
      <div class="border-l border-gray-200 dark:border-gray-700 pl-4 flex gap-2">
        <div class="relative group">
          <button class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
            <Download class="w-4 h-4" /> 导出数据
          </button>
          <div class="absolute right-0 bottom-full mb-2 w-40 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-xl overflow-hidden opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-20">
            <button @click="exportData('csv')" class="w-full text-left px-4 py-3 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors border-b border-gray-100 dark:border-gray-700">导出为 CSV</button>
            <button @click="exportData('jsonl')" class="w-full text-left px-4 py-3 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors border-b border-gray-100 dark:border-gray-700">导出为 JSONL</button>
            <button @click="exportData('sharegpt')" class="w-full text-left px-4 py-3 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">导出为 ShareGPT</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Log Table -->
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full text-left border-collapse">
          <thead>
            <tr class="bg-gray-50 dark:bg-gray-900/50 text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">
              <th class="px-6 py-4 font-semibold">ID</th>
              <th class="px-6 py-4 font-semibold">时间</th>
              <th class="px-6 py-4 font-semibold">提供商 / 模型</th>
              <th class="px-6 py-4 font-semibold">端点</th>
              <th class="px-6 py-4 font-semibold">Token 消耗</th>
              <th class="px-6 py-4 font-semibold">延时 / 模式</th>
              <th class="px-6 py-4 font-semibold">状态</th>
              <th class="px-6 py-4 font-semibold text-right">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700 text-sm">
            <tr v-for="log in logs" :key="log.id" class="hover:bg-gray-50 dark:hover:bg-gray-700/30 transition-colors">
              <td class="px-6 py-4 text-gray-500 font-mono">#{{ log.id }}</td>
              <td class="px-6 py-4 text-gray-700 dark:text-gray-300">{{ formatTime(log.timestamp) }}</td>
              <td class="px-6 py-4">
                <div class="flex flex-col">
                  <span class="font-medium text-gray-900 dark:text-white">{{ log.provider }}</span>
                  <span class="text-xs text-gray-500">{{ log.model }}</span>
                </div>
              </td>
              <td class="px-6 py-4">
                <span class="px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-xs font-medium text-gray-600 dark:text-gray-300">
                  {{ log.endpoint }}
                </span>
              </td>
              <td class="px-6 py-4 text-gray-600 dark:text-gray-400">
                <div class="flex flex-col text-xs">
                  <span>{{ log.total_tokens }} Total</span>
                  <span class="text-[10px] opacity-70">{{ log.prompt_tokens }}P / {{ log.completion_tokens }}C</span>
                </div>
              </td>
              <td class="px-6 py-4 text-gray-600 dark:text-gray-400">
                <div class="flex flex-col text-xs">
                  <span>{{ log.latency.toFixed(2) }}s</span>
                  <span class="text-[10px] opacity-70">{{ log.is_streaming ? 'Streaming' : 'Non-stream' }}</span>
                </div>
              </td>
              <td class="px-6 py-4">
                <span :class="getStatusClass(log.status_code)" class="px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-tight">
                  {{ log.status_code }}
                </span>
              </td>
              <td class="px-6 py-4 text-right">
                <button @click="openDetail(log)" class="text-blue-600 dark:text-blue-400 hover:underline">详情</button>
              </td>
            </tr>
            <tr v-if="logs.length === 0" class="text-center">
              <td colspan="7" class="py-12 text-gray-400">未找到相关日志</td>
            </tr>
          </tbody>
        </table>
      </div>
      
      <!-- Pagination -->
      <div class="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-between items-center bg-gray-50/50 dark:bg-gray-900/20">
        <div class="text-xs text-gray-500">
          第 {{ offset + 1 }} - {{ offset + logs.length }} 条日志
        </div>
        <div class="flex gap-2">
          <button @click="prevPage" :disabled="offset === 0" class="px-3 py-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-xs disabled:opacity-50">上一页</button>
          <button @click="nextPage" :disabled="logs.length < limit" class="px-3 py-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-xs disabled:opacity-50">下一页</button>
        </div>
      </div>
    </div>

    <!-- Detail Modal -->
    <div v-if="selectedLog" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div class="bg-white dark:bg-gray-800 w-full max-w-4xl max-h-[90vh] rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in duration-200">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">请求详情 #{{ selectedLog.id }}</h3>
          <button @click="selectedLog = null" class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
            <X class="w-6 h-6" />
          </button>
        </div>
        <div class="flex-1 overflow-auto p-6 space-y-6">
          <div class="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div class="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-xl">
              <p class="text-[10px] uppercase font-bold text-gray-400 mb-1">Provider</p>
              <p class="text-sm font-semibold">{{ selectedLog.provider }}</p>
            </div>
            <div class="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-xl">
              <p class="text-[10px] uppercase font-bold text-gray-400 mb-1">Model</p>
              <p class="text-sm font-semibold">{{ selectedLog.model }}</p>
            </div>
            <div class="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-xl">
              <p class="text-[10px] uppercase font-bold text-gray-400 mb-1">Timestamp</p>
              <p class="text-sm font-semibold">{{ formatTime(selectedLog.timestamp) }}</p>
            </div>
            <div class="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-xl">
              <p class="text-[10px] uppercase font-bold text-gray-400 mb-1">Status</p>
              <span :class="getStatusClass(selectedLog.status_code)" class="px-2 py-0.5 rounded text-[10px] font-bold uppercase">{{ selectedLog.status_code }}</span>
            </div>
          </div>

          <div class="space-y-4">
            <div class="space-y-2">
              <h4 class="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <MessageSquare class="w-4 h-4 text-blue-500" /> Prompt
              </h4>
              <pre class="p-4 bg-gray-900 text-gray-300 rounded-xl text-xs overflow-auto max-h-60 whitespace-pre-wrap font-mono">{{ selectedLog.content?.prompt }}</pre>
            </div>
            <div class="space-y-2">
              <h4 class="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
                <CheckCircle2 class="w-4 h-4 text-green-500" /> Response
              </h4>
              <pre class="p-4 bg-gray-900 text-gray-300 rounded-xl text-xs overflow-auto max-h-60 whitespace-pre-wrap font-mono">{{ selectedLog.content?.response }}</pre>
            </div>
            <div v-if="selectedLog.content?.error" class="space-y-2">
              <h4 class="text-sm font-bold text-red-500 flex items-center gap-2">
                <AlertCircle class="w-4 h-4" /> Error
              </h4>
              <pre class="p-4 bg-red-900/20 text-red-400 border border-red-900/50 rounded-xl text-xs overflow-auto whitespace-pre-wrap font-mono">{{ selectedLog.content?.error }}</pre>
            </div>
            <div v-if="selectedLog.media && selectedLog.media.length > 0" class="space-y-2">
              <h4 class="text-sm font-bold text-purple-500 flex items-center gap-2">
                <Image class="w-4 h-4" /> Media Files
              </h4>
              <div v-for="m in selectedLog.media" :key="m.file_path" class="p-4 bg-gray-50 dark:bg-gray-900/50 rounded-xl flex items-center justify-between mb-2">
                <span class="text-xs font-mono truncate mr-4">{{ m.file_path }}</span>
                <a :href="`/api/media/${m.file_path.split('/').pop()}`" target="_blank" class="text-xs bg-purple-600 hover:bg-purple-700 text-white px-3 py-1 rounded-lg transition-colors">查看媒体</a>
              </div>
            </div>
          </div>
        </div>
        <div class="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
          <button @click="onDeleteLog(selectedLog.id)" class="text-red-500 hover:text-red-600 text-sm font-medium mr-auto">删除记录</button>
          <button @click="selectedLog = null" class="bg-gray-900 dark:bg-white text-white dark:text-gray-900 px-6 py-2 rounded-xl text-sm font-bold transition-all hover:scale-105 active:scale-95">关闭</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useUIStore } from '@/stores/ui'
import { 
  getLogs, 
  getStats, 
  deleteLog,
  type Log 
} from '@/api'
import { 
  Search, 
  X, 
  MessageSquare, 
  CheckCircle2, 
  AlertCircle,
  Image,
  Download
} from 'lucide-vue-next'

const ui = useUIStore()
const logs = ref<Log[]>([])
const providers = ref<string[]>([])
const selectedLog = ref<Log | null>(null)
const limit = ref(20)
const offset = ref(0)

const filters = reactive({
  provider: '',
  model: '',
  status_code: undefined as number | undefined
})

async function fetchLogs() {
  try {
    const data = await getLogs({
      limit: limit.value,
      offset: offset.value,
      ...filters
    })
    logs.value = data
  } catch (err) {
    console.error('Failed to fetch logs:', err)
  }
}

async function fetchProviders() {
  try {
    const stats = await getStats()
    providers.value = Object.keys(stats.providers_config)
  } catch (err) {
    console.error('Failed to fetch providers:', err)
  }
}

function resetFilters() {
  filters.provider = ''
  filters.model = ''
  filters.status_code = undefined
  offset.value = 0
  fetchLogs()
}

function nextPage() {
  offset.value += limit.value
  fetchLogs()
}

function prevPage() {
  if (offset.value >= limit.value) {
    offset.value -= limit.value
    fetchLogs()
  }
}

function formatTime(timestamp: string) {
  return new Date(timestamp).toLocaleString()
}

function getStatusClass(code: number) {
  if (code >= 200 && code < 300) return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
  if (code >= 400 && code < 500) return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
  return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
}

function openDetail(log: Log) {
  selectedLog.value = log
}

async function onDeleteLog(id: number) {
  if (await ui.confirm('确认删除', '确定要删除这条日志吗？')) {
    try {
      await deleteLog(id)
      ui.showToast('日志已删除', 'success')
      selectedLog.value = null
      fetchLogs()
    } catch (err) {
      ui.showToast('删除失败', 'error')
    }
  }
}

function exportData(format: string) {
  window.open(`/api/export?format=${format}`, '_blank')
}

onMounted(() => {
  fetchLogs()
  fetchProviders()
})
</script>
