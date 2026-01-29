<template>
  <div class="space-y-6">
    <div class="flex justify-between items-center">
      <h3 class="text-xl font-bold text-gray-900 dark:text-white">模型映射 (Model Mappings)</h3>
      <button @click="openAddMappingModal"
        class="text-sm bg-purple-600 text-white px-4 py-2 rounded-lg hover:bg-purple-700 transition-colors flex items-center gap-2">
        <Plus class="w-4 h-4" /> 添加映射
      </button>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      <div v-for="(config, key) in mappings" :key="key"
        class="bg-white dark:bg-gray-800 rounded-xl border border-gray-200 dark:border-gray-700 shadow-sm overflow-hidden flex flex-col">
        <div class="p-4 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center bg-purple-50/50 dark:bg-purple-900/10">
          <div class="flex items-center gap-3">
            <div class="w-8 h-8 bg-purple-100 dark:bg-purple-900/50 rounded-lg flex items-center justify-center">
              <Hash class="w-4 h-4 text-purple-600 dark:text-purple-400" />
            </div>
            <h4 class="text-base font-bold text-gray-900 dark:text-white font-mono">{{ key }}</h4>
          </div>
          <div class="flex gap-2">
            <button @click="openEditMappingModal(String(key), config)" class="text-xs font-bold text-blue-600 hover:text-blue-500">EDIT</button>
            <button @click="deleteMapping(String(key))" class="text-xs font-bold text-red-500 hover:text-red-400">DEL</button>
          </div>
        </div>
        <div class="p-4 space-y-3 flex-1">
           <div>
              <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest block mb-1">Targets</span>
              <div class="flex flex-wrap gap-1">
                 <template v-if="typeof config === 'string'">
                    <span class="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-xs font-mono">{{ config }}</span>
                 </template>
                 <template v-else-if="Array.isArray(config)">
                    <span v-for="t in config" :key="t" class="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-xs font-mono">{{ t }}</span>
                 </template>
                 <template v-else>
                    <span v-for="t in config.targets" :key="t" class="px-2 py-0.5 bg-gray-100 dark:bg-gray-700 rounded text-xs font-mono">{{ t }}</span>
                 </template>
              </div>
           </div>
           <div>
              <span class="text-[10px] font-bold text-gray-400 uppercase tracking-widest block mb-1">Strategy</span>
              <span class="text-xs font-medium text-gray-700 dark:text-gray-300">
                {{ (typeof config === 'object' && !Array.isArray(config) && config.strategy) ? config.strategy : 'round-robin (default)' }}
              </span>
           </div>
        </div>
      </div>
      
      <div v-if="Object.keys(mappings).length === 0" class="col-span-full py-12 text-center text-gray-400 bg-gray-50 dark:bg-gray-800/50 rounded-xl border border-dashed border-gray-300 dark:border-gray-700">
         暂无模型映射配置
      </div>
    </div>

    <!-- Edit/Add Mapping Modal -->
    <div v-if="editingMapping"
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm">
      <div
        class="bg-white dark:bg-gray-800 w-full max-w-lg rounded-lg shadow-2xl flex flex-col overflow-hidden animate-in fade-in zoom-in duration-200 border border-white/10">
        <div
          class="p-5 px-8 border-b border-gray-200 dark:border-gray-700 flex justify-between items-center bg-gray-50/50 dark:bg-gray-900/20">
          <div>
            <h3 class="text-xl font-black text-gray-900 dark:text-white tracking-tight">{{ isAdding ? '新增映射' : '编辑映射' }}</h3>
            <p class="text-[10px] text-gray-500 font-bold uppercase tracking-widest mt-0.5">Model Mapping Configuration</p>
          </div>
          <button @click="editingMapping = null"
            class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-all hover:rotate-90">
            <X class="w-5 h-5 text-gray-400" />
          </button>
        </div>

        <div class="p-8 py-6 space-y-6">
          <div class="space-y-1.5">
            <label class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] ml-1">映射名称 (Key)</label>
            <input v-model="mappingForm.key" :disabled="!isAdding" type="text" placeholder="例如: gpt-4, claude-3"
              class="w-full bg-gray-50 dark:bg-gray-900/50 border-2 border-transparent focus:border-purple-500/50 rounded-lg px-4 py-2.5 text-sm outline-none transition-all font-bold disabled:opacity-50" />
          </div>

          <div class="space-y-1.5">
            <label class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] ml-1">目标模型 (Targets)</label>
            <div class="bg-gray-50 dark:bg-gray-900/50 rounded-lg border-2 border-transparent p-2 max-h-40 overflow-y-auto custom-scrollbar">
               <label v-for="m in allAvailableModels" :key="m" class="flex items-center gap-2 px-2 py-1.5 hover:bg-gray-100 dark:hover:bg-gray-700 rounded cursor-pointer">
                  <input type="checkbox" :value="m" v-model="mappingForm.targets" class="rounded text-purple-600 focus:ring-purple-500" />
                  <span class="text-sm font-mono text-gray-700 dark:text-gray-300">{{ m }}</span>
               </label>
            </div>
            <p class="text-[10px] text-gray-400 px-1">选择一个或多个后端模型作为此映射的目标。</p>
          </div>

          <div class="space-y-1.5">
             <label class="text-[10px] font-black text-gray-400 uppercase tracking-[0.2em] ml-1">负载策略 (Strategy)</label>
             <select v-model="mappingForm.strategy" class="w-full bg-gray-50 dark:bg-gray-900/50 border-2 border-transparent focus:border-purple-500/50 rounded-lg px-4 py-2.5 text-sm outline-none transition-all font-bold">
                <option value="round-robin">Round Robin (轮询)</option>
                <option value="random">Random (随机)</option>
             </select>
          </div>
        </div>

        <div class="p-6 px-8 border-t border-gray-200 dark:border-gray-700 bg-gray-50/50 dark:bg-gray-900/20 flex justify-end items-center gap-8">
          <button @click="editingMapping = null"
            class="text-xs font-bold text-gray-400 hover:text-gray-900 dark:hover:text-white transition-colors uppercase tracking-widest">Discard</button>
          <button @click="saveMapping"
            class="bg-purple-600 hover:bg-purple-500 text-white px-8 py-3 rounded-lg text-sm font-black transition-all hover:scale-[1.02] active:scale-95 shadow-lg shadow-purple-500/20">
            保存映射
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
  getAllModels,
  updateConfig
} from '@/api'
import { Plus, X, Hash } from 'lucide-vue-next'

