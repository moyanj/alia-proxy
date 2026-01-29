<template>
  <div class="h-full">
    <!-- List View -->
    <div v-if="!isDetailView" class="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
      <!-- Filters -->
      <div
        class="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-wrap gap-4 items-end">
        <div class="space-y-1.5 flex-1 min-w-[200px]">
          <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">提供商</label>
          <select v-model="filters.provider"
            class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none">
            <option value="">全部</option>
            <option v-for="p in providers" :key="p" :value="p">{{ p }}</option>
          </select>
        </div>
        <div class="space-y-1.5 flex-1 min-w-[200px]">
          <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">模型 (模糊搜索)</label>
          <input v-model="filters.model" type="text" placeholder="例如: gpt-4"
            class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
        </div>
        <div class="space-y-1.5 w-32">
          <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">状态码</label>
          <input v-model.number="filters.status_code" type="number" placeholder="200"
            class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none" />
        </div>
        <div class="flex gap-2">
          <button @click="fetchLogs"
            class="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
            <Search class="w-4 h-4" /> 搜索
          </button>
          <button @click="resetFilters"
            class="bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-200 px-4 py-2 rounded-lg text-sm font-medium transition-colors">
            重置
          </button>
        </div>
        <div class="border-l border-gray-200 dark:border-gray-700 pl-4 flex gap-2">
          <div class="relative group">
            <button
              class="bg-green-600 hover:bg-green-700 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center gap-2">
              <Download class="w-4 h-4" /> 导出数据
            </button>
            <div
              class="absolute right-0 bottom-full mb-2 w-40 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl shadow-xl overflow-hidden opacity-0 invisible group-hover:opacity-100 group-hover:visible transition-all z-20">
              <button @click="exportData('csv')"
                class="w-full text-left px-4 py-3 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors border-b border-gray-100 dark:border-gray-700">导出为
                CSV</button>
              <button @click="exportData('jsonl')"
                class="w-full text-left px-4 py-3 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors border-b border-gray-100 dark:border-gray-700">导出为
                JSONL</button>
              <button @click="exportData('sharegpt')"
                class="w-full text-left px-4 py-3 text-sm hover:bg-gray-50 dark:hover:bg-gray-700 transition-colors">导出为
                ShareGPT</button>
            </div>
          </div>
        </div>
      </div>

      <!-- Log Table -->
      <div
        class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full text-left border-collapse">
            <thead>
              <tr
                class="bg-gray-50 dark:bg-gray-900/50 text-gray-500 dark:text-gray-400 text-xs uppercase tracking-wider">
                <th class="px-6 py-4 font-semibold">ID</th>
                <th class="px-6 py-4 font-semibold">时间</th>
                <th class="px-6 py-4 font-semibold">模型 / 提供商</th>
                <th class="px-6 py-4 font-semibold">端点</th>
                <th class="px-6 py-4 font-semibold">Token 消耗</th>
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
                    <span class="font-medium text-gray-900 dark:text-white">{{ log.model }}</span>
                    <span class="text-xs text-gray-500">{{ log.provider }}</span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span
                    class="px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-xs font-medium text-gray-600 dark:text-gray-300">
                    {{ log.endpoint }}
                  </span>
                </td>
                <td class="px-6 py-4 text-gray-600 dark:text-gray-400">
                  <div class="flex flex-col text-xs">
                    <span>{{ log.total_tokens }} Total</span>
                    <span class="text-[10px] opacity-70">{{ log.prompt_tokens }}P / {{ log.completion_tokens }}C</span>
                  </div>
                </td>
                <td class="px-6 py-4">
                  <span :class="getStatusClass(log.status_code)"
                    class="px-2 py-1 rounded-full text-[10px] font-bold uppercase tracking-tight">
                    {{ log.status_code }}
                  </span>
                </td>
                <td class="px-6 py-4 text-right">
                  <button @click="openDetail(log)" class="text-blue-600 dark:text-blue-400 font-bold hover:underline">查看详情</button>
                </td>
              </tr>
              <tr v-if="logs.length === 0" class="text-center">
                <td colspan="7" class="py-12 text-gray-400">未找到相关日志</td>
              </tr>
            </tbody>
          </table>
        </div>

        <!-- Pagination -->
        <div
          class="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-between items-center bg-gray-50/50 dark:bg-gray-900/20">
          <div class="text-xs text-gray-500">
            第 {{ offset + 1 }} - {{ offset + logs.length }} 条日志
          </div>
          <div class="flex gap-2">
            <button @click="prevPage" :disabled="offset === 0"
              class="px-3 py-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-xs disabled:opacity-50">上一页</button>
            <button @click="nextPage" :disabled="logs.length < limit"
              class="px-3 py-1 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-lg text-xs disabled:opacity-50">下一页</button>
          </div>
        </div>
      </div>
    </div>

    <!-- Detail View -->
    <div v-else-if="selectedLog" class="flex flex-col h-[calc(100%+3rem)] -m-6 bg-gray-50 dark:bg-gray-900 animate-in fade-in slide-in-from-right-4 duration-300">
      <!-- Detail Header -->
      <div class="h-14 bg-white dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700 flex items-center justify-between px-4 shrink-0 shadow-sm z-30">
        <div class="flex items-center gap-4">
          <button @click="closeDetail" class="p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors group">
            <ChevronLeft class="w-5 h-5 text-gray-500 group-hover:text-gray-900 dark:group-hover:text-white" />
          </button>
          <div class="h-4 w-[1px] bg-gray-200 dark:bg-gray-700"></div>
          <div class="flex items-center gap-2">
            <span class="text-xs font-mono text-gray-400">#{{ selectedLog.id }}</span>
            <span :class="getStatusClass(selectedLog.status_code)" class="px-2 py-0.5 rounded text-[10px] font-bold uppercase tracking-wider">
              {{ selectedLog.status_code }}
            </span>
          </div>
        </div>

        <div class="flex items-center gap-4">
          <div class="flex items-center gap-2">
            <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Raw Mode</span>
            <button 
              @click="showRawResponse = !showRawResponse"
              :class="showRawResponse ? 'bg-blue-600' : 'bg-gray-200 dark:bg-gray-700'"
              class="relative inline-flex h-5 w-10 items-center rounded-full transition-colors focus:outline-none"
            >
              <span 
                :class="showRawResponse ? 'translate-x-5' : 'translate-x-1'"
                class="inline-block h-3 w-3 transform rounded-full bg-white transition-transform"
              />
            </button>
          </div>
          <div class="h-4 w-[1px] bg-gray-200 dark:bg-gray-700"></div>
          
          <button @click="openInPlayground" 
            class="flex items-center gap-1.5 px-3 py-1.5 bg-blue-50 text-blue-600 dark:bg-blue-900/20 dark:text-blue-400 rounded-lg hover:bg-blue-100 dark:hover:bg-blue-900/40 transition-colors text-xs font-bold uppercase tracking-wide">
            <Terminal class="w-4 h-4" />
            Playground
          </button>
          
          <div class="h-4 w-[1px] bg-gray-200 dark:bg-gray-700"></div>
          
          <button @click="onDeleteLog(selectedLog.id)" class="p-1.5 hover:bg-red-50 dark:hover:bg-red-900/20 text-gray-400 hover:text-red-500 rounded-lg transition-colors">
            <Trash2 class="w-5 h-5" />
          </button>
        </div>
      </div>

      <!-- Detail Content Grid -->
      <div class="flex-1 flex overflow-hidden relative">
        <!-- Main Conversation Area -->
        <div class="flex-1 h-full overflow-y-auto p-8 space-y-8 scrollbar-thin">
          <!-- Conversation Flow -->
          <div class="max-w-4xl mx-auto space-y-8">
            <!-- Parsed Prompts -->
            <div v-for="(msg, idx) in parsedPrompt" :key="idx" class="group">
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-2">
                  <div :class="msg.role === 'user' ? 'bg-blue-500' : 'bg-purple-500'" class="p-1 rounded-md text-white">
                    <component :is="getRoleIcon(msg.role)" class="w-3 h-3" />
                  </div>
                  <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">{{ msg.role }}</span>
                </div>
                <button @click="copyToClipboard(msg.content)" class="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-all text-gray-400">
                  <Copy class="w-3.5 h-3.5" />
                </button>
              </div>
              <div class="bg-white dark:bg-gray-800 rounded-2xl p-6 border border-gray-200 dark:border-gray-700 shadow-sm transition-shadow hover:shadow-md">
                <div class="text-sm leading-relaxed text-gray-700 dark:text-gray-200 whitespace-pre-wrap font-sans">
                  <template v-if="Array.isArray(msg.content)">
                    <div v-for="(part, pIdx) in msg.content" :key="pIdx">
                      <span v-if="part.type === 'text'">{{ part.text }}</span>
                      <div v-else-if="part.type === 'image_url'" class="mt-2">
                        <img :src="part.image_url" class="rounded-lg max-w-md border border-gray-200 dark:border-gray-700" />
                      </div>
                    </div>
                  </template>
                  <template v-else>{{ msg.content }}</template>
                </div>
              </div>
            </div>

            <!-- Response -->
            <div class="group">
              <div class="flex items-center justify-between mb-3">
                <div class="flex items-center gap-2">
                  <div class="bg-green-500 p-1 rounded-md text-white">
                    <Bot class="w-3 h-3" />
                  </div>
                  <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest">Assistant</span>
                </div>
                <button @click="copyToClipboard(selectedLog.content?.response)" class="opacity-0 group-hover:opacity-100 p-1 hover:bg-gray-200 dark:hover:bg-gray-700 rounded transition-all text-gray-400">
                  <Copy class="w-3.5 h-3.5" />
                </button>
              </div>
              
              <div class="bg-white dark:bg-gray-800 rounded-2xl overflow-hidden border border-gray-200 dark:border-gray-700 shadow-sm transition-shadow hover:shadow-md">
                <div v-if="showRawResponse" class="p-6">
                  <pre class="text-xs font-mono text-gray-600 dark:text-gray-400 whitespace-pre-wrap">{{ selectedLog.content?.response }}</pre>
                </div>
                <div v-else class="p-8 prose dark:prose-invert prose-sm max-w-none" v-html="renderMarkdown(selectedLog.content?.response)"></div>
              </div>
            </div>

            <!-- Error -->
            <div v-if="selectedLog.content?.error" class="bg-red-50 dark:bg-red-900/10 border border-red-200 dark:border-red-900/30 rounded-2xl p-6">
              <div class="flex items-center gap-2 mb-3 text-red-600 dark:text-red-400">
                <AlertCircle class="w-4 h-4" />
                <span class="text-xs font-bold uppercase tracking-wider">Error Details</span>
              </div>
              <pre class="text-xs font-mono text-red-700 dark:text-red-300 whitespace-pre-wrap">{{ selectedLog.content?.error }}</pre>
            </div>

            <!-- Media -->
            <div v-if="selectedLog.media?.length" class="space-y-4">
               <h4 class="text-xs font-bold text-gray-400 uppercase tracking-widest">Generated Media</h4>
               <div class="grid grid-cols-2 gap-4">
                 <div v-for="m in selectedLog.media" :key="m.file_path" class="group relative bg-white dark:bg-gray-800 rounded-xl overflow-hidden border border-gray-200 dark:border-gray-700">
                    <img v-if="m.file_type === 'image'" :src="`/api/media/${m.file_path.split('/').pop()}`" class="w-full h-auto" />
                    <audio v-else-if="m.file_type === 'audio'" :src="`/api/media/${m.file_path.split('/').pop()}`" controls class="w-full p-2" />
                    <div class="absolute inset-0 bg-black/40 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                       <a :href="`/api/media/${m.file_path.split('/').pop()}`" target="_blank" class="bg-white text-gray-900 px-4 py-2 rounded-lg text-xs font-bold shadow-xl">Open File</a>
                    </div>
                 </div>
               </div>
            </div>
          </div>
        </div>

        <!-- Sidebar Details Panel -->
        <div class="w-80 bg-white dark:bg-gray-800 border-l border-gray-200 dark:border-gray-700 flex flex-col h-full shadow-lg z-20 shrink-0">
          <div class="flex-1 overflow-y-auto p-6 space-y-8 scrollbar-thin">
            
            <!-- Group 1: Basic Info -->
            <div>
              <h4 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                <Info class="w-3 h-3" /> 基础信息
              </h4>
              <div class="space-y-4">
                <div class="group/item">
                  <label class="text-[10px] font-medium text-gray-500 mb-1 block">Log ID</label>
                  <div class="flex items-center justify-between">
                    <span class="text-sm font-mono font-medium text-gray-900 dark:text-white">#{{ selectedLog.id }}</span>
                    <button @click="copyToClipboard(String(selectedLog.id))" class="opacity-0 group-hover/item:opacity-100 p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-all text-gray-400">
                      <Copy class="w-3 h-3" />
                    </button>
                  </div>
                </div>

                <div v-if="selectedLog.request_id" class="group/item">
                  <label class="text-[10px] font-medium text-gray-500 mb-1 block">Request ID</label>
                  <div class="flex items-center justify-between">
                    <span class="text-xs font-mono text-gray-700 dark:text-gray-300 truncate pr-2" :title="selectedLog.request_id">
                      {{ selectedLog.request_id }}
                    </span>
                    <button @click="copyToClipboard(selectedLog.request_id)" class="opacity-0 group-hover/item:opacity-100 p-1 hover:bg-gray-100 dark:hover:bg-gray-700 rounded transition-all text-gray-400 shrink-0">
                      <Copy class="w-3 h-3" />
                    </button>
                  </div>
                </div>

                <div class="group/item">
                  <label class="text-[10px] font-medium text-gray-500 mb-1 block">创建时间</label>
                  <span class="text-sm text-gray-900 dark:text-white">{{ formatTime(selectedLog.timestamp) }}</span>
                </div>

                <div class="grid grid-cols-2 gap-4">
                   <div>
                      <label class="text-[10px] font-medium text-gray-500 mb-1 block">状态</label>
                      <span :class="getStatusClass(selectedLog.status_code)" class="inline-flex px-2 py-0.5 rounded text-xs font-bold">
                        {{ selectedLog.status_code }}
                      </span>
                   </div>
                   <div>
                      <label class="text-[10px] font-medium text-gray-500 mb-1 block">模式</label>
                      <span class="text-xs font-medium px-2 py-0.5 rounded bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 inline-block">
                        {{ selectedLog.is_streaming ? '流式 (Stream)' : '普通 (Normal)' }}
                      </span>
                   </div>
                </div>
              </div>
            </div>

            <div class="h-[1px] bg-gray-100 dark:bg-gray-700"></div>

            <!-- Group 2: Model & Provider -->
            <div>
              <h4 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                <Cpu class="w-3 h-3" /> 模型配置
              </h4>
              <div class="space-y-4">
                <div>
                  <label class="text-[10px] font-medium text-gray-500 mb-1 block">提供商 (Provider)</label>
                  <div class="flex items-center gap-2">
                     <span class="w-2 h-2 rounded-full bg-blue-500"></span>
                     <span class="text-sm font-medium text-gray-900 dark:text-white">{{ selectedLog.provider }}</span>
                  </div>
                </div>
                <div>
                  <label class="text-[10px] font-medium text-gray-500 mb-1 block">模型 (Model)</label>
                  <span class="text-sm font-mono text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-900 px-2 py-1 rounded border border-gray-100 dark:border-gray-700 block truncate" :title="selectedLog.model">
                    {{ selectedLog.model }}
                  </span>
                </div>
                <div>
                  <label class="text-[10px] font-medium text-gray-500 mb-1 block">端点 (Endpoint)</label>
                  <span class="text-xs font-mono text-gray-500">{{ selectedLog.endpoint }}</span>
                </div>
              </div>
            </div>

            <div class="h-[1px] bg-gray-100 dark:bg-gray-700"></div>

            <!-- Group 3: Stats -->
            <div>
              <h4 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                <Activity class="w-3 h-3" /> 性能与消耗
              </h4>
              
              <div class="bg-gray-50 dark:bg-gray-900/50 rounded-xl p-4 border border-gray-100 dark:border-gray-800 space-y-3">
                 <div class="flex justify-between items-center">
                    <span class="text-xs text-gray-500">响应耗时</span>
                    <span class="text-sm font-mono font-bold text-gray-900 dark:text-white">{{ selectedLog.latency.toFixed(3) }}s</span>
                 </div>
                 <div class="h-[1px] bg-gray-200 dark:bg-gray-700/50"></div>
                 <div class="flex justify-between items-center">
                    <span class="text-xs text-gray-500">提问 Tokens</span>
                    <span class="text-xs font-mono text-gray-700 dark:text-gray-300">{{ selectedLog.prompt_tokens }}</span>
                 </div>
                 <div class="flex justify-between items-center">
                    <span class="text-xs text-gray-500">回答 Tokens</span>
                    <span class="text-xs font-mono text-gray-700 dark:text-gray-300">{{ selectedLog.completion_tokens }}</span>
                 </div>
                 <div class="flex justify-between items-center pt-1">
                    <span class="text-xs font-bold text-gray-700 dark:text-gray-300">Total Tokens</span>
                    <span class="text-sm font-mono font-bold text-blue-600 dark:text-blue-400">{{ selectedLog.total_tokens }}</span>
                 </div>
              </div>
            </div>

            <div class="h-[1px] bg-gray-100 dark:bg-gray-700"></div>

            <!-- Group 4: Client -->
            <div>
               <h4 class="text-xs font-bold text-gray-400 uppercase tracking-widest mb-4 flex items-center gap-2">
                 <Globe class="w-3 h-3" /> 客户端信息
               </h4>
               <div class="space-y-4">
                 <div>
                    <label class="text-[10px] font-medium text-gray-500 mb-1 block">IP 地址</label>
                    <div class="flex items-center gap-2">
                       <span class="text-sm font-mono text-gray-700 dark:text-gray-300">{{ selectedLog.ip_address || '未知' }}</span>
                    </div>
                 </div>
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
  type Log
} from '@/api'
import {
  Search,
  X,
  MessageSquare,
  CheckCircle2,
  AlertCircle,
  Image,
  Download,
  Eye,
  Code,
  User,
  Bot,
  Settings,
  ChevronLeft,
  Copy,
  Clock,
  Cpu,
  Hash,
  Activity,
  Trash2,
  Info,
  Globe,
  Terminal
} from 'lucide-vue-next'

