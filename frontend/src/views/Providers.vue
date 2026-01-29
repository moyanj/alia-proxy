<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h3 class="text-xl font-bold text-gray-900 dark:text-white">配置的提供商</h3>
      <div class="flex gap-2">
        <button @click="openAddModal"
          class="text-sm bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2">
          <Plus class="w-4 h-4" /> 添加提供商
        </button>
        <button @click="fetchAll"
          class="text-sm bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">刷新状态</button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div v-for="(config, name) in providers" :key="name"
        class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden flex flex-col">

        <div class="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-start">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
              <Cloud class="w-6 h-6 text-gray-600 dark:text-gray-400" />
            </div>
            <div>
              <h4 class="text-lg font-bold text-gray-900 dark:text-white">{{ name }}</h4>
              <span
                class="text-[10px] font-black px-2 py-0.5 bg-blue-500/10 text-blue-600 dark:bg-blue-500/20 dark:text-blue-400 rounded-md uppercase tracking-widest border border-blue-500/10">{{
                  config.type }}</span>
            </div>
          </div>
          <div class="flex flex-col items-end gap-2">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full animate-pulse"
                :class="healthStatus[name] === 'healthy' ? 'bg-green-500 shadow-[0_0_8px_rgba(34,197,94,0.5)]' : 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.5)]'"></div>
              <span class="text-xs font-bold text-gray-500 dark:text-gray-400">{{ healthStatus[name] || 'Checking...' }}</span>
            </div>
            <button @click="openEditModal(name, config)"
              class="text-xs font-bold text-blue-600 dark:text-blue-400 hover:underline">编辑配置</button>
          </div>
        </div>

        <div class="p-6 space-y-4 flex-1">
          <div class="grid grid-cols-1 gap-4">
            <div v-if="config.base_url" class="space-y-1.5">
              <p class="text-[10px] uppercase font-black text-gray-400 tracking-wider">Base URL</p>
              <p
                class="text-sm font-mono truncate bg-gray-50 dark:bg-gray-900/50 p-2.5 rounded-lg border border-gray-100 dark:border-gray-700/50">
                {{ config.base_url }}</p>
            </div>
            <div v-if="config.api_key" class="space-y-1.5">
              <p class="text-[10px] uppercase font-black text-gray-400 tracking-wider">API Key</p>
              <p
                class="text-sm font-mono bg-gray-50 dark:bg-gray-900/50 p-2.5 rounded-lg border border-gray-100 dark:border-gray-700/50 break-all">
                {{ Array.isArray(config.api_key) ? config.api_key.join(', ') : config.api_key }}
              </p>
            </div>
            <div v-if="config.timeout" class="space-y-1.5">
              <p class="text-[10px] uppercase font-black text-gray-400 tracking-wider">Timeout</p>
              <p
                class="text-sm font-mono bg-gray-50 dark:bg-gray-900/50 p-2.5 rounded-lg border border-gray-100 dark:border-gray-700/50">
                {{ config.timeout }}s</p>
            </div>
          </div>
        </div>

        <div class="pb-6 space-y-3 px-6">
          <p class="text-[10px] uppercase font-black text-gray-400 tracking-wider flex justify-between items-center">
            支持的模型
            <button @click="fetchModelsForProvider(name)" class="text-blue-500 hover:underline">查看全部</button>
          </p>
          <div class="flex flex-wrap gap-2">
            <span v-for="m in (models[name] || []).slice(0, 5)" :key="(m as any).id"
              class="px-2.5 py-1 bg-gray-100 dark:bg-gray-700/50 text-gray-600 dark:text-gray-300 text-[10px] rounded-md font-bold border border-gray-200/50 dark:border-gray-600/30">
              {{ (m as any).id || m }}
            </span>
            <span v-if="(models[name]?.length || 0) > 5" class="px-2.5 py-1 text-gray-400 text-[10px] font-bold">
              +{{ (models[name]?.length || 0) - 5 }} more
            </span>
            <span v-if="!models[name]" class="text-xs text-gray-400 italic">点击刷新获取列表</span>
          </div>
        </div>

        <div
          class="p-4 px-6 bg-gray-50/50 dark:bg-gray-900/30 border-t border-gray-200 dark:border-gray-700 flex justify-between items-center mt-auto">
          <button @click="testProvider(name)"
            class="text-xs font-black text-blue-600 dark:text-blue-400 hover:text-blue-500 transition-colors uppercase tracking-widest">测试连接</button>
          <button @click="deleteProvider(name)"
            class="text-xs font-black text-red-500 hover:text-red-400 transition-colors uppercase tracking-widest">删除</button>
        </div>
      </div>
    </div>

    <!-- Detail Models Modal -->
    <div v-if="showModelsModal"
      class="fixed inset-0 z-[60] flex items-center justify-center p-4 bg-black/60 backdrop-blur-sm">
      <div
        class="bg-white dark:bg-gray-800 w-full max-w-lg rounded-xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in duration-200">
        <div
          class="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center bg-gray-50/50 dark:bg-gray-900/20">
          <div class="flex-1">
            <h3 class="text-xl font-bold text-gray-900 dark:text-white">{{ activeModelsProvider }} 支持的模型</h3>
            <div class="mt-3 relative">
              <Search class="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" />
              <input v-model="modelSearchQuery" type="text" placeholder="搜索模型名称..."
                class="w-full bg-white dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-xl pl-9 pr-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500/50 transition-all" />
            </div>
          </div>
          <button @click="showModelsModal = false"
            class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors text-gray-500 ml-4">
            <X class="w-6 h-6" />
          </button>
        </div>
        <div class="p-4 overflow-y-auto max-h-[60vh] bg-gray-50/30 dark:bg-black/10 custom-scrollbar">
          <div v-if="filteredModels.length > 0" class="grid grid-cols-1 gap-2">
            <div v-for="m in filteredModels" :key="(m as any).id || m"
              class="flex items-center justify-between p-3 bg-white dark:bg-gray-800 rounded-xl border border-gray-100 dark:border-gray-700 shadow-sm hover:border-blue-500/50 transition-colors group">
              <span class="text-sm font-mono text-gray-700 dark:text-gray-300">{{ (m as any).id || m }}</span>
              <div class="flex items-center gap-2">
                <span v-if="(m as any).owned_by"
                  class="text-[10px] bg-gray-100 dark:bg-gray-700 px-1.5 py-0.5 rounded text-gray-500 uppercase font-bold">{{
                    (m as any).owned_by }}</span>
                <button @click="copyToClipboard((m as any).id || m)"
                  class="opacity-0 group-hover:opacity-100 p-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded text-blue-500 transition-all">
                  <Copy class="w-4 h-4" />
                </button>
              </div>
            </div>
          </div>
          <div v-else-if="models[activeModelsProvider]?.error" class="p-8 text-center">
            <AlertCircle class="w-12 h-12 text-red-500 mx-auto mb-3 opacity-50" />
            <p class="text-sm text-red-500 font-medium">{{ models[activeModelsProvider].error }}</p>
          </div>
          <div v-else class="p-12 text-center">
            <div
              class="w-16 h-16 bg-gray-100 dark:bg-gray-800 rounded-full flex items-center justify-center mx-auto mb-4">
              <Search class="w-8 h-8 text-gray-300" />
            </div>
            <p class="text-gray-400 italic">未找到匹配的模型</p>
          </div>
        </div>
        <div
          class="p-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/20 flex justify-end">
          <button @click="showModelsModal = false"
            class="px-6 py-2 bg-gray-900 dark:bg-white text-white dark:text-gray-900 rounded-xl text-sm font-bold">关闭</button>
        </div>
      </div>
    </div>

    <!-- Edit/Add Modal -->
    <div v-if="editingProvider"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div
        class="bg-white dark:bg-gray-800 w-full max-w-3xl rounded-lg shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in duration-200 border border-white/10">
        <div
          class="p-5 px-8 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center bg-gray-50/50 dark:bg-gray-900/20">
          <div>
            <h3 class="text-xl font-black text-gray-900 dark:text-white tracking-tight">{{ isAdding ? '新增提供商' : '编辑配置'
              }}
            </h3>
            <p class="text-[10px] text-gray-500 font-bold uppercase tracking-widest mt-0.5">{{ isAdding ? 'Create new '
              : `Instance: ${editingProvider}` }}</p>
          </div>
          <button @click="editingProvider = null"
            class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all hover:rotate-90">
            <X class="w-5 h-5 text-gray-400" />
          </button>
        </div>

        <div class="p-8 py-6 space-y-6 overflow-y-auto max-h-[80vh] custom-scrollbar">
          <!-- Top Row: ID, Type, Timeout -->
          <div class="grid grid-cols-12 gap-5">
            <div class="col-span-4 space-y-1.5">
              <label class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] ml-1">提供商标识</label>
              <input v-model="editForm.name" :disabled="!isAdding" type="text" placeholder="标识符"
                class="w-full bg-gray-50 dark:bg-gray-900/50 border-2 border-transparent focus:border-blue-500/50 rounded-lg px-4 py-2.5 text-sm outline-none transition-all font-bold disabled:opacity-50" />
            </div>
            <div class="col-span-4 space-y-1.5">
              <label class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] ml-1">类型</label>
              <div class="relative">
                <select v-model="editForm.type"
                  class="w-full appearance-none bg-gray-50 dark:bg-gray-900/50 border-2 border-transparent focus:border-blue-500/50 rounded-lg px-4 py-2.5 text-sm outline-none transition-all font-bold cursor-pointer capitalize">
                  <option v-for="t in providerTypes" :key="t" :value="t">{{ t }}</option>
                </select>
                <ChevronDown
                  class="w-4 h-4 absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-gray-400" />
              </div>
            </div>
            <div class="col-span-4 space-y-1.5">
              <label class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] ml-1">超时 (秒)</label>
              <input v-model.number="editForm.timeout" type="number" step="0.5"
                class="w-full bg-gray-50 dark:bg-gray-900/50 border-2 border-transparent focus:border-blue-500/50 rounded-lg px-4 py-2.5 text-sm outline-none transition-all font-bold text-center" />
            </div>
          </div>

          <!-- Middle Row: Base URL & Extra Config -->
          <div class="grid grid-cols-12 gap-5">
            <div class="col-span-7 space-y-1.5">
              <label class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] ml-1">基础地址 (Base
                URL)</label>
              <input v-model="editForm.base_url" type="text" placeholder="https://api.openai.com/v1"
                class="w-full bg-gray-50 dark:bg-gray-900/50 border-2 border-transparent focus:border-blue-500/50 rounded-lg px-4 py-2.5 text-sm outline-none transition-all font-mono" />
            </div>
            <div class="col-span-5 space-y-1.5">
              <label class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] ml-1">额外 JSON 配置</label>
              <input v-model="editForm.extra" placeholder='{"proxy": "..."}'
                class="w-full bg-gray-50 dark:bg-gray-900/50 border-2 border-transparent focus:border-blue-500/50 rounded-lg px-4 py-2.5 text-sm outline-none transition-all font-mono" />
            </div>
          </div>

          <!-- Bottom: API Keys (Full Width) -->
          <div class="space-y-2.5 p-4 bg-blue-500/5 rounded-lg border border-blue-500/10">
            <div class="flex justify-between items-center">
              <label class="text-[10px] font-black text-blue-500 uppercase tracking-[0.2em] ml-1">API Key 池</label>
              <span class="text-[9px] text-blue-500/60 font-bold">支持逗号分隔，后端将自动轮换</span>
            </div>
            <textarea v-model="editForm.api_key" placeholder="sk-..., sk-..."
              class="w-full bg-white dark:bg-gray-900 border-2 border-transparent focus:border-blue-500/50 rounded-lg px-5 py-3 text-xs outline-none min-h-[90px] font-mono transition-all resize-none shadow-inner"></textarea>
          </div>
        </div>

        <div
          class="p-6 px-8 border-t border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/20 flex justify-end items-center gap-8">
          <button @click="editingProvider = null"
            class="text-xs font-bold text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors uppercase tracking-widest">Discard</button>
          <button @click="saveProvider"
            class="bg-blue-600 hover:bg-blue-500 text-white px-8 py-3 rounded-lg text-sm font-black transition-all hover:scale-[1.02] active:scale-95 shadow-lg shadow-blue-500/20">
            保存配置
          </button>
        </div>
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
import { Cloud, Plus, X, ChevronDown, Copy, AlertCircle, Search } from 'lucide-vue-next'

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
    return list.filter(m => {
      const id = (m as any).id || m
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
    providers.value = configData.providers
    healthStatus.value = healthData.providers
    models.value = modelsData
    providerTypes.value = typesData
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

  // 处理 API Key，如果是数组则转为逗号分隔
  if (Array.isArray(config.api_key)) {
    editForm.api_key = config.api_key.join(', ')
  } else {
    editForm.api_key = config.api_key || ''
  }

  editForm.timeout = config.timeout || 60.0

  // 提取额外配置
  const { type, base_url, api_key, timeout, ...rest } = config
  editForm.extra = Object.keys(rest).length > 0 ? JSON.stringify(rest, null, 2) : ''

  editingProvider.value = name
}

async function saveProvider() {
  if (!editForm.name) return ui.showToast('请填写提供商名称', 'error')

  const config = await getConfig()
  if (!config.providers) config.providers = {}

  // 处理 API Key，支持逗号分隔
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

  // 合并额外配置
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

async function testProvider(name: string) {
  try {
    const health = await getHealth()
    healthStatus.value = health.providers
    if (healthStatus.value[name] === 'healthy') {
      ui.showToast(`${name} 连接成功！`, 'success')
    } else {
      ui.showToast(`${name} 连接失败: ${healthStatus.value[name]}`, 'error')
    }
  } catch (err) {
    ui.showToast('测试过程出错', 'error')
  }
}

onMounted(() => {
  fetchAll()
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
