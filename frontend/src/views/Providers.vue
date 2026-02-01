<template>
  <div class="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
    <!-- Header with Actions -->
    <div class="flex justify-between items-center mb-8">
      <div>
        <h3 class="text-xl font-bold text-gray-900 dark:text-white">配置的提供商</h3>
        <p class="text-xs text-gray-500">管理您的 AI 模型提供商及其 API 密钥池。</p>
      </div>
      <div class="flex gap-2">
        <button @click="openAddModal" class="win-btn-primary flex items-center gap-2">
          <Plus class="w-4 h-4" /> 添加提供商
        </button>
        <button @click="fetchAll" class="px-4 py-1.5 bg-black/5 dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-md text-sm font-medium hover:bg-black/10 transition-colors">
          刷新
        </button>
      </div>
    </div>

    <!-- Provider List in Windows Settings Style -->
    <div class="space-y-2">
      <div v-for="(config, name) in providers" :key="name" 
        class="win-card px-6 py-4 flex items-center justify-between win-card-hover group transition-all"
      >
        <div class="flex items-center gap-6">
          <div class="w-12 h-12 rounded-xl bg-blue-500/10 flex items-center justify-center text-blue-600 shrink-0">
             <Cloud class="w-6 h-6" />
          </div>
          <div class="flex flex-col">
            <div class="flex items-center gap-2">
              <span class="text-[15px] font-bold text-gray-900 dark:text-white">{{ name }}</span>
              <span class="px-1.5 py-0.5 rounded bg-black/5 dark:bg-white/10 text-[10px] font-bold text-gray-500 uppercase tracking-tighter border border-black/5">
                {{ config.type }}
              </span>
            </div>
            <div class="flex items-center gap-3 mt-1">
               <div class="flex items-center gap-1.5">
                  <div class="w-1.5 h-1.5 rounded-full" :class="healthStatus[name] === 'healthy' ? 'bg-green-500' : 'bg-red-500'"></div>
                  <span class="text-[11px] font-bold uppercase tracking-tight" :class="healthStatus[name] === 'healthy' ? 'text-green-600' : 'text-red-600'">
                    {{ healthStatus[name] === 'healthy' ? 'Healthy' : (healthStatus[name] || 'Unknown') }}
                  </span>
               </div>
               <span class="text-[11px] text-gray-400 font-medium truncate max-w-[200px]">{{ config.base_url || 'Default Endpoint' }}</span>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-4">
           <div class="flex -space-x-2 overflow-hidden mr-4">
               <div v-for="(m, idx) in (models[name] || []).slice(0, 3)" :key="typeof m === 'string' ? m : m.id || idx" class="inline-block h-6 w-6 rounded-full ring-2 ring-white dark:ring-[#2d2d2d] bg-gray-100 dark:bg-gray-700 flex items-center justify-center">
                  <span class="text-[8px] font-bold text-gray-500 uppercase truncate px-0.5">{{ (typeof m === 'string' ? m : m.id || '?').split('-')[0] }}</span>
               </div>
              <div v-if="(models[name]?.length || 0) > 3" class="inline-block h-6 w-6 rounded-full ring-2 ring-white dark:ring-[#2d2d2d] bg-gray-200 dark:bg-gray-800 flex items-center justify-center">
                 <span class="text-[8px] font-bold text-gray-500">+{{ (models[name]?.length || 0) - 3 }}</span>
              </div>
           </div>

            <div class="flex items-center gap-1">
               <button @click="fetchModelsForProvider(name)" class="p-2 hover:bg-black/5 dark:hover:bg-white/5 rounded-md text-gray-500" title="查看模型">
                  <LayoutGrid class="w-4 h-4" />
               </button>
               <button @click="openEditModal(name, config)" class="p-2 hover:bg-black/5 dark:hover:bg-white/5 rounded-md text-gray-500" title="编辑">
                  <Settings class="w-4 h-4" />
               </button>
               <button @click="deleteProvider(name)" class="p-2 hover:bg-red-500/10 hover:text-red-500 rounded-md transition-colors" title="删除">
                  <Trash2 class="w-4 h-4" />
               </button>
            </div>
        </div>
      </div>

      <div v-if="Object.keys(providers).length === 0" class="py-24 win-card flex flex-col items-center justify-center text-gray-400 border-dashed">
         <CloudOff class="w-12 h-12 mb-4 opacity-20" />
         <p class="text-sm font-bold uppercase tracking-widest">未配置提供商</p>
         <button @click="openAddModal" class="mt-4 text-blue-600 dark:text-blue-400 font-bold hover:underline">点击立即添加</button>
      </div>
    </div>

    <!-- Models Dialog -->
    <div v-if="showModelsModal" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
       <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="showModelsModal = false"></div>
       <div class="win-card w-full max-w-lg shadow-2xl animate-in zoom-in-95 duration-200 flex flex-col overflow-hidden relative z-10">
          <header class="p-6 border-b border-black/5 dark:border-white/5 flex items-center justify-between">
             <div>
                <h4 class="text-lg font-bold">{{ activeModelsProvider }} 模型列表</h4>
                <p class="text-xs text-gray-500">此提供商支持的所有模型。</p>
             </div>
             <button @click="showModelsModal = false" class="p-2 hover:bg-black/5 rounded-full transition-colors">
                <X class="w-5 h-5" />
             </button>
          </header>
          <div class="p-4 bg-black/[0.01]">
             <div class="relative group">
                <Search class="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 group-focus-within:text-blue-500" />
                <input v-model="modelSearchQuery" type="text" placeholder="搜索模型名称..."
                  class="w-full bg-white dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-md pl-10 pr-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500/50" />
             </div>
          </div>
          <div class="flex-1 overflow-y-auto max-h-[400px] p-4 custom-scrollbar space-y-2">
             <div v-for="m in filteredModels" :key="m" class="flex items-center justify-between p-3 rounded-lg bg-black/[0.02] dark:bg-white/[0.02] border border-black/5 dark:border-white/5 group">
                <span class="text-sm font-mono font-medium">{{ m }}</span>
                <button @click="copyToClipboard(m)" class="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-blue-500/10 text-blue-500 rounded transition-all">
                   <Copy class="w-3.5 h-3.5" />
                </button>
             </div>
             <div v-if="filteredModels.length === 0" class="py-12 text-center text-gray-400 italic text-sm">
                未找到匹配模型
             </div>
          </div>
          <footer class="p-4 border-t border-black/5 bg-black/[0.01] flex justify-end">
             <button @click="showModelsModal = false" class="px-6 py-1.5 bg-black/5 hover:bg-black/10 rounded-md text-sm font-bold transition-colors">
                关闭
             </button>
          </footer>
       </div>
    </div>

    <!-- Edit/Add Modal (Full Dialog Style) -->
    <div v-if="editingProvider" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
       <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="editingProvider = null"></div>
       <div class="win-card w-full max-w-2xl shadow-2xl animate-in zoom-in-95 duration-200 flex flex-col overflow-hidden relative z-10">
          <header class="p-6 border-b border-black/5 dark:border-white/5 flex items-center justify-between">
             <h4 class="text-lg font-bold">{{ isAdding ? '添加新提供商' : `编辑 ${editingProvider}` }}</h4>
             <button @click="editingProvider = null" class="p-2 hover:bg-black/5 rounded-full transition-colors">
                <X class="w-5 h-5" />
             </button>
          </header>

          <div class="p-8 overflow-y-auto max-h-[70vh] custom-scrollbar space-y-6">
             <div class="grid grid-cols-2 gap-6">
                <div class="space-y-1.5">
                   <label class="text-[11px] font-bold text-gray-500 uppercase tracking-widest ml-1">提供商标识 (ID)</label>
                   <input v-model="editForm.name" :disabled="!isAdding" type="text" placeholder="openai-primary"
                     class="w-full bg-white dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-md px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500/50 disabled:opacity-50" />
                </div>
                <div class="space-y-1.5">
                   <label class="text-[11px] font-bold text-gray-500 uppercase tracking-widest ml-1">接口类型</label>
                   <div class="relative">
                      <select v-model="editForm.type"
                        class="w-full bg-white dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-md px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500/50 appearance-none capitalize">
                        <option v-for="t in providerTypes" :key="t" :value="t">{{ t }}</option>
                      </select>
                      <ChevronDown class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                   </div>
                </div>
             </div>

             <div class="space-y-1.5">
                <label class="text-[11px] font-bold text-gray-500 uppercase tracking-widest ml-1">基础地址 (Base URL)</label>
                <input v-model="editForm.base_url" type="text" placeholder="https://api.openai.com/v1"
                  class="w-full bg-white dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-md px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500/50 font-mono" />
             </div>

             <div class="space-y-1.5">
                <label class="text-[11px] font-bold text-gray-500 uppercase tracking-widest ml-1">API Key 池 (逗号分隔)</label>
                <textarea v-model="editForm.api_key" placeholder="sk-..., sk-..."
                  class="w-full bg-white dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-md px-4 py-3 text-xs outline-none focus:ring-2 focus:ring-blue-500/50 font-mono min-h-[100px] resize-none"></textarea>
             </div>

             <div class="grid grid-cols-2 gap-6">
                <div class="space-y-1.5">
                   <label class="text-[11px] font-bold text-gray-500 uppercase tracking-widest ml-1">超时设置 (秒)</label>
                   <input v-model.number="editForm.timeout" type="number"
                     class="w-full bg-white dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-md px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500/50" />
                </div>
                <div class="space-y-1.5">
                   <label class="text-[11px] font-bold text-gray-500 uppercase tracking-widest ml-1">额外配置 (JSON)</label>
                   <input v-model="editForm.extra" placeholder='{"proxy": "http://..."}'
                     class="w-full bg-white dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-md px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500/50 font-mono" />
                </div>
             </div>
          </div>

          <footer class="p-6 border-t border-black/5 bg-black/[0.01] flex justify-end gap-3">
             <button @click="editingProvider = null" class="px-6 py-2 bg-black/5 hover:bg-black/10 rounded-md text-sm font-bold transition-colors">
                取消
             </button>
             <button @click="saveProvider" class="win-btn-primary px-8">
                保存配置
             </button>
          </footer>
       </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive, computed } from 'vue'
