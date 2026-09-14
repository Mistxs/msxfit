<script setup>
import { ref, onMounted, computed } from 'vue'
import { api, todayISO } from '../api.js'
import LineChart from '../components/LineChart.vue'

const entries = ref([])
const weeklyAvg = ref(null)
const totalChange = ref(0)
const err = ref('')
const form = ref({ date: todayISO(), weight_kg: '', note: '' })

async function load() {
  const r = await api.weight.list()
  entries.value = r.entries
  weeklyAvg.value = r.weekly_avg
  totalChange.value = r.total_change
}
onMounted(load)

async function add() {
  try {
    await api.weight.add({
      date: form.value.date,
      weight_kg: parseFloat(form.value.weight_kg),
      note: form.value.note,
    })
    form.value.weight_kg = ''
    form.value.note = ''
    await load()
  } catch (e) {
    err.value = e.message
  }
}

async function remove(id) {
  await api.weight.remove(id)
  await load()
}

const chartPoints = computed(() => entries.value.map((e) => ({ x: e.date, y: e.weight_kg })))
const latest = computed(() => entries.value[entries.value.length - 1])
const first = computed(() => entries.value[0])
</script>

<template>
  <div>
    <div class="card">
      <h2>Запись веса</h2>
      <div class="grid2">
        <div><label>Дата</label><input type="date" v-model="form.date" /></div>
        <div><label>Вес, кг</label><input type="number" step="0.1" v-model.number="form.weight_kg" /></div>
      </div>
      <label>Заметка</label>
      <input v-model="form.note" placeholder="необязательно" />
      <button style="margin-top: 10px" @click="add">Добавить</button>
      <p v-if="err" class="err">{{ err }}</p>
    </div>

    <div class="card" v-if="latest">
      <div class="grid2">
        <div><div class="muted">Текущий вес</div><div class="big">{{ latest.weight_kg }}<span class="unit"> кг</span></div></div>
        <div><div class="muted">Среднее за неделю</div><div class="big">{{ weeklyAvg ?? '—' }}<span class="unit" v-if="weeklyAvg"> кг</span></div></div>
      </div>
      <div class="spread" style="margin-top: 8px">
        <span class="muted">С начала записей</span>
        <span :style="{ color: totalChange < 0 ? 'var(--good)' : 'var(--bad)' }">
          {{ totalChange > 0 ? '+' : '' }}{{ totalChange }} кг
        </span>
      </div>
    </div>

    <div class="card" v-if="chartPoints.length > 1">
      <h2>Динамика веса</h2>
      <LineChart :points="chartPoints" />
    </div>

    <div class="card" v-if="entries.length">
      <h2>История</h2>
      <div class="table-wrap">
      <table>
        <thead><tr><th>Дата</th><th>Вес</th><th></th></tr></thead>
        <tbody>
          <tr v-for="e in [...entries].reverse()" :key="e.id">
            <td>{{ e.date }}</td>
            <td>{{ e.weight_kg }} кг</td>
            <td><button class="ghost" style="padding: 2px 8px" @click="remove(e.id)">✕</button></td>
          </tr>
        </tbody>
      </table>
      </div>
    </div>
    <p v-else class="list-empty">Записей пока нет.</p>
  </div>
</template>
