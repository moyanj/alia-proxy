# 前端开发

前端是一个标准的 **Vue 3** 单页应用，使用 **Vite** 构建。

## 关键技术栈

- **框架**: Vue 3 (Composition API)
- **语言**: TypeScript
- **状态管理**: Pinia
- **样式**: TailwindCSS
- **图标**: Lucide Vue Next
- **图表**: ECharts (vue-echarts)

## 代码风格

我们严格遵循 Vue 3 的 `<script setup>` 语法糖风格。

**推荐写法**:

```vue
<template>
  <div class="p-4 bg-white rounded-xl">
    <h1>{{ title }}</h1>
    <button @click="increment" class="btn-primary">Count: {{ count }}</button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'

// Props
defineProps<{
  title: string
}>()

// State
const count = ref(0)
const userStore = useUserStore()

// Computed
const doubleCount = computed(() => count.value * 2)

// Methods
function increment() {
  count.value++
}
</script>
```

## 状态管理 (Pinia)

全局状态（如用户偏好、当前加载的模型列表）存储在 `frontend/src/stores/` 目录中。

例如 `ui.ts` store 负责管理全局的 UI 状态（暗色模式、Toast 通知）：

```typescript
// frontend/src/stores/ui.ts
export const useUIStore = defineStore('ui', () => {
  const isDark = ref(false)
  
  function toggleTheme() {
    isDark.value = !isDark.value
    // ... dom manipulation
  }

  return { isDark, toggleTheme }
})
```

## API 集成

所有的后端 API 调用都封装在 `frontend/src/api/index.ts` 中，使用 `axios` 实例。不要在组件内部直接使用 `fetch` 或 `axios`，而是调用封装好的强类型函数。

```typescript
// frontend/src/api/index.ts
export async function getStats(): Promise<Stats> {
  const { data } = await api.get('/stats')
  return data
}
```
