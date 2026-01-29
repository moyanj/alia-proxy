import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { useRouter } from 'vue-router'
import { type Log } from '@/api'

export interface Message {
  role: 'system' | 'user' | 'assistant'
  content: string
}

export interface PlaygroundState {
  model: string
  systemPrompt: string
  messages: Message[]
  temperature: number
  stream: boolean
}

export const usePlaygroundStore = defineStore('playground', () => {
  const router = useRouter()
  
  // State
  const model = ref('')
  const systemPrompt = ref('You are a helpful assistant.')
  const messages = ref<Message[]>([])
  const temperature = ref(0.7)
  const stream = ref(true)
  
  // Actions
  function setModel(newModel: string) {
    model.value = newModel
  }

  function setSystemPrompt(prompt: string) {
    systemPrompt.value = prompt
  }

  function setTemperature(temp: number) {
    temperature.value = temp
  }

  function setStream(isStream: boolean) {
    stream.value = isStream
  }

  function addMessage(role: 'user' | 'assistant', content: string = '') {
    messages.value.push({ role, content })
  }

  function updateMessage(index: number, content: string) {
    if (messages.value[index]) {
      messages.value[index].content = content
    }
  }

  function removeMessage(index: number) {
    messages.value.splice(index, 1)
  }

  function clearMessages() {
    messages.value = []
  }

  function loadFromLog(log: Log) {
    // Reset state
    clearMessages()
    
    // Set Model
    if (log.provider && log.model) {
      model.value = `${log.provider}/${log.model}`
    }

    // Parse Content
    try {
      if (log.content?.prompt) {
        const promptData = JSON.parse(log.content.prompt)
        
        if (Array.isArray(promptData)) {
          // Handle array of messages
          promptData.forEach((msg: any) => {
            if (msg.role === 'system') {
              systemPrompt.value = msg.content
            } else {
              messages.value.push({
                role: msg.role,
                content: typeof msg.content === 'string' ? msg.content : JSON.stringify(msg.content)
              })
            }
          })
        } else if (typeof promptData === 'object') {
            // Handle single object (unlikely for chat but possible)
             if (promptData.role === 'system') {
              systemPrompt.value = promptData.content
            } else {
              messages.value.push({
                role: promptData.role || 'user',
                content: typeof promptData.content === 'string' ? promptData.content : JSON.stringify(promptData.content)
              })
            }
        } else {
           // Handle string prompt
           messages.value.push({ role: 'user', content: String(promptData) })
        }
      }
      
      // Add Assistant Response if exists
      if (log.content?.response) {
        messages.value.push({
          role: 'assistant',
          content: log.content.response
        })
      }
    } catch (e) {
      console.error('Failed to parse log content for playground:', e)
      // Fallback: treat as simple string
      if (log.content?.prompt) {
         messages.value.push({ role: 'user', content: log.content.prompt })
      }
    }

    // Navigate to Playground
    router.push('/playground')
  }

  return {
    model,
    systemPrompt,
    messages,
    temperature,
    stream,
    setModel,
    setSystemPrompt,
    setTemperature,
    setStream,
    addMessage,
    updateMessage,
    removeMessage,
    clearMessages,
    loadFromLog
  }
})
