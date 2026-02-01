<template>
  <div class="h-full flex flex-col animate-in fade-in slide-in-from-bottom-4 duration-500">
    <!-- Filters Bar -->
    <section class="win-card p-4 mb-6 flex flex-wrap gap-4 items-end">
      <div class="space-y-1.5 flex-1 min-w-[180px]">
        <label class="text-[11px] font-bold text-gray-500 uppercase tracking-widest ml-1">提供商</label>
        <div class="relative">
          <select v-model="filters.provider"
            class="w-full bg-white dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-md px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500/50 appearance-none">
            <option value="">全部</option>
            <option v-for="p in providers" :key="p" :value="p">{{ p }}</option>
          </select>
          <ChevronDown class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
        </div>
      </div>
      <div class="space-y-1.5 flex-1 min-w-[200px]">
        <label class="text-[11px] font-bold text-gray-500 uppercase tracking-widest ml-1">模型名称</label>
        <div class="relative group">
          <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 group-focus-within:text-blue-500" />
          <input v-model="filters.model" type="text" placeholder="搜索模型..."
            class="w-full bg-white dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-md pl-10 pr-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500/50 transition-all" />
        </div>
      </div>
      <div class="space-y-1.5 w-28">
        <label class="text-[11px] font-bold text-gray-500 uppercase tracking-widest ml-1">状态码</label>
        <input v-model.number="filters.status_code" type="number" placeholder="200"
          class="w-full bg-white dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-md px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500/50 transition-all" />
      </div>
      
      <div class="flex gap-2">
        <button @click="fetchLogs" class="win-btn-primary">
          查询
        </button>
        <button @click="resetFilters" class="px-4 py-1.5 bg-black/5 dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-md text-sm font-medium hover:bg-black/10 transition-colors">
          重置
        </button>
      </div>

      <div class="ml-auto flex items-center gap-2 border-l border-black/5 dark:border-white/5 pl-4">
         <button @click="exportData('csv')" class="p-2 hover:bg-black/5 dark:hover:bg-white/5 rounded-md text-gray-600 dark:text-gray-400 transition-colors" title="导出 CSV">
            <Download class="w-5 h-5" />
         </button>
         <button @click="onClearLogs" class="p-2 hover:bg-red-500/10 hover:text-red-500 rounded-md text-gray-600 dark:text-gray-400 transition-colors" title="清空日志">
            <Trash2 class="w-5 h-5" />
         </button>
      </div>
    </section>

    <!-- Table Container -->
    <div class="flex-1 win-card overflow-hidden flex flex-col relative">
      <div class="flex-1 overflow-auto custom-scrollbar">
        <table class="w-full text-left border-collapse min-w-[800px]">
          <thead>
            <tr class="sticky top-0 bg-white/80 dark:bg-gray-800/80 backdrop-blur-md z-10 text-[11px] font-bold text-gray-500 uppercase tracking-widest border-b border-black/5 dark:border-white/5">
              <th class="px-6 py-4">时间</th>
              <th class="px-6 py-4">模型 / 提供商</th>
              <th class="px-6 py-4">端点</th>
              <th class="px-6 py-4">消耗</th>
              <th class="px-6 py-4">延迟</th>
              <th class="px-6 py-4">状态</th>
              <th class="px-6 py-4 text-right">操作</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-black/5 dark:divide-white/5 text-[13px]">
            <tr v-for="log in logs" :key="log.id" class="group hover:bg-black/[0.02] dark:hover:bg-white/[0.02] transition-colors">
              <td class="px-6 py-4 text-gray-500">
                <div class="flex flex-col">
                  <span>{{ formatDate(log.timestamp) }}</span>
                  <span class="text-[10px] opacity-60">{{ formatTime(log.timestamp) }}</span>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="flex flex-col">
                  <span class="font-bold text-gray-900 dark:text-white">{{ log.model }}</span>
                  <span class="text-[10px] font-bold text-blue-600 dark:text-blue-400 uppercase tracking-tighter">{{ log.provider }}</span>
                </div>
              </td>
              <td class="px-6 py-4">
                <span class="px-2 py-0.5 rounded bg-black/5 dark:bg-white/5 text-[10px] font-bold text-gray-500 uppercase">
                  {{ log.endpoint }}
                </span>
              </td>
              <td class="px-6 py-4">
                <div class="flex flex-col">
                  <span class="font-mono font-bold">{{ log.total_tokens }}</span>
                  <span class="text-[10px] text-gray-400 font-mono">{{ log.prompt_tokens }}P + {{ log.completion_tokens }}C</span>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-1.5">
                   <Clock class="w-3 h-3 text-gray-400" />
                   <span class="font-mono font-medium">{{ log.latency.toFixed(2) }}s</span>
                </div>
              </td>
              <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                   <div class="w-2 h-2 rounded-full" :class="getStatusColor(log.status_code)"></div>
                   <span class="font-bold font-mono">{{ log.status_code }}</span>
                </div>
              </td>
              <td class="px-6 py-4 text-right">
                <button @click="openDetail(log)" class="px-3 py-1 bg-blue-500 text-white rounded text-xs font-bold transition-all hover:bg-blue-600">
                  详情
                </button>
              </td>
            </tr>
            <tr v-if="logs.length === 0" class="text-center">
              <td colspan="7" class="py-24">
                <Inbox class="w-12 h-12 mx-auto mb-3 text-gray-200" />
                <p class="text-sm font-medium text-gray-400 uppercase tracking-widest">无日志数据</p>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Pagination Footer -->
      <footer class="h-14 border-t border-black/5 dark:border-white/5 px-6 flex items-center justify-between bg-black/[0.01] dark:bg-white/[0.01]">
        <div class="text-xs font-bold text-gray-400 uppercase tracking-widest">
           Showing {{ offset + 1 }}-{{ offset + logs.length }} 
        </div>
        <div class="flex items-center gap-2">
          <button @click="prevPage" :disabled="offset === 0" class="p-1.5 hover:bg-black/5 dark:hover:bg-white/5 rounded-md disabled:opacity-30 transition-colors">
            <ChevronLeft class="w-5 h-5" />
          </button>
          <span class="text-sm font-bold min-w-[20px] text-center">{{ Math.floor(offset / limit) + 1 }}</span>
          <button @click="nextPage" :disabled="logs.length < limit" class="p-1.5 hover:bg-black/5 dark:hover:bg-white/5 rounded-md disabled:opacity-30 transition-colors">
            <ChevronRight class="w-5 h-5" />
          </button>
        </div>
      </footer>
    </div>

    <!-- Detail Slide-over -->
    <div v-if="isDetailView" class="fixed inset-0 z-[100] flex justify-end">
       <div class="absolute inset-0 bg-black/20 backdrop-blur-sm" @click="closeDetail"></div>
       <div class="w-full max-w-2xl bg-white dark:bg-[#1c1c1c] shadow-2xl animate-in slide-in-from-right duration-300 flex flex-col relative z-10">
          <!-- Detail Header -->
          <header class="h-16 border-b border-black/5 dark:border-white/5 px-6 flex items-center justify-between shrink-0">
             <div class="flex items-center gap-4">
                <button @click="closeDetail" class="p-2 hover:bg-black/5 dark:hover:bg-white/5 rounded-full">
                   <ChevronRight class="w-5 h-5" />
                </button>
                <h3 class="text-lg font-bold">日志详情</h3>
             </div>
             <div class="flex items-center gap-3">
                <button @click="openInPlayground" class="win-btn-primary flex items-center gap-2 text-xs">
                   <Terminal class="w-4 h-4" /> Playground
                </button>
                <button @click="onDeleteLog(selectedLog?.id || 0)" class="p-2 hover:bg-red-500/10 hover:text-red-500 rounded-md transition-colors">
                   <Trash2 class="w-5 h-5" />
                </button>
             </div>
          </header>

          <!-- Detail Content -->
          <div v-if="selectedLog" class="flex-1 overflow-y-auto p-8 custom-scrollbar space-y-8">
             <!-- Status Header -->
             <div class="flex items-center justify-between p-6 rounded-2xl bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5">
                <div class="space-y-1">
                   <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Request ID</p>
                   <p class="font-mono text-xs break-all">{{ selectedLog.request_id || 'N/A' }}</p>
                </div>
                <div class="text-right">
                   <p class="text-[10px] font-bold text-gray-400 uppercase tracking-widest mb-1">Status</p>
                   <span :class="getStatusClass(selectedLog.status_code)" class="px-3 py-1 rounded-full text-xs font-bold font-mono">
                      {{ selectedLog.status_code }}
                   </span>
                </div>
             </div>

             <!-- Metadata Grid -->
             <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
                <div v-for="item in detailMeta" :key="item.label">
                   <p class="text-[10px] font-bold text-gray-500 uppercase tracking-widest mb-1">{{ item.label }}</p>
                   <p class="text-sm font-semibold">{{ item.value }}</p>
                </div>
             </div>

             <!-- Prompt / Response -->
             <div class="space-y-6">
                <div class="space-y-3">
                   <div class="flex items-center justify-between">
                      <h4 class="text-sm font-bold flex items-center gap-2">
                         <MessageSquare class="w-4 h-4 text-blue-500" /> 用户提示词
                      </h4>
                      <button @click="copyToClipboard(selectedLog.content?.prompt)" class="text-[10px] font-bold text-blue-600 uppercase hover:underline">Copy JSON</button>
                   </div>
                   <div class="bg-black/[0.02] dark:bg-white/[0.02] rounded-xl p-4 border border-black/5 dark:border-white/5">
                      <div v-for="(msg, idx) in parsedPrompt" :key="idx" class="mb-4 last:mb-0">
                         <div class="flex items-center gap-2 mb-1.5">
                            <span class="text-[10px] font-bold uppercase tracking-widest px-1.5 py-0.5 rounded" :class="msg.role === 'user' ? 'bg-blue-500 text-white' : 'bg-gray-500 text-white'">{{ msg.role }}</span>
                         </div>
                         <p class="text-sm leading-relaxed whitespace-pre-wrap font-sans opacity-90">{{ msg.content }}</p>
                      </div>
                   </div>
                </div>

                <div class="space-y-3">
                   <div class="flex items-center justify-between">
                      <h4 class="text-sm font-bold flex items-center gap-2">
                         <Bot class="w-4 h-4 text-green-500" /> 模型响应
                      </h4>
                      <button @click="copyToClipboard(selectedLog.content?.response)" class="text-[10px] font-bold text-blue-600 uppercase hover:underline">Copy Text</button>
                   </div>
                   <div class="bg-black/[0.02] dark:bg-white/[0.02] rounded-xl p-6 border border-black/5 dark:border-white/5 prose prose-sm dark:prose-invert max-w-none" v-html="renderMarkdown(selectedLog.content?.response)">
                   </div>
                </div>

                <div v-if="selectedLog.content?.error" class="space-y-3">
                   <h4 class="text-sm font-bold text-red-500 flex items-center gap-2">
                      <AlertCircle class="w-4 h-4" /> 错误详情
                   </h4>
                   <div class="bg-red-500/5 rounded-xl p-4 border border-red-500/10">
                      <pre class="text-xs font-mono text-red-500 whitespace-pre-wrap">{{ selectedLog.content?.error }}</pre>
                   </div>
                </div>
             </div>
          </div>
       </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import MarkdownIt from 'markdown-it'
