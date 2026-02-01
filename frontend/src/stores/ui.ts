import { ref } from 'vue'
import { defineStore } from 'pinia'

export interface Toast {
  id: number
  message: string
  type: 'success' | 'error' | 'info'
}

export const useUIStore = defineStore('ui', () => {
  const toasts = ref<Toast[]>([])
  const isDark = ref(false)
  const confirmModal = ref<{
    show: boolean
    title: string
    message: string
    onConfirm: () => void
    onCancel: () => void
  } | null>(null)

  let toastId = 0

  function initTheme() {
    if (localStorage.theme === 'dark' || (!('theme' in localStorage) && window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      isDark.value = true
      document.documentElement.classList.add('dark')
    } else {
      isDark.value = false
      document.documentElement.classList.remove('dark')
    }
  }

  function toggleTheme() {
    isDark.value = !isDark.value
    if (isDark.value) {
      document.documentElement.classList.add('dark')
      localStorage.theme = 'dark'
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.theme = 'light'
    }
  }

  function showToast(message: string, type: 'success' | 'error' | 'info' = 'info') {
    const id = ++toastId
    toasts.value.push({ id, message, type })
    setTimeout(() => {
      removeToast(id)
    }, 3000)
  }

  function removeToast(id: number) {
    toasts.value = toasts.value.filter(t => t.id !== id)
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

  return { toasts, confirmModal, isDark, initTheme, toggleTheme, showToast, removeToast, confirm }
})
