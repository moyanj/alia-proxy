<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h3 class="text-xl font-bold text-gray-900 dark:text-white">配置的提供商</h3>
      <div class="flex gap-2">
        <button @click="openAddModal" class="text-sm bg-green-600 text-white px-4 py-2 rounded-lg hover:bg-green-700 transition-colors flex items-center gap-2">
          <Plus class="w-4 h-4" /> 添加提供商
        </button>
        <button @click="fetchAll" class="text-sm bg-blue-600 text-white px-4 py-2 rounded-lg hover:bg-blue-700 transition-colors">刷新状态</button>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
      <div v-for="(config, name) in providers" :key="name" class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden flex flex-col">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-start">
          <div class="flex items-center gap-3">
            <div class="w-10 h-10 bg-gray-100 dark:bg-gray-700 rounded-lg flex items-center justify-center">
              <Cloud class="w-6 h-6 text-gray-600 dark:text-gray-400" />
            </div>
            <div>
              <h4 class="text-lg font-bold text-gray-900 dark:text-white">{{ name }}</h4>
              <span class="text-xs font-medium px-2 py-0.5 bg-blue-100 text-blue-700 dark:bg-blue-900/30 dark:text-blue-400 rounded uppercase tracking-wider">{{ config.type }}</span>
            </div>
          </div>
          <div class="flex flex-col items-end gap-2">
            <div class="flex items-center gap-2">
              <div class="w-2 h-2 rounded-full" :class="healthStatus[name] === 'healthy' ? 'bg-green-500' : 'bg-red-500'"></div>
              <span class="text-xs font-medium text-gray-500">{{ healthStatus[name] || 'Checking...' }}</span>
            </div>
            <button @click="openEditModal(name, config)" class="text-xs text-blue-600 dark:text-blue-400 hover:underline">编辑配置</button>
          </div>
        </div>
        
        <div class="p-6 space-y-4 flex-1">
          <div class="grid grid-cols-1 gap-3">
            <div v-if="config.base_url" class="space-y-1">
              <p class="text-[10px] uppercase font-bold text-gray-400">Base URL</p>
              <p class="text-sm font-mono truncate bg-gray-50 dark:bg-gray-900/50 p-2 rounded-lg border border-gray-100 dark:border-gray-700/50">{{ config.base_url }}</p>
            </div>
            <div v-if="config.api_key" class="space-y-1">
              <p class="text-[10px] uppercase font-bold text-gray-400">API Key</p>
              <p class="text-sm font-mono bg-gray-50 dark:bg-gray-900/50 p-2 rounded-lg border border-gray-100 dark:border-gray-700/50">{{ config.api_key }}</p>
            </div>
          </div>
          
          <div class="space-y-2">
            <p class="text-[10px] uppercase font-bold text-gray-400 flex justify-between items-center">
              支持的模型
              <button @click="fetchModelsForProvider(name)" class="text-blue-500 hover:underline">查看全部</button>
            </p>
            <div class="flex flex-wrap gap-1.5">
              <span v-for="m in (models[name] || []).slice(0, 5)" :key="m.id" class="px-2 py-1 bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 text-[10px] rounded font-medium">
                {{ m.id || m }}
              </span>
              <span v-if="(models[name]?.length || 0) > 5" class="px-2 py-1 text-gray-400 text-[10px]">
                +{{ models[name].length - 5 }} more
              </span>
              <span v-if="!models[name]" class="text-xs text-gray-400 italic">点击刷新获取列表</span>
            </div>
          </div>
        </div>
        
        <div class="p-4 bg-gray-50 dark:bg-gray-900/30 border-t border-gray-200 dark:border-gray-700 flex justify-between">
           <button @click="testProvider(name)" class="text-xs font-bold text-blue-600 dark:text-blue-400 hover:underline">测试连接</button>
           <button @click="deleteProvider(name)" class="text-xs font-bold text-red-500 hover:underline">删除</button>
        </div>
      </div>
    </div>

    <!-- Edit/Add Modal -->
    <div v-if="editingProvider" class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div class="bg-white dark:bg-gray-800 w-full max-w-md rounded-2xl shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in duration-200">
        <div class="p-6 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white">{{ isAdding ? '添加提供商' : '编辑提供商' }}</h3>
          <button @click="editingProvider = null" class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors">
            <X class="w-6 h-6" />
          </button>
        </div>
        <div class="p-6 space-y-4">
          <div class="space-y-1.5">
            <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">提供商名称 (唯一标识)</label>
            <input v-model="editForm.name" :disabled="!isAdding" type="text" placeholder="例如: openai-pro" class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500" />
          </div>
          <div class="space-y-1.5">
            <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">类型</label>
            <select v-model="editForm.type" class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500">
              <option value="openai">OpenAI</option>
              <option value="anthropic">Anthropic</option>
              <option value="ollama">Ollama</option>
            </select>
          </div>
          <div class="space-y-1.5">
            <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">Base URL (可选)</label>
            <input v-model="editForm.base_url" type="text" placeholder="https://api.openai.com/v1" class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm outline-none" />
          </div>
          <div class="space-y-1.5">
            <label class="text-xs font-medium text-gray-500 uppercase tracking-wider">API Key</label>
            <input v-model="editForm.api_key" type="password" placeholder="保持不变或输入新 Key" class="w-full bg-gray-50 dark:bg-gray-900 border border-gray-200 dark:border-gray-700 rounded-lg px-3 py-2 text-sm outline-none" />
          </div>
        </div>
        <div class="p-6 border-t border-gray-200 dark:border-gray-700 flex justify-end gap-3">
          <button @click="editingProvider = null" class="px-4 py-2 text-sm text-gray-500 hover:text-gray-700">取消</button>
          <button @click="saveProvider" class="bg-blue-600 hover:bg-blue-700 text-white px-6 py-2 rounded-xl text-sm font-bold transition-all active:scale-95">保存配置</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { useUIStore } from '@/stores/ui'
import { 
  getConfig, 
  getHealth, 
  getAllModels,
  updateConfig,
  type ProviderConfig 
} from '@/api'
import { Cloud, Plus, X } from 'lucide-vue-next'

const ui = useUIStore()
const providers = ref<Record<string, ProviderConfig>>({})
const healthStatus = ref<Record<string, string>>({})
const models = ref<Record<string, any[]>>({})

const editingProvider = ref<string | null>(null)
const isAdding = ref(false)
const editForm = reactive({
  name: '',
  type: 'openai',
  base_url: '',
  api_key: ''
})

async function fetchAll() {
  try {
    const [configData, healthData, modelsData] = await Promise.all([
      getConfig(),
      getHealth(),
      getAllModels()
    ])
    providers.value = configData.providers
    healthStatus.value = healthData.providers
    models.value = modelsData
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
  editingProvider.value = 'new'
}

function openEditModal(name: string, config: any) {
  isAdding.value = false
  editForm.name = name
  editForm.type = config.type
  editForm.base_url = config.base_url || ''
  editForm.api_key = config.api_key || ''
  editingProvider.value = name
}

async function saveProvider() {
  if (!editForm.name) return ui.showToast('请填写提供商名称', 'error')
  
  const config = await getConfig()
  if (!config.providers) config.providers = {}
  
  config.providers[editForm.name] = {
    type: editForm.type,
    base_url: editForm.base_url || undefined,
    api_key: editForm.api_key || undefined
  }
  
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
  ui.showToast(`${name} 支持 ${models.value[name]?.length || 0} 个模型`, 'info')
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
