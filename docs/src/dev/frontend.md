# 前端开发

前端是一个基于 **Vue 3** 的现代化单页应用（SPA），使用 **Vite** 构建，提供了 AI Proxy Service 的完整 Web 管理界面。

## 技术栈概览

| 类别 | 技术 | 版本 |
|------|------|------|
| 框架 | Vue 3 | 3.5.26 |
| 构建工具 | Vite | 7.3.1 |
| 状态管理 | Pinia | 3.0.4 |
| 路由 | Vue Router | 4.6.4 |
| UI 样式 | TailwindCSS | 4.1.18 |
| 图表库 | ECharts + vue-echarts | 6.0.0 + 8.0.1 |
| 图标库 | lucide-vue-next | 0.563.0 |
| HTTP 客户端 | Axios | 1.13.3 |
| 编程语言 | TypeScript | 5.9.3 |

## 项目结构

```
frontend/
├── src/
│   ├── views/              # 页面组件 (路由视图)
│   │   ├── Dashboard.vue   # 系统仪表盘首页
│   │   ├── Analytics.vue   # 数据分析报告
│   │   ├── Logs.vue        # 请求日志管理
│   │   ├── Providers.vue   # 提供商配置
│   │   ├── Mappings.vue    # 模型映射配置
│   │   └── Playground.vue  # AI 对话测试演练场
│   ├── components/         # 可复用组件
│   │   ├── layout/
│   │   │   ├── DefaultLayout.vue  # 主布局框架
│   │   │   └── GlobalUI.vue       # 全局 UI 组件 (Toast、Modal)
│   │   ├── MiniChart.vue    # 迷你趋势图
│   │   └── TrendIndicator.vue # 趋势指示器
│   ├── stores/             # Pinia 状态管理
│   │   ├── ui.ts           # UI 状态 (主题、Toast、确认框)
│   │   ├── playground.ts   # 演练场状态 (消息、模型配置)
│   │   └── counter.ts      # 示例计数器
│   ├── api/                # API 接口封装
│   │   └── index.ts        # Axios 实例及接口函数
│   ├── router/             # 路由配置
│   │   └── index.ts        # Vue Router 定义
│   ├── assets/             # 静态资源
│   │   └── main.css        # 全局样式
│   ├── main.ts             # 应用入口
│   └── App.vue             # 根组件
├── tailwind.config.ts      # TailwindCSS 配置
├── vite.config.ts          # Vite 构建配置
├── tsconfig.json           # TypeScript 配置
└── package.json            # 依赖管理
```

## 页面路由

所有页面均通过 Vue Router 管理，采用嵌套路由结构，由 `DefaultLayout` 提供统一布局框架：

| 路径 | 页面名称 | 功能描述 |
|------|----------|----------|
| `/` | Dashboard | 系统运行状态仪表盘、实时指标卡片、模型负载分布、24h 趋势图 |
| `/analytics` | Analytics | 请求趋势分析、错误统计、提供商分布图表 |
| `/logs` | Logs | 请求日志列表查看、详情展开、删除操作 |
| `/providers` | Providers | AI 提供商配置管理 (API Key、Base URL 等) |
| `/mappings` | Mappings | 模型映射关系配置 |
| `/playground` | Playground | AI 对话测试演练场，支持可视化/JSON 双模式编辑 |

## 代码风格规范

我们严格遵循 Vue 3 的 `<script setup>` 语法糖风格，所有组件均使用 **Composition API** + **TypeScript**。

### 组件模板

**推荐写法**：

```vue
<template>
  <div class="p-4 bg-white dark:bg-gray-800 rounded-xl">
    <h1 class="text-lg font-bold">{{ title }}</h1>
    <button @click="increment" class="btn-primary">
      Count: {{ count }}
    </button>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import { useUserStore } from '@/stores/user'

// Props 定义
defineProps<{
  title: string
}>()

// Emits 定义
const emit = defineEmits<{
  (e: 'update', value: number): void
}>()

// State
const count = ref(0)
const userStore = useUserStore()

// Computed
const doubleCount = computed(() => count.value * 2)

// Methods
function increment() {
  count.value++
  emit('update', count.value)
}
</script>
```

