<template>
  <!-- Toasts (WinUI 3 style info bars) -->
  <div class="fixed top-8 right-8 z-[200] space-y-3 pointer-events-none w-[380px]">
    <transition-group 
      enter-active-class="transition duration-300 ease-out"
      enter-from-class="opacity-0 translate-x-12 scale-95"
      enter-to-class="opacity-100 translate-x-0 scale-100"
      leave-active-class="transition duration-200 ease-in"
      leave-from-class="opacity-100 scale-100"
      leave-to-class="opacity-0 scale-95"
    >
      <div 
        v-for="toast in ui.toasts" 
        :key="toast.id"
        class="pointer-events-auto px-4 py-3 rounded-lg shadow-2xl border flex items-center gap-4 group"
        :class="[
          toast.type === 'success' ? 'bg-white dark:bg-[#2d2d2d] border-green-500/20' :
          toast.type === 'error' ? 'bg-white dark:bg-[#2d2d2d] border-red-500/20' :
          'bg-white dark:bg-[#2d2d2d] border-blue-500/20'
        ]"
      >
        <!-- Color Bar -->
        <div 
          class="absolute left-0 top-3 bottom-3 w-1 rounded-full"
          :class="[
            toast.type === 'success' ? 'bg-green-500' :
            toast.type === 'error' ? 'bg-red-500' :
            'bg-blue-500'
          ]"
        ></div>

        <div class="p-1.5 rounded-md" :class="[
          toast.type === 'success' ? 'bg-green-500/10 text-green-600' :
          toast.type === 'error' ? 'bg-red-500/10 text-red-600' :
          'bg-blue-500/10 text-blue-600'
        ]">
          <component :is="getIcon(toast.type)" class="w-4 h-4 shrink-0" />
        </div>
        
        <div class="flex-1">
          <p class="text-xs font-bold text-gray-900 dark:text-white leading-tight">{{ toast.type.toUpperCase() }}</p>
          <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{{ toast.message }}</p>
        </div>

        <button @click="ui.removeToast(toast.id)" class="opacity-0 group-hover:opacity-100 p-1 hover:bg-black/5 dark:hover:bg-white/5 rounded transition-all">
          <X class="w-3.5 h-3.5 text-gray-400" />
        </button>
      </div>
    </transition-group>
  </div>

  <!-- Confirmation Modal (WinUI 3 ContentDialog style) -->
  <div v-if="ui.confirmModal" class="fixed inset-0 z-[210] flex items-center justify-center p-4">
    <div class="absolute inset-0 bg-black/40 backdrop-blur-[2px] animate-in fade-in duration-200" @click="ui.confirmModal.onCancel"></div>
    <div class="win-card w-full max-w-[400px] shadow-[0_20px_60px_rgba(0,0,0,0.3)] overflow-hidden animate-in zoom-in-95 duration-200 relative z-10">
      <div class="p-8 space-y-4">
        <h3 class="text-xl font-bold text-gray-900 dark:text-white tracking-tight">{{ ui.confirmModal.title }}</h3>
        <p class="text-[13px] text-gray-600 dark:text-gray-400 leading-relaxed">{{ ui.confirmModal.message }}</p>
      </div>
      
      <div class="p-6 bg-black/[0.02] dark:bg-white/[0.02] border-t border-black/5 dark:border-white/5 flex gap-3">
        <button 
          @click="ui.confirmModal.onConfirm" 
          class="flex-1 win-btn-primary py-2.5 rounded-md font-bold"
        >
          确定
        </button>
        <button 
          @click="ui.confirmModal.onCancel" 
          class="flex-1 bg-white dark:bg-white/5 border border-black/10 dark:border-white/10 text-gray-700 dark:text-white py-2.5 rounded-md text-[13px] font-bold hover:bg-black/5 dark:hover:bg-white/10 transition-all"
        >
          取消
        </button>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useUIStore } from '@/stores/ui'
import { CheckCircle2, AlertCircle, Info, X } from 'lucide-vue-next'

const ui = useUIStore()

function getIcon(type: string) {
  if (type === 'success') return CheckCircle2
  if (type === 'error') return AlertCircle
  return Info
}
</script>
