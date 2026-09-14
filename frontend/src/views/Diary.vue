<script setup>
import { ref, onMounted, computed, watch } from 'vue'
import { api, todayISO } from '../api.js'

const date = ref(todayISO())
const diary = ref(null)
const foods = ref([])
const dishes = ref([])
const err = ref('')

const mealTypes = [
  { key: 'breakfast', label: 'Завтрак' },
  { key: 'lunch', label: 'Обед' },
  { key: 'dinner', label: 'Ужин' },
  { key: 'snack', label: 'Перекус' },
  { key: 'other', label: 'Другое' },
]

const form = ref({
  meal_type: 'breakfast',
  source: 'food',
  food_id: null,
  dish_id: null,
  grams: 100,
})

async function loadRefs() {
  const [f, d] = await Promise.all([api.foods.list(), api.dishes.list()])
  foods.value = f.foods
  dishes.value = d.dishes
}
async function load() {
  try {
    diary.value = await api.diary.get(date.value)
  } catch (e) {
    err.value = e.message
  }
}
onMounted(async () => {
  await loadRefs()
  await load()
})
watch(date, load)

async function add() {
  const item = {
    date: date.value,
    meal_type: form.value.meal_type,
    source_type: form.value.source,
    food_id: form.value.source === 'food' ? form.value.food_id : null,
    dish_id: form.value.source === 'dish' ? form.value.dish_id : null,
    grams: parseFloat(form.value.grams) || 0,
  }
  if ((item.source_type === 'food' && !item.food_id) || (item.source_type === 'dish' && !item.dish_id)) {
    err.value = 'Выберите продукт или блюдо'
    return
  }
  try {
    await api.diary.add(item)
    form.value.grams = 100
    err.value = ''
    await load()
  } catch (e) {
    err.value = e.message
  }
}

async function remove(id) {
  await api.diary.remove(id)
  await load()
}

const totals = computed(() => diary.value?.totals || { kcal: 0, protein: 0, fat: 0, carbs: 0 })
const groups = computed(() => diary.value?.items || {})
const mealsWithItems = computed(() => mealTypes.filter((m) => (groups.value[m.key] || []).length))
</script>

<template>
  <div>
    <div class="card">
      <label>Дата</label>
      <input type="date" v-model="date" />
    </div>

    <div class="card">
      <h2>Добавить приём пищи</h2>
      <div class="chips">
        <button
          v-for="m in mealTypes"
          :key="m.key"
          :class="{ active: form.meal_type === m.key }"
          @click="form.meal_type = m.key"
        >{{ m.label }}</button>
      </div>

      <div class="chips" style="margin-top: 10px">
        <button :class="{ active: form.source === 'food' }" @click="form.source = 'food'">Продукт</button>
        <button :class="{ active: form.source === 'dish' }" @click="form.source = 'dish'">Блюдо</button>
      </div>

      <label>{{ form.source === 'food' ? 'Продукт' : 'Блюдо' }}</label>
      <input
        v-if="form.source === 'food'"
        list="foods-list"
        placeholder="Начните вводить название…"
        @input="(e) => form.food_id = foods.find((f) => f.name === e.target.value)?.id || null"
      />
      <select v-else v-model="form.dish_id">
        <option :value="null" disabled>— выберите блюдо —</option>
        <option v-for="d in dishes" :key="d.id" :value="d.id">{{ d.name }}</option>
      </select>
      <datalist id="foods-list">
        <option v-for="f in foods" :key="f.id" :value="f.name">
          {{ f.kcal }} ккал · Б{{ f.protein }} Ж{{ f.fat }} У{{ f.carbs }}
        </option>
      </datalist>

      <label>Грамм</label>
      <input type="number" min="0" step="1" v-model.number="form.grams" />
      <button style="margin-top: 10px" @click="add">Добавить</button>
      <p v-if="err" class="err">{{ err }}</p>
    </div>

    <div class="card" v-if="diary">
      <h2>Итог за день</h2>
      <div class="spread">
        <span><strong>{{ Math.round(totals.kcal) }}</strong><span class="unit"> ккал</span></span>
        <span class="unit">Б {{ Math.round(totals.protein) }} · Ж {{ Math.round(totals.fat) }} · У {{ Math.round(totals.carbs) }}</span>
      </div>
    </div>

    <div class="card" v-for="m in mealsWithItems" :key="m.key">
      <h2>{{ m.label }}</h2>
      <table>
        <thead>
          <tr><th>Что</th><th style="text-align:right">г</th><th style="text-align:right">ккал</th><th style="text-align:right">Б</th><th></th></tr>
        </thead>
        <tbody>
          <tr v-for="it in groups[m.key]" :key="it.id">
            <td>{{ it.label }}</td>
            <td style="text-align:right">{{ it.grams }}</td>
            <td style="text-align:right">{{ it.kcal }}</td>
            <td style="text-align:right">{{ it.protein }}</td>
            <td style="text-align:right"><button class="ghost" style="padding: 2px 8px" @click="remove(it.id)">✕</button></td>
          </tr>
        </tbody>
      </table>
    </div>

    <p v-if="diary && !mealTypes.some((m) => groups[m.key]?.length)" class="list-empty">Пока ничего не записано.</p>
  </div>
</template>