**禁止写法**：
- Options API (`export default { data(), methods() }`)
- 直接操作 DOM (`document.getElementById`)
- 硬编码字符串（应使用常量或配置）

## 状态管理 (Pinia)

全局状态存储在 `frontend/src/stores/` 目录中，采用 **Setup Store** 语法（函数式定义）。

### UI 状态管理 (ui.ts)

管理主题切换、Toast 通知、确认对话框等全局 UI 状态：

```typescript
// frontend/src/stores/ui.ts
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

  // 初始化主题
  function initTheme() {
    if (localStorage.theme === 'dark' || 
        (!('theme' in localStorage) && 
         window.matchMedia('(prefers-color-scheme: dark)').matches)) {
      isDark.value = true
      document.documentElement.classList.add('dark')
    }
  }

  // 切换主题
  function toggleTheme() {
    isDark.value = !    if (isisDark.value
Dark.value) {
      document.documentElement.classList.add('dark')
      localStorage.theme = 'dark'
    } else {
      document.documentElement.classList.remove('dark')
      localStorage.theme = 'light'
    }
  }

  // 显示 Toast
  function showToast(message: string, type: 'success' | 'error' | 'info' = 'info') {
    const id = Date.now()
    toasts.value.push({ id, message, type })
    setTimeout(() => {
      toasts.value = toasts.value.filter(t => t.id !== id)
    }, 3000)
  }

  return { toasts, isDark, initTheme, toggleTheme, showToast }
})
```

### 演练场状态管理 (playground.ts)

管理 Playground 页面的对话状态，支持从日志加载历史会话：

```typescript
// frontend/src/stores/playground.ts
import { ref, computed } from 'vue'
import { defineStore } from 'pinia'
import { useRouter } from 'vue-router'
import { type Log } from '@/api'

export interface Message {
  role: 'system' | 'user' | 'assistant'
  content: string
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

  function addMessage(role: 'user' | 'assistant', content: string = '') {
    messages.value.push({ role, content })
  }

  function clearMessages() {
    messages.value = []
  }

  // 从日志加载会话
  function loadFromLog(log: Log) {
    clearMessages()
    if (log.provider && log.model) {
      model.value = `${log.provider}/${log.model}`
    }
    // 解析日志内容并填充消息...
    router.push('/playground')
  }

  return {
    model,
    systemPrompt,
    messages,
    temperature,
    stream,
    setModel,
    addMessage,
    clearMessages,
    loadFromLog
  }
})
```

## API 集成

所有后端 API 调用都封装在 `frontend/src/api/index.ts` 中，使用 **Axios** 实例并导出强类型的接口函数。组件中应调用封装好的函数，而非直接使用 `fetch` 或 `axios`。

### API 接口定义

```typescript
// frontend/src/api/index.ts
import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL || '',
})

// 类型定义
export interface Log {
  id: number
  request_id: string | null
  timestamp: string
  provider: string
  model: string
  status_code: number
  latency: number
  // ... 其他字段
}

export interface Stats {
  total_requests: number
  provider_counts: Record<string, number>
  model_counts: Record<string, number>
  // ... 其他字段
}

export interface Analytics {
  summary: {
    total_requests: number
    success_rate: number
    avg_latency: number
  }
  // ... 其他统计字段
}

// 接口函数
export const getStats = () => api.get<Stats>('/api/stats').then(res => res.data)
export const getAnalytics = (params?: { days?: number }) => 
  api.get<Analytics>('/api/analytics', { params }).then(res => res.data)
export const getLogs = (params: any) => api.get<Log[]>('/api/logs', { params }).then(res => res.data)
export const getProviders = () => api.get<Record<string, ProviderConfig>>('/api/providers').then(res => res.data)
export const getAllModels = () => api.get<Record<string, any[]>>('/api/models').then(res => res.data)

export default api
```