import { useUIStore } from '@/stores/ui'
import { usePlaygroundStore } from '@/stores/playground'
import {
  getLogs,
  getLogDetail,
  getStats,
  deleteLog,
  clearLogs,
  type Log
} from '@/api'
import {
  Search,
  MessageSquare,
  AlertCircle,
  Download,
  User,
  Bot,
  ChevronLeft,
  ChevronRight,
  ChevronDown,
  Copy,
  Clock,
  Cpu,
  Trash2,
  Terminal,
  Inbox
} from 'lucide-vue-next'

const ui = useUIStore()
const playgroundStore = usePlaygroundStore()
const logs = ref<Log[]>([])
const providers = ref<string[]>([])
const selectedLog = ref<Log | null>(null)
const isDetailView = ref(false)
const limit = ref(20)
const offset = ref(0)

const md = new MarkdownIt({
  html: true,
  linkify: true,
  typographer: true
})

const filters = reactive({
  provider: '',
  model: '',
  status_code: undefined as number | undefined
})

const parsedPrompt = computed(() => {
  if (!selectedLog.value?.content?.prompt) return []
  try {
    const data = JSON.parse(selectedLog.value.content.prompt)
    if (Array.isArray(data)) return data
    if (typeof data === 'object') return [data]
    return [{ role: 'user', content: String(data) }]
  } catch (e) {
    return [{ role: 'user', content: selectedLog.value.content.prompt }]
  }
})

