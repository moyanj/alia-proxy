<template>
  <div class="h-[calc(100vh-10rem)] flex flex-col lg:flex-row gap-6">
    <!-- Configuration & Input Panel -->
    <div class="flex-1 flex flex-col gap-6 min-w-0">
      <!-- Top Bar: Model & Settings -->
      <div class="bg-white dark:bg-gray-800 p-4 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-wrap items-center gap-4">
        <div class="flex-1 min-w-[200px]">
          <label class="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1 block">选择模型</label>
          <div class="relative">
            <select v-model="store.model" 
              class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500 appearance-none">
              <option value="" disabled>请选择模型</option>
              <optgroup v-for="(modelsList, provider) in allModels" :key="provider" :label="provider">
                <option v-for="m in modelsList" :key="m.id || m" :value="`${provider}/${m.id || m}`">
                  {{ m.id || m }}
                </option>
              </optgroup>
            </select>
            <ChevronDown class="w-4 h-4 absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 pointer-events-none" />
          </div>
        </div>
        
        <div class="w-32">
          <label class="text-xs font-medium text-gray-500 uppercase tracking-wider mb-1 block">Temperature</label>
          <input v-model.number="store.temperature" type="number" step="0.1" min="0" max="2" 
            class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500" />
        </div>

        <div class="flex items-center gap-2 pt-5">
           <label class="flex items-center gap-2 cursor-pointer">
              <input v-model="store.stream" type="checkbox" class="w-4 h-4 text-blue-600 rounded focus:ring-blue-500" />
              <span class="text-sm font-medium text-gray-700 dark:text-gray-300">流式输出</span>
           </label>
        </div>
      </div>

      <!-- Chat Editor Area -->
      <div class="flex-1 bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col overflow-hidden">
        <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center bg-gray-50/50 dark:bg-gray-900/20">
          <div class="flex items-center gap-4">
             <button 
               @click="viewMode = 'visual'"
               :class="viewMode === 'visual' ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
               class="px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider transition-all flex items-center gap-2">
               <MessageSquare class="w-4 h-4" /> Visual
             </button>
             <button 
               @click="viewMode = 'json'"
               :class="viewMode === 'json' ? 'bg-white dark:bg-gray-700 text-blue-600 dark:text-blue-400 shadow-sm' : 'text-gray-500 hover:text-gray-700 dark:hover:text-gray-300'"
               class="px-3 py-1.5 rounded-lg text-xs font-bold uppercase tracking-wider transition-all flex items-center gap-2">
               <Code class="w-4 h-4" /> JSON
             </button>
          </div>
          <button @click="store.clearMessages" class="text-xs text-red-500 hover:text-red-600 font-bold uppercase tracking-wider flex items-center gap-1.5">
            <Trash2 class="w-4 h-4" /> 清空
          </button>
        </div>

        <div class="flex-1 overflow-y-auto p-6 bg-gray-50 dark:bg-gray-900/50 relative custom-scrollbar">
          
          <!-- Visual Mode -->
          <div v-if="viewMode === 'visual'" class="space-y-6 max-w-3xl mx-auto">
            <!-- System Prompt -->
            <div class="space-y-2">
              <div class="flex items-center gap-2 text-xs font-bold text-gray-500 uppercase tracking-wider">
                <Settings class="w-3.5 h-3.5" /> System Prompt
              </div>
              <textarea 
                v-model="store.systemPrompt"
                rows="3"
                class="w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4 text-sm outline-none focus:ring-2 focus:ring-blue-500/50 resize-none transition-shadow"
                placeholder="设定 AI 的行为模式..."
              ></textarea>
            </div>

            <div class="h-px bg-gray-200 dark:bg-gray-700/50 my-4"></div>

            <!-- Messages List -->
            <div v-for="(msg, idx) in store.messages" :key="idx" class="group relative flex gap-4 animate-in fade-in slide-in-from-bottom-2 duration-300">
              <div class="mt-2 shrink-0">
                <div :class="msg.role === 'user' ? 'bg-blue-100 text-blue-600 dark:bg-blue-900/30 dark:text-blue-400' : 'bg-green-100 text-green-600 dark:bg-green-900/30 dark:text-green-400'" 
                  class="w-8 h-8 rounded-lg flex items-center justify-center">
                  <User v-if="msg.role === 'user'" class="w-5 h-5" />
                  <Bot v-else class="w-5 h-5" />
                </div>
              </div>
              <div class="flex-1 space-y-2">
                <div class="flex justify-between items-center">
                   <select v-model="msg.role" class="bg-transparent text-xs font-bold uppercase tracking-wider text-gray-500 outline-none cursor-pointer hover:text-gray-800 dark:hover:text-gray-200">
                     <option value="user">User</option>
                     <option value="assistant">Assistant</option>
                   </select>
                   <button @click="store.removeMessage(idx)" class="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-500 transition-all">
                     <X class="w-4 h-4" />
                   </button>
                </div>
                <textarea 
                  v-model="msg.content"
                  rows="3"
                  class="w-full bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-xl p-4 text-sm outline-none focus:ring-2 focus:ring-blue-500/50 resize-y min-h-[80px] transition-shadow"
                  placeholder="输入内容..."
                ></textarea>
              </div>
            </div>

            <!-- Add Message Button -->
            <div class="flex justify-center pt-4">
              <button @click="store.addMessage('user')" 
                class="flex items-center gap-2 px-4 py-2 bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 rounded-full text-sm font-medium text-gray-600 dark:text-gray-300 hover:border-blue-500 hover:text-blue-500 transition-all shadow-sm">
                <Plus class="w-4 h-4" /> 添加消息
              </button>
            </div>
          </div>

          <!-- JSON Mode -->
          <div v-else class="h-full">
            <textarea 
              :value="jsonPreview"
              @input="updateFromJson"
              class="w-full h-full bg-gray-900 text-gray-300 font-mono text-sm p-4 rounded-xl border border-gray-700 focus:ring-2 focus:ring-blue-500 outline-none resize-none"
              spellcheck="false"
            ></textarea>
          </div>
        </div>

        <div class="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
          <button 
            @click="runTest" 
            :disabled="loading"
            class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl transition-all active:scale-[0.99] disabled:opacity-50 flex items-center justify-center gap-2 shadow-lg shadow-blue-500/20"
          >
            <Play v-if="!loading" class="w-5 h-5 fill-current" />
            <Loader2 v-else class="w-5 h-5 animate-spin" />
            {{ loading ? '运行中...' : '发送请求 (Send)' }}
          </button>
        </div>
      </div>
    </div>

    <!-- Output Panel -->
    <div class="flex-1 lg:max-w-md xl:max-w-lg bg-gray-900 rounded-xl border border-gray-700 shadow-2xl flex flex-col overflow-hidden">
      <div class="p-4 border-b border-gray-700 bg-gray-800/50 flex justify-between items-center">
        <h4 class="text-sm font-bold text-gray-400 uppercase tracking-wider flex items-center gap-2">
          <Terminal class="w-4 h-4" /> Output
        </h4>
        <div v-if="responseTime" class="text-[10px] text-gray-500 uppercase font-bold bg-gray-800 px-2 py-1 rounded">{{ responseTime }}ms</div>
      </div>
      
      <div class="flex-1 p-6 overflow-auto font-mono text-sm custom-scrollbar relative">
        <div v-if="error" class="text-red-400 bg-red-900/20 p-4 rounded-lg border border-red-900/50 mb-4 animate-in fade-in slide-in-from-top-2">
           <div class="flex items-center gap-2 mb-2 font-bold"><AlertCircle class="w-4 h-4" /> Error</div>
           {{ error }}
        </div>
        
        <div v-if="!output && !loading" class="absolute inset-0 flex flex-col items-center justify-center text-gray-600">
           <Command class="w-12 h-12 mb-4 opacity-20" />
           <p class="text-xs uppercase tracking-widest font-bold opacity-50">Ready to run</p>
        </div>

        <div v-else class="text-gray-300 whitespace-pre-wrap leading-relaxed">{{ output }}<span v-if="loading" class="inline-block w-2 h-4 bg-blue-500 ml-1 animate-pulse align-middle"></span></div>
      </div>

      <div class="p-3 border-t border-gray-700 bg-gray-800/50 flex justify-between items-center text-[10px] text-gray-500 font-bold">
        <div class="flex gap-4">
          <span :class="{'text-blue-400': status === 'PENDING', 'text-green-400': status === '200', 'text-red-400': status === 'ERROR'}">
             STATUS: {{ status || 'IDLE' }}
          </span>
          <span>TOKENS: {{ tokens || '0' }}</span>
        </div>
        <button @click="copyOutput" v-if="output" class="hover:text-white transition-colors">
           <Copy class="w-3.5 h-3.5" />
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, watch } from 'vue'
import { usePlaygroundStore } from '@/stores/playground'
import { useUIStore } from '@/stores/ui'
import { getAllModels } from '@/api'
import { 
  Play, Loader2, ChevronDown, MessageSquare, Code, 
  Trash2, Settings, User, Bot, X, Plus, Terminal,
  AlertCircle, Command, Copy
} from 'lucide-vue-next'
import axios from 'axios'

