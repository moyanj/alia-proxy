<template>
  <div class="h-[calc(100vh-10rem)] flex flex-col lg:flex-row gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
    <!-- Configuration & Input Panel -->
    <div class="flex-1 flex flex-col gap-6 min-w-0">
      <!-- Top Bar: Model & Settings -->
      <div class="win-card p-4 flex flex-wrap items-center gap-6">
        <div class="flex-1 min-w-[240px] space-y-1.5">
          <label class="text-[11px] font-bold text-gray-500 uppercase tracking-widest ml-1">选择模型 (映射或原始)</label>
          <div class="relative">
            <select v-model="store.model" 
              class="w-full bg-white dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-md px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500/50 appearance-none font-medium">
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
        
        <div class="w-32 space-y-1.5">
          <label class="text-[11px] font-bold text-gray-500 uppercase tracking-widest ml-1">Temperature</label>
          <input v-model.number="store.temperature" type="number" step="0.1" min="0" max="2" 
            class="w-full bg-white dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-md px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500/50 font-mono" />
        </div>

        <div class="flex items-center gap-3 pt-5">
           <label class="relative inline-flex items-center cursor-pointer group">
              <input v-model="store.stream" type="checkbox" class="sr-only peer" />
              <div class="w-10 h-5 bg-gray-200 peer-focus:outline-none rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-blue-600 transition-colors"></div>
              <span class="ml-2 text-xs font-bold text-gray-500 group-hover:text-blue-500 transition-colors uppercase tracking-widest">流式</span>
           </label>
        </div>
      </div>

      <!-- Chat Editor Area -->
      <div class="flex-1 win-card flex flex-col overflow-hidden">
        <header class="p-4 border-b border-black/5 dark:border-white/5 flex justify-between items-center bg-black/[0.01] dark:bg-white/[0.01]">
          <div class="flex items-center gap-2">
             <button 
               @click="viewMode = 'visual'"
               :class="viewMode === 'visual' ? 'bg-blue-500 text-white shadow-md shadow-blue-500/20' : 'text-gray-500 hover:bg-black/5 dark:hover:bg-white/5'"
               class="px-4 py-1.5 rounded text-[11px] font-bold uppercase tracking-widest transition-all"
             >
               可视化
             </button>
             <button 
               @click="viewMode = 'json'"
               :class="viewMode === 'json' ? 'bg-blue-500 text-white shadow-md shadow-blue-500/20' : 'text-gray-500 hover:bg-black/5 dark:hover:bg-white/5'"
               class="px-4 py-1.5 rounded text-[11px] font-bold uppercase tracking-widest transition-all"
             >
               JSON
             </button>
          </div>
          <button @click="store.clearMessages" class="text-[11px] text-red-500 hover:text-red-400 font-bold uppercase tracking-widest flex items-center gap-1.5">
            <Trash2 class="w-4 h-4" /> 清空会话
          </button>
        </header>

        <div class="flex-1 overflow-y-auto p-8 custom-scrollbar relative bg-[#fafafa] dark:bg-[#1a1a1a]/50">
          
          <!-- Visual Mode -->
          <div v-if="viewMode === 'visual'" class="space-y-10 max-w-3xl mx-auto pb-12">
            <!-- System Prompt Section -->
            <div class="space-y-3">
              <div class="flex items-center gap-2 text-[10px] font-bold text-gray-400 uppercase tracking-widest">
                <Settings class="w-3.5 h-3.5" /> System Persona
              </div>
              <textarea 
                v-model="store.systemPrompt"
                rows="3"
                class="w-full bg-white dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-xl p-5 text-sm outline-none focus:ring-2 focus:ring-blue-500/50 resize-none transition-all shadow-sm"
                placeholder="设定 AI 的身份和行为准则..."
              ></textarea>
            </div>

            <!-- Messages List -->
            <div class="space-y-8">
               <div v-for="(msg, idx) in store.messages" :key="idx" class="group relative flex gap-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
                 <!-- Role Icon -->
                 <div class="shrink-0 mt-1">
                   <div 
                     :class="msg.role === 'user' ? 'bg-blue-600 text-white shadow-lg shadow-blue-500/30' : 'bg-purple-600 text-white shadow-lg shadow-purple-500/30'" 
                     class="w-9 h-9 rounded-xl flex items-center justify-center transition-transform group-hover:scale-110"
                   >
                     <User v-if="msg.role === 'user'" class="w-5 h-5" />
                     <Bot v-else class="w-5 h-5" />
                   </div>
                 </div>

                 <!-- Content Area -->
                 <div class="flex-1 space-y-2">
                   <div class="flex justify-between items-center px-1">
                      <select v-model="msg.role" class="bg-transparent text-[11px] font-bold uppercase tracking-widest text-gray-400 outline-none cursor-pointer hover:text-blue-500 transition-colors">
                        <option value="user">User</option>
                        <option value="assistant">Assistant</option>
                      </select>
                      <button @click="store.removeMessage(idx)" class="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-red-500/10 text-gray-300 hover:text-red-500 transition-all rounded">
                        <Trash2 class="w-4 h-4" />
                      </button>
                   </div>
                   <textarea 
                     v-model="msg.content"
                     rows="3"
                     class="w-full bg-white dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-2xl p-5 text-sm outline-none focus:ring-2 focus:ring-blue-500/50 resize-y min-h-[100px] transition-all shadow-sm group-hover:shadow-md"
                     placeholder="输入消息内容..."
                   ></textarea>
                 </div>
               </div>
            </div>

            <!-- Add Message Button -->
            <div class="flex justify-center">
              <button @click="store.addMessage('user')" 
                class="flex items-center gap-2 px-6 py-2.5 bg-white dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-full text-[12px] font-bold text-gray-600 dark:text-gray-300 hover:border-blue-500 hover:text-blue-500 transition-all shadow-sm hover:shadow-md active:scale-95"
              >
                <Plus class="w-4 h-4" /> 新增消息行
              </button>
            </div>
          </div>

          <!-- JSON Mode -->
          <div v-else class="h-full">
            <textarea 
              :value="jsonPreview"
              @input="updateFromJson"
              class="w-full h-full bg-[#1e1e1e] text-[#d4d4d4] font-mono text-sm p-8 rounded-2xl border border-black/10 focus:ring-2 focus:ring-blue-500/50 outline-none resize-none shadow-2xl"
              spellcheck="false"
            ></textarea>
          </div>
        </div>

        <!-- Action Footer -->
        <footer class="p-6 border-t border-black/5 dark:border-white/5 bg-white dark:bg-[#1a1a1a]">
          <button 
            @click="runTest" 
            :disabled="loading"
            class="win-btn-primary w-full py-4 rounded-xl flex items-center justify-center gap-3 text-[15px] font-bold tracking-tight shadow-xl shadow-blue-500/20 active:scale-[0.99] disabled:opacity-50 transition-all"
          >
            <Play v-if="!loading" class="w-5 h-5" />
            <Loader2 v-else class="w-5 h-5 animate-spin" />
            {{ loading ? '模型正在响应中...' : '提交请求并生成响应' }}
          </button>
        </footer>
      </div>
    </div>

    <!-- Output Panel -->
    <div class="flex-1 lg:max-w-md xl:max-w-xl flex flex-col min-w-0">
      <div class="win-card flex-1 flex flex-col overflow-hidden bg-[#1e1e1e] border-none shadow-2xl">
         <header class="h-14 border-b border-white/5 px-6 flex justify-between items-center shrink-0">
            <div class="flex items-center gap-3">
               <Terminal class="w-4 h-4 text-blue-400" />
               <h4 class="text-[11px] font-bold text-gray-400 uppercase tracking-widest">终端输出 (Terminal)</h4>
            </div>
            <div v-if="responseTime" class="text-[10px] font-bold bg-white/5 text-gray-400 px-2 py-1 rounded uppercase tracking-tighter">
               {{ responseTime }}ms
            </div>
         </header>
         
         <div class="flex-1 p-8 overflow-y-auto custom-scrollbar-dark relative">
            <div v-if="error" class="mb-6 animate-in slide-in-from-top-4 duration-300">
               <div class="flex items-center gap-2 text-red-500 mb-2">
                  <AlertCircle class="w-5 h-5" />
                  <span class="text-xs font-bold uppercase tracking-widest">Request Failed</span>
               </div>
               <div class="p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 text-sm font-mono whitespace-pre-wrap leading-relaxed">
                  {{ error }}
               </div>
            </div>

            <div v-if="!output && !loading && !error" class="absolute inset-0 flex flex-col items-center justify-center opacity-20 select-none">
               <Activity class="w-16 h-16 mb-6 text-white animate-pulse" />
               <p class="text-[11px] font-bold text-white uppercase tracking-[0.3em]">Waiting for interaction</p>
            </div>

            <div class="text-gray-100 font-mono text-[13px] leading-relaxed whitespace-pre-wrap selection:bg-blue-500/30">
               {{ output }}<span v-if="loading" class="inline-block w-2 h-4 bg-blue-500 ml-1 animate-pulse align-middle"></span>
            </div>
         </div>

         <footer class="h-14 border-t border-white/5 px-6 flex justify-between items-center shrink-0 bg-black/20">
            <div class="flex items-center gap-6">
               <div class="flex flex-col">
                  <span class="text-[9px] font-bold text-gray-500 uppercase tracking-tighter">Status</span>
                  <span :class="{'text-blue-400': status === 'PENDING', 'text-green-400': status === '200', 'text-red-400': status === 'ERROR'}" class="text-[11px] font-bold font-mono">
                     {{ status || 'IDLE' }}
                  </span>
               </div>
               <div class="flex flex-col border-l border-white/5 pl-6">
                  <span class="text-[9px] font-bold text-gray-500 uppercase tracking-tighter">Usage</span>
                  <span class="text-[11px] font-bold font-mono text-gray-300">{{ tokens }} TOKENS</span>
               </div>
            </div>
            
            <button v-if="output" @click="copyOutput" class="p-2 hover:bg-white/10 rounded-md text-gray-400 transition-colors" title="Copy Output">
               <Copy class="w-4 h-4" />
            </button>
         </footer>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue'
import { usePlaygroundStore } from '@/stores/playground'
import { useUIStore } from '@/stores/ui'
import { getAllModels } from '@/api'
import { 
  Play, Loader2, ChevronDown, Trash2, Settings, User, Bot, Plus, Terminal,
  AlertCircle, Copy, Activity, X
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
  } catch (err) { }
}

async function fetchModels() {
  try {
    allModels.value = await getAllModels()
    if (!store.model) {
      const providers = Object.keys(allModels.value)
      if (providers.length > 0) {
        const firstProvider = providers[0]!
        const models = allModels.value[firstProvider]
        if (Array.isArray(models) && models.length > 0) {
          store.model = `${firstProvider}/${models[0].id || models[0]}`
        }
      }
    }
  } catch (err) { }
}

async function runTest() {
  if (!store.model) return ui.showToast('请先选择模型', 'error')
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
            } catch (e) { }
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
  ui.showToast('已复制', 'success')
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

.custom-scrollbar-dark::-webkit-scrollbar {
  width: 4px;
}
.custom-scrollbar-dark::-webkit-scrollbar-thumb {
  background: rgba(255, 255, 255, 0.1);
  border-radius: 10px;
}
</style>
