import { ref } from 'vue'
import { defineStore } from 'pinia'

export interface Toast {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
}

export const useUIStore = defineStore('ui', () => {
  const toasts = ref<Toast[]>([])
  const confirmModal = ref<{
    show: boolean
    title: string
    message: string
    onConfirm: () => void
    onCancel: () => void
  } | null>(null)

  let toastId = 0

  function showToast(message: string, type: 'success' | 'error' | 'info' = 'info') {
    const id = ++toastId
    toasts.value.push({ id, message, type })
    setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id)
    }, 3000)
  }

  function confirm(title: string, message: string): Promise<boolean> {
    return new Promise((resolve) => {
      confirmModal.value = {
        show: true,
        title,
        message,
        onConfirm: () => {
          confirmModal.value = null
          resolve(true)
        },
        onCancel: () => {
          confirmModal.value = null
          resolve(false)
        }
      }
    })
  }

  return { toasts, confirmModal, showToast, confirm }
})
