<script setup>
import { computed } from 'vue'

const props = defineProps({
  points: { type: Array, default: () => [] }, // [{ x: '2026-09-01', y: 108.2 }]
  width: { type: Number, default: 600 },
  height: { type: Number, default: 160 },
})

const poly = computed(() => {
  const pts = props.points
  if (!pts.length) return ''
  const ys = pts.map((p) => p.y)
  const minY = Math.min(...ys)
  const maxY = Math.max(...ys)
  const rangeY = maxY - minY || 1
  const pad = 8
  const stepX = (props.width - pad * 2) / Math.max(1, pts.length - 1)
  const h = props.height - pad * 2
  return pts
    .map((p, i) => {
      const x = pad + i * stepX
      const y = pad + (1 - (p.y - minY) / rangeY) * h
      return `${x.toFixed(1)},${y.toFixed(1)}`
    })
    .join(' ')
})
</script>

<template>
  <svg :viewBox="`0 0 ${width} ${height}`" width="100%" :height="height" style="display:block">
    <polyline :points="poly" fill="none" stroke="var(--accent)" stroke-width="2" stroke-linejoin="round" />
  </svg>
</template>