const store = usePlaygroundStore()
const ui = useUIStore()

const allModels = ref<Record<string, any[]>>({})
const loading = ref(false)
const output = ref('')
const status = ref('')
const error = ref('')
const tokens = ref(0)
const responseTime = ref(0)
const viewMode = ref<'visual' | 'json'>('visual')

const jsonPreview = computed(() => {
  const msgs = [
    { role: 'system', content: store.systemPrompt },
    ...store.messages
  ]
  return JSON.stringify(msgs, null, 2)
})

function updateFromJson(e: Event) {
  try {
    const val = (e.target as HTMLTextAreaElement).value
    const parsed = JSON.parse(val)
    if (Array.isArray(parsed)) {
      const systemMsg = parsed.find((m: any) => m.role === 'system')
      if (systemMsg) store.systemPrompt = systemMsg.content
      
      store.messages = parsed
        .filter((m: any) => m.role !== 'system')
        .map((m: any) => ({ role: m.role, content: m.content }))
    }
  } catch (err) {
    // Ignore parse errors while typing
  }
}

async function fetchModels() {
  try {
    allModels.value = await getAllModels()
    // Default model if not set
    if (!store.model) {
      const providers = Object.keys(allModels.value)
      if (providers.length > 0) {
        const firstProvider = providers[0]
        const models = (allModels.value as any)[firstProvider]
        if (Array.isArray(models) && models.length > 0) {
          store.model = `${firstProvider}/${models[0].id || models[0]}`
        }
      }
    }
  } catch (err) {
    console.error('Failed to fetch models:', err)
  }
}

