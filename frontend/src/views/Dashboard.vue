<script setup>
import { ref, onMounted, computed } from 'vue'
import { api, todayISO } from '../api.js'
import ProgressBar from '../components/ProgressBar.vue'

const data = ref(null)
const err = ref('')
const today = todayISO()

async function load() {
  try {
    data.value = await api.balance.get(today)
  } catch (e) {
    err.value = e.message
  }
}
onMounted(load)

const c = computed(() => data.value?.consumed || { kcal: 0, protein: 0, fat: 0, carbs: 0 })
const t = computed(() => data.value?.target || { kcal: 0, protein: 0, fat: 0, carbs: 0 })
</script>

<template>
  <div>
    <div class="card">
      <div class="row between">
        <div>
          <div class="muted">Сегодня</div>
          <div class="hint">{{ today }}</div>
        </div>
        <div style="text-align: right">
          <div class="muted">Вес</div>
          <div class="big">{{ data?.weight ?? '—' }}<span class="unit" v-if="data?.weight"> кг</span></div>
        </div>
      </div>
    </div>

    <div class="card" v-if="data">
      <h2>Питание</h2>
      <ProgressBar :value="c.kcal" :max="t.kcal" label="Калории" unit=" ккал" />
      <div style="height: 12px"></div>
      <ProgressBar :value="c.protein" :max="t.protein" label="Белок" unit=" г" color="var(--protein)" />
      <div style="height: 8px"></div>
      <ProgressBar :value="c.fat" :max="t.fat" label="Жиры" unit=" г" color="var(--fat)" />
      <div style="height: 8px"></div>
      <ProgressBar :value="c.carbs" :max="t.carbs" label="Углеводы" unit=" г" color="var(--carbs)" />
      <div class="hint" style="margin-top: 10px">
        Осталось: {{ Math.round(data.remaining.kcal) }} ккал · белок {{ Math.round(data.remaining.protein) }} г
      </div>
    </div>

    <div class="card" v-if="data">
      <h2>Активность</h2>
      <div class="grid2">
        <div>
          <div class="muted">🚶 Шаги</div>
          <div class="big">{{ data.activity.steps }}</div>
        </div>
        <div>
          <div class="muted">Расход (оценка)</div>
          <div class="big">~{{ Math.round(data.activity.kcal) }}<span class="unit"> ккал</span></div>
        </div>
      </div>
      <p class="hint" style="margin: 8px 0 0">Расход — оценка, не точное число.</p>
    </div>

    <div class="card" v-if="data && data.remaining.kcal > 0">
      <RouterLink to="/suggest" style="color: var(--accent)">→ Что ещё можно сегодня съесть?</RouterLink>
    </div>

    <p v-if="err" class="err">{{ err }}</p>
    <p v-if="!data && !err" class="muted">Загрузка…</p>
  </div>
</template>