import { useUIStore } from '@/stores/ui'
import {
  getConfig,
  getHealth,
  getAllModels,
  getProviderTypes,
  updateConfig,
  type ProviderConfig
} from '@/api'
import { 
   Cloud, Plus, X, ChevronDown, Copy, AlertCircle, 
   Search, LayoutGrid, Settings, Trash2, CloudOff 
} from 'lucide-vue-next'

const ui = useUIStore()
const providers = ref<Record<string, ProviderConfig>>({})
const healthStatus = ref<Record<string, string>>({})
const models = ref<Record<string, any>>({})
const providerTypes = ref<string[]>([])

const editingProvider = ref<string | null>(null)
const isAdding = ref(false)
const showModelsModal = ref(false)
const activeModelsProvider = ref('')
const modelSearchQuery = ref('')

const filteredModels = computed(() => {
  const list = models.value[activeModelsProvider.value] || []
  if (Array.isArray(list)) {
    return list.map(m => m.id || m).filter(id => {
      return String(id).toLowerCase().includes(modelSearchQuery.value.toLowerCase())
    })
  }
  return []
})

const editForm = reactive({
  name: '',
  type: 'openai',
  base_url: '',
  api_key: '',
  timeout: 60.0,
  extra: ''
})

async function fetchAll() {
  try {
    const [configData, healthData, modelsData, typesData] = await Promise.all([
      getConfig(),
      getHealth(),
      getAllModels(),
      getProviderTypes()
    ])
    providers.value = configData.providers || {}
    healthStatus.value = healthData.providers || {}
    models.value = modelsData || {}
    providerTypes.value = typesData || []
  } catch (err) {
    console.error('Failed to fetch providers info:', err)
  }
}