async function runTest() {
  if (!store.model) return ui.showToast('请先选择模型', 'error')
  
  // Auto-add empty message if none
  if (store.messages.length === 0) {
     store.addMessage('user', '')
     return
  }

  loading.value = true
  output.value = ''
  error.value = ''
  status.value = 'PENDING'
  tokens.value = 0
  const start = Date.now()

  try {
    const messages = [
      { role: 'system', content: store.systemPrompt },
      ...store.messages
    ]
    
    if (store.stream) {
      // Use Fetch for streaming
      const response = await fetch('/v1/chat/completions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: store.model,
          messages,
          temperature: store.temperature,
          stream: true
        })
      })

      if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`)
      
      status.value = response.status.toString()
      const reader = response.body?.getReader()
      const decoder = new TextDecoder()

      while (reader) {
        const { value, done } = await reader.read()
        if (done) break
        
        const chunk = decoder.decode(value)
        const lines = chunk.split('\n').filter(line => line.trim() !== '')
        
        for (const line of lines) {
          if (line.includes('[DONE]')) continue
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              const content = data.choices[0]?.delta?.content || ''
              output.value += content
            } catch (e) {
              console.error('Error parsing stream chunk', e)
            }
          }
        }
      }
    } else {
      const res = await axios.post('/v1/chat/completions', {
        model: store.model,
        messages,
        temperature: store.temperature,
        stream: false
      })
      status.value = res.status.toString()
      output.value = res.data.choices[0].message.content
      tokens.value = res.data.usage?.total_tokens || 0
    }
  } catch (err: any) {
    error.value = err.message || '请求失败'
    status.value = 'ERROR'
  } finally {
    loading.value = false
    responseTime.value = Date.now() - start
  }
}

function copyOutput() {
  navigator.clipboard.writeText(output.value)
  ui.showToast('已复制到剪贴板', 'success')
}

onMounted(() => {
  fetchModels()
  if (store.messages.length === 0) {
    store.addMessage('user')
  }
})
</script>

<style scoped>
.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}
.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}
.custom-scrollbar::-webkit-scrollbar-thumb {
  background: rgba(156, 163, 175, 0.3);
  border-radius: 10px;
}
.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background: rgba(156, 163, 175, 0.5);
}
</style>