const ui = useUIStore()
const mappings = ref<Record<string, any>>({})
const models = ref<Record<string, any>>({})

const editingMapping = ref<string | null>(null)
const isAdding = ref(false)

const allAvailableModels = computed(() => {
  const list: string[] = []
  for (const provider in models.value) {
    const providerModels = models.value[provider]
    if (Array.isArray(providerModels)) {
      providerModels.forEach(m => {
        const id = (m as any).id || m
        list.push(`${provider}/${id}`)
      })
    }
  }
  return list
})

const mappingForm = reactive({
  key: '',
  targets: [] as string[],
  strategy: 'round-robin'
})

async function fetchAll() {
  try {
    const [configData, modelsData] = await Promise.all([
      getConfig(),
      getAllModels()
    ])
    mappings.value = configData.mapping || {}
    models.value = modelsData
  } catch (err) {
    console.error('Failed to fetch mappings info:', err)
  }
}

function openAddMappingModal() {
  isAdding.value = true
  mappingForm.key = ''
  mappingForm.targets = []
  mappingForm.strategy = 'round-robin'
  editingMapping.value = 'new'
}

function openEditMappingModal(key: string, config: any) {
  isAdding.value = false
  mappingForm.key = key
  
  if (typeof config === 'string') {
    mappingForm.targets = [config]
    mappingForm.strategy = 'round-robin'
  } else if (Array.isArray(config)) {
    mappingForm.targets = [...config]
    mappingForm.strategy = 'round-robin'
  } else {
    mappingForm.targets = [...config.targets]
    mappingForm.strategy = config.strategy || 'round-robin'
  }
  
  editingMapping.value = key
}

async function saveMapping() {
  if (!mappingForm.key) return ui.showToast('请填写映射名称', 'error')
  if (mappingForm.targets.length === 0) return ui.showToast('请至少选择一个目标模型', 'error')

  const config = await getConfig()
  if (!config.mapping) config.mapping = {}

  // Construct mapping config
  let mappingData: any
  if (mappingForm.targets.length === 1 && mappingForm.strategy === 'round-robin') {
     mappingData = {
       targets: mappingForm.targets,
       strategy: mappingForm.strategy
     }
  } else {
     mappingData = {
       targets: mappingForm.targets,
       strategy: mappingForm.strategy
     }
  }

  config.mapping[mappingForm.key] = mappingData

  try {
    await updateConfig(config)
    ui.showToast('映射保存成功', 'success')
    editingMapping.value = null
    fetchAll()
  } catch (err) {
    ui.showToast('保存失败', 'error')
  }
}

async function deleteMapping(key: string) {
  if (await ui.confirm('确认删除', `确定要删除映射 ${key} 吗？`)) {
    const config = await getConfig()
    if (config.mapping && config.mapping[key]) {
      delete config.mapping[key]
      try {
        await updateConfig(config)
        ui.showToast('映射已删除', 'success')
        fetchAll()
      } catch (err) {
        ui.showToast('删除失败', 'error')
      }
    }
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
