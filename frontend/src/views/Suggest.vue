<script setup>
import { ref, onMounted } from 'vue'
import { api, todayISO } from '../api.js'

const data = ref(null)
const err = ref('')
const addedId = ref(null)
const today = todayISO()

async function load() {
  try {
    data.value = await api.balance.suggest(today)
  } catch (e) {
    err.value = e.message
  }
}
onMounted(load)

async function add(s) {
  await api.diary.add({
    date: today,
    meal_type: 'snack',
    source_type: s.type,
    food_id: s.type === 'food' ? s.id : null,
    dish_id: s.type === 'dish' ? s.id : null,
    grams: s.grams,
  })
  addedId.value = s.id
  await load()
}
</script>

<template>
  <div>
    <div class="card" v-if="data">
      <h2>Что ещё можно сегодня</h2>
      <div class="grid2">
        <div><div class="muted">Осталось ккал</div><div class="big">{{ Math.round(data.remaining.kcal) }}</div></div>
        <div><div class="muted">Остаток Б/Ж/У</div>
          <div class="big" style="font-size: 18px">{{ Math.round(data.remaining.protein) }} / {{ Math.round(data.remaining.fat) }} / {{ Math.round(data.remaining.carbs) }} г</div>
        </div>
      </div>
      <p class="hint" style="margin: 8px 0 0">Порции подобраны, чтобы уложиться в остаток ккал и добрать белок.</p>
    </div>

    <p v-if="data?.note" class="muted" style="margin-top: 12px">{{ data.note }}</p>

    <div class="card" v-for="s in data?.suggestions || []" :key="s.type + s.id">
      <div class="row between">
        <div>
          <strong>{{ s.name }}</strong>
          <span class="tag" style="margin-left: 6px">{{ s.type === 'food' ? 'продукт' : 'блюдо' }}</span>
          <div class="hint">{{ s.grams }} г · {{ s.kcal }} ккал · Б{{ s.protein }} Ж{{ s.fat }} У{{ s.carbs }}</div>
        </div>
        <button :class="{ ghost: addedId === s.id }" @click="add(s)">
          {{ addedId === s.id ? 'Добавлено ✓' : 'В дневник' }}
        </button>
      </div>
    </div>

    <p v-if="data && !data.suggestions.length" class="list-empty">Нет подходящих вариантов.</p>
    <p v-if="err" class="err">{{ err }}</p>
  </div>
</template>
