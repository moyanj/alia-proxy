<template>
  <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 h-[calc(100vh-10rem)]">
    <!-- Configuration -->
    <div class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm flex flex-col overflow-hidden">
      <div class="p-4 border-b border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50">
        <h4 class="text-sm font-bold text-gray-900 dark:text-white uppercase tracking-wider">演练场配置</h4>
      </div>
      <div class="p-6 space-y-4 flex-1 overflow-auto">
        <div class="space-y-1.5">
          <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">选择模型 (provider/model)</label>
          <select v-model="form.model" class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500">
            <optgroup v-for="(modelsList, provider) in allModels" :key="provider" :label="provider">
              <option v-for="m in modelsList" :key="m.id || m" :value="`${provider}/${m.id || m}`">
                {{ m.id || m }}
              </option>
            </optgroup>
          </select>
        </div>

        <div class="space-y-1.5">
          <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">对话历史 (JSON)</label>
          <div class="relative group">
            <pre class="hidden">{{ messagesJson }}</pre>
            <textarea 
              v-model="messagesJson"
              rows="12"
              class="w-full bg-gray-900 text-gray-300 font-mono text-xs p-4 rounded-xl border border-gray-700 focus:ring-2 focus:ring-blue-500 outline-none"
            ></textarea>
            <button @click="resetMessages" class="absolute top-2 right-2 p-1 bg-gray-800 hover:bg-gray-700 text-gray-400 rounded transition-colors">
              <RotateCcw class="w-4 h-4" />
            </button>
          </div>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-1.5">
            <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">Temperature</label>
            <input v-model.number="form.temperature" type="number" step="0.1" min="0" max="2" class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm outline-none" />
          </div>
          <div class="space-y-1.5">
            <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">Stream</label>
            <div class="flex items-center h-9 px-3 bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg">
              <input v-model="form.stream" type="checkbox" class="w-4 h-4 text-blue-600 rounded" />
              <span class="ml-2 text-sm text-gray-600 dark:text-gray-400">开启流式输出</span>
            </div>
          </div>
        </div>
      </div>
      <div class="p-6 border-t border-gray-200 dark:border-gray-700">
        <button 
          @click="runTest" 
          :disabled="loading"
          class="w-full bg-blue-600 hover:bg-blue-700 text-white font-bold py-3 rounded-xl transition-all active:scale-95 disabled:opacity-50 flex items-center justify-center gap-2"
        >
          <Play v-if="!loading" class="w-5 h-5" />
          <Loader2 v-else class="w-5 h-5 animate-spin" />
          {{ loading ? '运行中...' : '发送请求' }}
        </button>
      </div>
    </div>

    <!-- Output -->
    <div class="bg-gray-900 rounded-xl border border-gray-700 shadow-2xl flex flex-col overflow-hidden">
      <div class="p-4 border-b border-gray-700 bg-gray-800/50 flex justify-between items-center">
        <h4 class="text-sm font-bold text-gray-400 uppercase tracking-wider">输出响应</h4>
        <div v-if="responseTime" class="text-[10px] text-gray-500 uppercase font-bold">{{ responseTime }}ms</div>
      </div>
      <div class="flex-1 p-6 overflow-auto font-mono text-sm">
        <div v-if="error" class="text-red-400 bg-red-900/20 p-4 rounded-lg border border-red-900/50 mb-4">
           {{ error }}
        </div>
        <div class="text-gray-300 whitespace-pre-wrap">{{ output || '等待发送请求...' }}</div>
      </div>
      <div class="p-4 border-t border-gray-700 bg-gray-800/50 flex justify-between items-center text-[10px] text-gray-500 font-bold">
        <span>STATUS: {{ status || 'IDLE' }}</span>
        <span>TOKEN: {{ tokens || '0' }}</span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useUIStore } from '@/stores/ui'
import { getAllModels } from '@/api'
import { Play, RotateCcw, Loader2 } from 'lucide-vue-next'
import axios from 'axios'

const ui = useUIStore()
const allModels = ref<Record<string, any[]>>({})
const loading = ref(false)
const output = ref('')
const status = ref('')
const error = ref('')
const tokens = ref(0)
const responseTime = ref(0)

const messagesJson = ref(JSON.stringify([
  { role: "user", content: "你好！请做一个自我介绍。" }
], null, 2))

const form = reactive({
  model: '',
  temperature: 0.7,
  stream: false
})

async function fetchModels() {
  try {
    allModels.value = await getAllModels()
    // Default to first available model
    const providers = Object.keys(allModels.value)
    if (providers.length > 0) {
      const firstProvider = providers[0]
      if (firstProvider) {
        const models = (allModels.value as any)[firstProvider]
        if (Array.isArray(models) && models.length > 0) {
          form.model = `${firstProvider}/${models[0].id || models[0]}`
        }
      }
    }
  } catch (err) {
    console.error('Failed to fetch models:', err)
  }
}

function resetMessages() {
  messagesJson.value = JSON.stringify([
    { role: "user", content: "你好！请做一个自我介绍。" }
  ], null, 2)
}

async function runTest() {
  loading.value = true
  output.value = ''
  error.value = ''
  status.value = 'PENDING'
  tokens.value = 0
  const start = Date.now()

  try {
    const messages = JSON.parse(messagesJson.value)
    
    if (form.stream) {
      // Use Fetch for streaming
      const response = await fetch('/v1/chat/completions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: form.model,
          messages,
          temperature: form.temperature,
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
        model: form.model,
        messages,
        temperature: form.temperature,
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

onMounted(() => {
  fetchModels()
})
</script>
