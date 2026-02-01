# FRONTEND KNOWLEDGE BASE

## OVERVIEW
Vue 3 dashboard for AliaProxy monitoring, logs, and interactive playground. Built with Vite, Pinia, TailwindCSS, and ECharts.

## STRUCTURE
```
frontend/
├── src/views/        # Top-level page components (Routed)
├── src/components/   # Reusable UI components
├── src/stores/       # Global state (Pinia)
├── src/api/          # Axios API wrappers
├── src/router/       # Vue Router configuration
└── src/assets/       # Static assets and global styles
```

## WHERE TO LOOK
| Task | Location | Notes |
|------|----------|-------|
| **Add Page** | `src/views/` | Add `.vue` file & register in `router/index.ts` |
| **Global State** | `src/stores/` | Use Pinia setup stores (e.g., `ui.ts`, `counter.ts`) |
| **API Calls** | `src/api/` | Encapsulate Axios calls here, don't call in components |
| **Layout/Nav** | `src/components/layout/` | `DefaultLayout.vue` wraps most pages |
| **Charts** | `src/views/Dashboard.vue` | Uses `vue-echarts` |

## CONVENTIONS
- **Component Style**: Use Composition API with `<script setup lang="ts">`.
- **Styling**: Utility-first with TailwindCSS. Avoid scoped `<style>` unless necessary.
- **State**: Use Pinia for cross-component state.
- **Icons**: Use `lucide-vue-next` for all iconography.

## ANTI-PATTERNS
- **Options API**: Do not use `export default { data, methods }`. Use `<script setup>`.
- **Direct DOM**: Avoid `document.getElementById`. Use `ref()` template refs.
- **Hardcoded Strings**: Use constants or config files for labels/titles where possible.

## COMMANDS
```bash
# Development
pnpm dev

# Build
pnpm build

# Lint/Format
pnpm lint
pnpm format
```
