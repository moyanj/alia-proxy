<template>
  <div class="space-y-6 animate-in fade-in slide-in-from-bottom-4 duration-500">
    <div class="flex justify-between items-center mb-8">
      <div>
        <h3 class="text-xl font-bold text-gray-900 dark:text-white">模型映射</h3>
        <p class="text-xs text-gray-500">将通用模型名称映射到一个或多个实际的后端模型。</p>
      </div>
      <button @click="openAddMappingModal" class="win-btn-primary flex items-center gap-2">
        <Plus class="w-4 h-4" /> 添加映射
      </button>
    </div>

    <div class="space-y-2">
      <div v-for="(config, key) in mappings" :key="key" 
        class="win-card px-6 py-4 flex items-center justify-between win-card-hover group transition-all"
      >
        <div class="flex items-center gap-6">
          <div class="w-12 h-12 rounded-xl bg-purple-500/10 flex items-center justify-center text-purple-600 shrink-0">
             <Hash class="w-6 h-6" />
          </div>
          <div class="flex flex-col">
            <span class="text-[15px] font-bold text-gray-900 dark:text-white">{{ key }}</span>
            <div class="flex items-center gap-2 mt-1">
               <span class="text-[11px] font-bold text-purple-600 dark:text-purple-400 uppercase tracking-tighter">
                 {{ getStrategy(config) }}
               </span>
               <span class="text-[11px] text-gray-400 font-medium">
                 → {{ getTargetsCount(config) }} 个目标模型
               </span>
            </div>
          </div>
        </div>

        <div class="flex items-center gap-4">
           <div class="flex flex-wrap gap-1 max-w-[300px] justify-end">
              <span v-for="t in getTargets(config).slice(0, 2)" :key="t" class="px-2 py-0.5 rounded bg-black/5 dark:bg-white/5 text-[10px] font-mono text-gray-500 border border-black/5">
                {{ t }}
              </span>
              <span v-if="getTargets(config).length > 2" class="text-[10px] text-gray-400 font-bold">+{{ getTargets(config).length - 2 }}</span>
           </div>

            <div class="flex items-center gap-1">
               <button @click="openEditMappingModal(String(key), config)" class="p-2 hover:bg-black/5 dark:hover:bg-white/5 rounded-md text-gray-500" title="编辑">
                  <Settings class="w-4 h-4" />
               </button>
               <button @click="deleteMapping(String(key))" class="p-2 hover:bg-red-500/10 hover:text-red-500 rounded-md transition-colors" title="删除">
                  <Trash2 class="w-4 h-4" />
               </button>
            </div>
        </div>
      </div>

      <div v-if="Object.keys(mappings).length === 0" class="py-24 win-card flex flex-col items-center justify-center text-gray-400 border-dashed">
         <ZapOff class="w-12 h-12 mb-4 opacity-20" />
         <p class="text-sm font-bold uppercase tracking-widest">未配置模型映射</p>
         <button @click="openAddMappingModal" class="mt-4 text-purple-600 dark:text-purple-400 font-bold hover:underline">点击立即添加</button>
      </div>
    </div>

    <!-- Edit/Add Mapping Dialog -->
    <div v-if="editingMapping" class="fixed inset-0 z-[100] flex items-center justify-center p-4">
       <div class="absolute inset-0 bg-black/40 backdrop-blur-sm" @click="editingMapping = null"></div>
       <div class="win-card w-full max-w-lg shadow-2xl animate-in zoom-in-95 duration-200 flex flex-col overflow-hidden relative z-10">
          <header class="p-6 border-b border-black/5 dark:border-white/5 flex items-center justify-between">
             <h4 class="text-lg font-bold">{{ isAdding ? '添加模型映射' : `编辑 ${editingMapping}` }}</h4>
             <button @click="editingMapping = null" class="p-2 hover:bg-black/5 rounded-full transition-colors">
                <X class="w-5 h-5" />
             </button>
          </header>

          <div class="p-8 overflow-y-auto max-h-[70vh] custom-scrollbar space-y-6">
             <div class="space-y-1.5">
                <label class="text-[11px] font-bold text-gray-500 uppercase tracking-widest ml-1">映射名称 (对外展示的模型名)</label>
                <input v-model="mappingForm.key" :disabled="!isAdding" type="text" placeholder="gpt-4, my-custom-model"
                  class="w-full bg-white dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-md px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500/50 disabled:opacity-50" />
             </div>

             <div class="space-y-1.5">
                <label class="text-[11px] font-bold text-gray-500 uppercase tracking-widest ml-1">负载策略</label>
                <div class="relative">
                   <select v-model="mappingForm.strategy"
                     class="w-full bg-white dark:bg-white/5 border border-black/10 dark:border-white/10 rounded-md px-4 py-2 text-sm outline-none focus:ring-2 focus:ring-blue-500/50 appearance-none">
                     <option value="round-robin">Round Robin (轮询)</option>
                     <option value="random">Random (随机)</option>
                   </select>
                   <ChevronDown class="absolute right-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400 pointer-events-none" />
                </div>
             </div>

             <div class="space-y-1.5">
                <label class="text-[11px] font-bold text-gray-500 uppercase tracking-widest ml-1">目标模型 (支持多选)</label>
                <div class="win-card max-h-48 overflow-y-auto custom-scrollbar p-1">
                   <label v-for="m in allAvailableModels" :key="m" class="flex items-center gap-3 px-3 py-2 hover:bg-black/5 dark:hover:bg-white/5 rounded-md cursor-pointer group">
                      <input type="checkbox" :value="m" v-model="mappingForm.targets" class="w-4 h-4 rounded border-gray-300 text-blue-600 focus:ring-blue-500/50" />
                      <span class="text-sm font-mono transition-colors group-hover:text-blue-500">{{ m }}</span>
                   </label>
                   <div v-if="allAvailableModels.length === 0" class="p-4 text-center text-xs text-gray-400 italic">
                      未发现可用的后端模型，请先配置提供商
                   </div>
                </div>
             </div>
          </div>

          <footer class="p-6 border-t border-black/5 bg-black/[0.01] flex justify-end gap-3">
             <button @click="editingMapping = null" class="px-6 py-2 bg-black/5 hover:bg-black/10 rounded-md text-sm font-bold transition-colors">
                取消
             </button>
             <button @click="saveMapping" class="win-btn-primary px-8">
                保存映射
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
  getAllModels,
  updateConfig
} from '@/api'
import { 
  Plus, X, Hash, ChevronDown, Settings, Trash2, ZapOff 
} from 'lucide-vue-next'

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

function getStrategy(config: any) {
  if (typeof config === 'object' && !Array.isArray(config) && config.strategy) {
    return config.strategy
  }
  return 'round-robin'
}

function getTargets(config: any): string[] {
  if (typeof config === 'string') return [config]
  if (Array.isArray(config)) return config
  return config.targets || []
}

function getTargetsCount(config: any) {
  return getTargets(config).length
}

async function fetchAll() {
  try {
    const [configData, modelsData] = await Promise.all([
      getConfig(),
      getAllModels()
    ])
    mappings.value = configData.mapping || {}
    models.value = modelsData || {}
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
  mappingForm.targets = getTargets(config)
  mappingForm.strategy = getStrategy(config)
  editingMapping.value = key
}

async function saveMapping() {
  if (!mappingForm.key) return ui.showToast('请填写映射名称', 'error')
  if (mappingForm.targets.length === 0) return ui.showToast('请至少选择一个目标模型', 'error')

  const config = await getConfig()
  if (!config.mapping) config.mapping = {}

  config.mapping[mappingForm.key] = {
    targets: mappingForm.targets,
    strategy: mappingForm.strategy
  }

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
