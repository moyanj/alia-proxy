<template>
  <div class="flex items-center gap-0.5 text-[10px] font-bold"
    :class="actualTrend >= 0 ? (inverse ? 'text-red-500' : 'text-green-500') : (inverse ? 'text-green-500' : 'text-red-500')">
    <TrendingUp v-if="actualTrend >= 0" class="w-3 h-3" />
    <TrendingDown v-else class="w-3 h-3" />
    <span>{{ Math.abs(actualTrend).toFixed(1) }}%</span>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { TrendingUp, TrendingDown } from 'lucide-vue-next'

const props = defineProps<{
  value: number
  inverse?: boolean
}>()

const actualTrend = computed(() => props.value || 0)
</script>