const ui = useUIStore()
const playgroundStore = usePlaygroundStore()
const logs = ref<Log[]>([])
const providers = ref<string[]>([])
const selectedLog = ref<Log | null>(null)
const isDetailView = ref(false)
const limit = ref(20)
const offset = ref(0)
const showRawResponse = ref(false)
const refreshing = ref(false)

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
    return [data]
  } catch (e) {
    return [{ role: 'system', content: selectedLog.value.content.prompt }]
  }
})

function renderMarkdown(content: string | null | undefined) {
  if (!content) return ''
  return md.render(content)
}

function getRoleIcon(role: string) {
  switch (role.toLowerCase()) {
    case 'user': return User
    case 'assistant': return Bot
    case 'system': return Settings
    default: return MessageSquare
  }
}

function getRoleClass(role: string) {
  switch (role.toLowerCase()) {
    case 'user': return 'bg-blue-50 dark:bg-blue-900/20 border-blue-100 dark:border-blue-800'
    case 'assistant': return 'bg-green-50 dark:bg-green-900/20 border-green-100 dark:border-green-800'
    case 'system': return 'bg-gray-50 dark:bg-gray-900/50 border-gray-100 dark:border-gray-800'
    default: return 'bg-gray-50 dark:bg-gray-900/50 border-gray-100 dark:border-gray-800'
  }
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

function formatTime(timestamp: string) {
  return new Date(timestamp).toLocaleString()
}

function getStatusClass(code: number) {
  if (code >= 200 && code < 300) return 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
  if (code >= 400 && code < 500) return 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/30 dark:text-yellow-400'
  return 'bg-red-100 text-red-700 dark:bg-red-900/30 dark:text-red-400'
}

async function openDetail(log: Log) {
  try {
    refreshing.value = true
    const detail = await getLogDetail(log.id)
    selectedLog.value = detail
    isDetailView.value = true
    showRawResponse.value = false
  } catch (err) {
    console.error('Failed to fetch log detail:', err)
    ui.showToast('获取详情失败', 'error')
  } finally {
    refreshing.value = false
  }
}

function closeDetail() {
  isDetailView.value = false
  selectedLog.value = null
}

function copyToClipboard(text: string | null | undefined) {
  if (!text) return
  navigator.clipboard.writeText(text).then(() => {
    ui.showToast('已复制到剪贴板', 'success')
  })
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

function openInPlayground() {
  if (selectedLog.value) {
    playgroundStore.loadFromLog(selectedLog.value)
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