function openAddModal() {
  isAdding.value = true
  editForm.name = ''
  editForm.type = 'openai'
  editForm.base_url = ''
  editForm.api_key = ''
  editForm.timeout = 60.0
  editForm.extra = ''
  editingProvider.value = 'new'
}

function openEditModal(name: string, config: any) {
  isAdding.value = false
  editForm.name = name
  editForm.type = config.type
  editForm.base_url = config.base_url || ''

  if (Array.isArray(config.api_key)) {
    editForm.api_key = config.api_key.join(', ')
  } else {
    editForm.api_key = config.api_key || ''
  }

  editForm.timeout = config.timeout || 60.0

  const { type, base_url, api_key, timeout, ...rest } = config
  editForm.extra = Object.keys(rest).length > 0 ? JSON.stringify(rest) : ''

  editingProvider.value = name
}

async function saveProvider() {
  if (!editForm.name) return ui.showToast('请填写提供商名称', 'error')

  const config = await getConfig()
  if (!config.providers) config.providers = {}

  let apiKey: string | string[] | undefined = editForm.api_key || undefined
  if (apiKey && apiKey.includes(',')) {
    apiKey = apiKey.split(',').map(k => k.trim()).filter(k => k)
  }

  const providerData: any = {
    type: editForm.type,
    base_url: editForm.base_url || undefined,
    api_key: apiKey,
    timeout: editForm.timeout
  }

  if (editForm.extra) {
    try {
      const extraData = JSON.parse(editForm.extra)
      Object.assign(providerData, extraData)
    } catch (e) {
      return ui.showToast('额外配置 JSON 格式错误', 'error')
    }
  }

  config.providers[editForm.name] = providerData

  try {
    await updateConfig(config)
    ui.showToast('配置保存成功', 'success')
    editingProvider.value = null
    fetchAll()
  } catch (err) {
    ui.showToast('保存失败', 'error')
  }
}

async function deleteProvider(name: string) {
  if (await ui.confirm('确认删除', `确定要删除提供商 ${name} 吗？`)) {
    const config = await getConfig()
    delete config.providers[name]
    try {
      await updateConfig(config)
      ui.showToast('提供商已删除', 'success')
      fetchAll()
    } catch (err) {
      ui.showToast('删除失败', 'error')
    }
  }
}

async function fetchModelsForProvider(name: string) {
  activeModelsProvider.value = name
  modelSearchQuery.value = ''
  showModelsModal.value = true
}

function copyToClipboard(text: string) {
  navigator.clipboard.writeText(text)
  ui.showToast('已复制到剪贴板', 'success')
}

onMounted(() => {
  fetchAll()
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
