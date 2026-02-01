<template>
  <svg class="w-16 h-8" viewBox="0 0 64 32">
    <path
      :d="pathData"
      fill="none"
      :stroke="color"
      stroke-width="2"
      stroke-linecap="round"
      stroke-linejoin="round"
    />
    <defs>
      <linearGradient :id="gradientId" x1="0%" y1="0%" x2="0%" y2="100%">
        <stop offset="0%" :stop-color="color" stop-opacity="0.3" />
        <stop offset="100%" :stop-color="color" stop-opacity="0" />
      </linearGradient>
    </defs>
    <path
      v-if="pathData"
      :d="`${pathData} L 64 32 L 0 32 Z`"
      :fill="`url(#${gradientId})`"
    />
  </svg>
</template>

<script setup lang="ts">
import { computed } from 'vue'

const props = defineProps<{
  data: number[]
  color?: string
}>()

const gradientId = computed(() => `gradient-${Math.random().toString(36).substr(2, 9)}`)

const pathData = computed(() => {
  if (!props.data || props.data.length === 0) return ''
  
  // Handle single data point
  if (props.data.length === 1) {
    const y = 32 / 2 // Center vertically
    return `M 0,${y} L 64,${y}` // Draw a flat line for a single point
  }

  const max = Math.max(...props.data)
  const min = Math.min(...props.data)
  const range = max - min || 1
  const width = 64
  const height = 32
  const padding = 4
  
  const points = props.data.map((value, index) => {
    const x = (index / (props.data.length - 1)) * width
    const y = height - padding - ((value - min) / range) * (height - 2 * padding)
    return `${x.toFixed(2)},${y.toFixed(2)}`
  })
  
  return `M ${points.join(' L ')}`
})
</script>