const detailMeta = computed(() => [
  { label: 'Provider', value: selectedLog.value?.provider },
  { label: 'Model', value: selectedLog.value?.model },
  { label: 'Latency', value: selectedLog.value?.latency.toFixed(3) + 's' },
  { label: 'Tokens', value: selectedLog.value?.total_tokens },
])

function renderMarkdown(content: string | null | undefined) {
  if (!content) return '<p class="text-gray-400 italic">No content</p>'
  return md.render(content)
}

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

function formatDate(timestamp: string) {
  return new Date(timestamp).toLocaleDateString()
}

function formatTime(timestamp: string) {
  return new Date(timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

function getStatusColor(code: number) {
  if (code >= 200 && code < 300) return 'bg-green-500'
  if (code >= 400 && code < 500) return 'bg-yellow-500'
  return 'bg-red-500'
}

function getStatusClass(code: number) {
  if (code >= 200 && code < 300) return 'bg-green-500/10 text-green-500 border border-green-500/20'
  if (code >= 400 && code < 500) return 'bg-yellow-500/10 text-yellow-500 border border-yellow-500/20'
  return 'bg-red-500/10 text-red-500 border border-red-500/20'
}

async function openDetail(log: Log) {
  try {
    const detail = await getLogDetail(log.id)
    selectedLog.value = detail
    isDetailView.value = true
  } catch (err) {
    ui.showToast('获取详情失败', 'error')
  }
}

function closeDetail() {
  isDetailView.value = false
  selectedLog.value = null
}

function copyToClipboard(text: string | null | undefined) {
  if (!text) return
  navigator.clipboard.writeText(text).then(() => {
    ui.showToast('已复制', 'success')
  })
}

async function onDeleteLog(id: number) {
  if (await ui.confirm('确认删除', '确定要删除这条日志吗？')) {
    try {
      await deleteLog(id)
      ui.showToast('已删除', 'success')
      closeDetail()
      fetchLogs()
    } catch (err) {
      ui.showToast('删除失败', 'error')
    }
  }
}

async function onClearLogs() {
  if (await ui.confirm('清空日志', '确定要删除当前所有过滤条件的日志吗？')) {
    try {
      await clearLogs(filters)
      ui.showToast('日志已清空', 'success')
      fetchLogs()
    } catch (err) {
      ui.showToast('操作失败', 'error')
    }
  }
}

function openInPlayground() {
  if (selectedLog.value) {
    playgroundStore.loadFromLog(selectedLog.value)
    // Redirect logic would go here if needed, but the store handles state
    ui.showToast('已加载到演练场', 'success')
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
