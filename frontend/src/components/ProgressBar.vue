<script setup>
import { computed } from 'vue'

const props = defineProps({
  value: { type: Number, default: 0 },
  max: { type: Number, default: 100 },
  color: { type: String, default: 'var(--accent)' },
  label: { type: String, default: '' },
  unit: { type: String, default: '' },
})

const pct = computed(() => {
  const m = props.max || 0
  if (m <= 0) return 0
  return Math.max(0, Math.min(100, (props.value / m) * 100))
})
const over = computed(() => props.value > props.max)
</script>

<template>
  <div>
    <div class="spread">
      <span class="muted">{{ label }}</span>
      <span>
        <strong>{{ Math.round(value) }}</strong><span class="unit">{{ unit }}</span>
        <span class="unit"> / {{ Math.round(max) }}{{ unit }}</span>
        <span v-if="over" class="unit" style="color: var(--bad)"> ⚠ +{{ Math.round(value - max) }}{{ unit }}</span>
      </span>
    </div>
    <div class="bar">
      <span :style="{ width: pct + '%', background: over ? 'var(--bad)' : color }"></span>
    </div>
  </div>
</template>
