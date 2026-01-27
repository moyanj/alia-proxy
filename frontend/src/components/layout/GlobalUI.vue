<template>
  <!-- Toasts -->
  <div class="fixed top-4 right-4 z-[100] space-y-2 pointer-events-none">
    <transition-group name="toast">
      <div 
        v-for="toast in ui.toasts" 
        :key="toast.id"
        class="pointer-events-auto px-4 py-3 rounded-xl shadow-lg border flex items-center gap-3 min-w-[200px]"
        :class="[
          toast.type === 'success' ? 'bg-green-50 border-green-200 text-green-800 dark:bg-green-900/90 dark:border-green-800 dark:text-green-300' :
          toast.type === 'error' ? 'bg-red-50 border-red-200 text-red-800 dark:bg-red-900/90 dark:border-red-800 dark:text-red-300' :
          'bg-blue-50 border-blue-200 text-blue-800 dark:bg-blue-900/90 dark:border-blue-800 dark:text-blue-300'
        ]"
      >
        <component :is="getIcon(toast.type)" class="w-5 h-5 flex-shrink-0" />
        <span class="text-sm font-medium">{{ toast.message }}</span>
      </div>
    </transition-group>
  </div>

  <!-- Confirmation Modal -->
  <div v-if="ui.confirmModal" class="fixed inset-0 z-[110] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
    <div class="bg-white dark:bg-gray-800 w-full max-w-sm rounded-2xl shadow-2xl p-6 space-y-4 animate-in zoom-in duration-200">
      <h3 class="text-lg font-bold text-gray-900 dark:text-white">{{ ui.confirmModal.title }}</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 leading-relaxed">{{ ui.confirmModal.message }}</p>
      <div class="flex justify-end gap-3 pt-2">
        <button @click="ui.confirmModal.onCancel" class="px-4 py-2 text-sm text-gray-500 hover:text-gray-700 font-medium">取消</button>
        <button @click="ui.confirmModal.onConfirm" class="bg-red-600 hover:bg-red-700 text-white px-6 py-2 rounded-xl text-sm font-bold transition-all active:scale-95">确定</button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUIStore } from '@/stores/ui'
import { CheckCircle2, AlertCircle, Info } from 'lucide-vue-next'

const ui = useUIStore()

function getIcon(type: string) {
  if (type === 'success') return CheckCircle2
  if (type === 'error') return AlertCircle
  return Info
}
</script>

<style scoped>
.toast-enter-active,
.toast-leave-active {
  transition: all 0.3s ease;
}
.toast-enter-from {
  opacity: 0;
  transform: translateX(30px);
}
.toast-leave-to {
  opacity: 0;
  transform: scale(0.9);
}
</style>