### 组件中使用

```typescript
// 在组件中调用
import { getStats, getAnalytics } from '@/api'

async function fetchData() {
  const stats = await getStats()
  const analytics = await getAnalytics({ days: 7 })
}
```

## 布局与导航

### 主布局 (DefaultLayout)

应用采用 **WinUI 3** 风格设计，包含左侧导航栏和右侧内容区：

```typescript
// 导航菜单配置
const groupedNavItems = [
  {
    title: '概览',
    items: [
      { name: '仪表盘', path: '/', icon: LayoutDashboard },
      { name: '分析报告', path: '/analytics', icon: BarChart3 },
      { name: '实时状态', path: '/health', icon: Activity },
    ]
  },
  {
    title: '日志',
    items: [
      { name: '请求日志', path: '/logs', icon: ListTodo },
    ]
  },
  {
    title: '配置',
    items: [
      { name: '提供商配置', path: '/providers', icon: ShieldCheck },
      { name: '模型映射', path: '/mappings', icon: Hash },
    ]
  },
  {
    title: '开发者',
    items: [
      { name: '演练场', path: '/playground', icon: Terminal },
    ]
  }
]
```

### 页面过渡动画

所有页面切换均带有平滑的过渡动画效果：

```vue
<router-view v-slot="{ Component }">
  <transition 
    enter-active-class="transition duration-300 ease-out"
    enter-from-class="opacity-0 translate-y-4"
    enter-to-class="opacity-100 translate-y-0"
    leave-active-class="transition duration-200 ease-in"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
    mode="out-in"
  >
    <component :is="Component" />
  </transition>
</router-view>
```

## 样式规范

### TailwindCSS 4

项目使用 TailwindCSS 4.0，配合 PostCSS 进行样式处理。遵循以下规范：

- **工具类优先**：优先使用 TailwindCSS 工具类，仅在必要时添加自定义样式
- **暗色模式**：通过 `dark:` 前缀支持暗色模式
- **自定义类**：使用 `.win-card` 等自定义类实现统一的卡片风格

### 全局样式

```css
/* frontend/src/assets/main.css */
@tailwind base;
@tailwind components;
@tailwind utilities;

/* 自定义卡片样式 */
.win-card {
  @apply bg-white dark:bg-[#1a1a1a] rounded-xl border border-black/5 dark:border-white/5;
}

/* 按钮样式 */
.win-btn-primary {
  @apply px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors;
}
```

## 图表集成

项目使用 **ECharts** + **vue-echarts** 实现数据可视化：

```typescript
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { LineChart, PieChart } from 'echarts/charts'
import { GridComponent, TooltipComponent, LegendComponent } from 'echarts/components'
import VChart from 'vue-echarts'

use([CanvasRenderer, LineChart, PieChart, GridComponent, TooltipComponent, LegendComponent])

// 在组件中使用
const chartOption = computed(() => ({
  tooltip: { trigger: 'axis' },
  xAxis: { type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'] },
  yAxis: { type: 'value' },
  series: [{ type: 'line', data: [820, 932, 901, 934, 1290, 1330, 1320] }]
}))
```

## 开发命令

```bash
# 安装依赖
pnpm install

# 开发模式启动
pnpm dev

# 类型检查
pnpm type-check

# 构建生产版本
pnpm build

# 代码格式化
pnpm format

# 代码检查与修复
pnpm lint
```

## 注意事项

1. **禁止使用 `any`**：TypeScript 严格模式，禁止使用 `any` 类型
2. **禁止 Options API**：必须使用 `<script setup>` Composition API
3. **API 封装**：所有接口调用必须通过 `src/api/index.ts` 封装
4. **图标使用**：统一使用 `lucide-vue-next` 图标库
5. **路径别名**：使用 `@/` 别名引用 src 目录下的模块
