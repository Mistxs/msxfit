<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from '../api.js'

const dishes = ref([])
const foods = ref([])
const err = ref('')
const editing = ref(null)
const form = ref(blank())

function blank() {
  return { name: '', portion_g: 100, manual: false, kcal: 0, protein: 0, fat: 0, carbs: 0, ingredients: [] }
}

async function load() {
  const [d, f] = await Promise.all([api.dishes.list(), api.foods.list()])
  dishes.value = d.dishes
  foods.value = f.foods
}
onMounted(load)

function reset() {
  editing.value = null
  form.value = blank()
}

function edit(d) {
  editing.value = d.id
  form.value = {
    name: d.name, portion_g: d.portion_g, manual: d.manual,
    kcal: d.kcal, protein: d.protein, fat: d.fat, carbs: d.carbs,
    ingredients: (d.ingredients || []).map((i) => ({ food_id: i.food_id, grams: i.grams })),
  }
}

function addIngredient() {
  form.value.ingredients.push({ food_id: null, grams: 100 })
}
function removeIngredient(i) {
  form.value.ingredients.splice(i, 1)
}

const preview = computed(() => {
  if (form.value.manual) {
    const p = form.value.portion_g || 100
    return {
      per100: { kcal: form.value.kcal * 100 / p, protein: form.value.protein * 100 / p,
                fat: form.value.fat * 100 / p, carbs: form.value.carbs * 100 / p },
      perPortion: { kcal: form.value.kcal, protein: form.value.protein, fat: form.value.fat, carbs: form.value.carbs },
    }
  }
  const t = { kcal: 0, protein: 0, fat: 0, carbs: 0, weight: 0 }
  for (const ing of form.value.ingredients) {
    const f = foods.value.find((x) => x.id === ing.food_id)
    if (!f) continue
    const g = ing.grams || 0
    t.kcal += (f.kcal * g) / 100
    t.protein += (f.protein * g) / 100
    t.fat += (f.fat * g) / 100
    t.carbs += (f.carbs * g) / 100
    t.weight += g
  }
  const w = t.weight || 0
  const per100 = w > 0
    ? { kcal: (t.kcal * 100) / w, protein: (t.protein * 100) / w, fat: (t.fat * 100) / w, carbs: (t.carbs * 100) / w }
    : { kcal: 0, protein: 0, fat: 0, carbs: 0 }
  const p = form.value.portion_g || 100
  return {
    per100,
    perPortion: { kcal: (per100.kcal * p) / 100, protein: (per100.protein * p) / 100,
                  fat: (per100.fat * p) / 100, carbs: (per100.carbs * p) / 100 },
  }
})

async function save() {
  try {
    const payload = {
      name: form.value.name, portion_g: form.value.portion_g, manual: form.value.manual,
      kcal: form.value.kcal, protein: form.value.protein, fat: form.value.fat, carbs: form.value.carbs,
      ingredients: form.value.manual ? [] : form.value.ingredients.filter((i) => i.food_id),
    }
    if (editing.value) await api.dishes.update(editing.value, payload)
    else await api.dishes.create(payload)
    reset()
    await load()
  } catch (e) {
    err.value = e.message
  }
}

async function remove(id) {
  await api.dishes.remove(id)
  await load()
}
</script>

<template>
  <div>
    <div class="card">
      <h2>{{ editing ? 'Редактировать блюдо' : 'Новое блюдо' }}</h2>
      <label>Название</label>
      <input v-model="form.name" placeholder="Напр. Фрикасе из курицы с гречкой" />

      <div class="grid2">
        <div><label>Вес порции, г</label><input type="number" step="1" v-model.number="form.portion_g" /></div>
        <div style="display:flex; align-items:flex-end">
          <label style="margin:0"><input type="checkbox" v-model="form.manual" style="width:auto" /> Ввести КБЖУ вручную (на порцию)</label>
        </div>
      </div>

      <div v-if="form.manual" class="grid2" style="margin-top: 8px">
        <div><label>Ккал (порция)</label><input type="number" step="0.1" v-model.number="form.kcal" /></div>
        <div><label>Белки</label><input type="number" step="0.1" v-model.number="form.protein" /></div>
        <div><label>Жиры</label><input type="number" step="0.1" v-model.number="form.fat" /></div>
        <div><label>Углеводы</label><input type="number" step="0.1" v-model.number="form.carbs" /></div>
      </div>

      <div v-else>
        <h2 style="margin-top: 12px">Ингредиенты</h2>
        <div v-for="(ing, i) in form.ingredients" :key="i" class="ing-row" style="margin-bottom: 6px">
          <select v-model="ing.food_id">
            <option :value="null" disabled>— продукт —</option>
            <option v-for="f in foods" :key="f.id" :value="f.id">{{ f.name }} ({{ f.kcal }} ккал)</option>
          </select>
          <input type="number" step="1" v-model.number="ing.grams" placeholder="г" />
          <button class="ghost" style="padding: 8px 10px" @click="removeIngredient(i)">✕</button>
        </div>
        <button class="ghost" @click="addIngredient">+ ингредиент</button>
      </div>

      <div class="card" style="background: var(--surface-2); margin-top: 12px">
        <div class="spread">
          <span class="muted">На 100 г</span>
          <span>{{ Math.round(preview.per100.kcal) }} ккал · Б{{ Math.round(preview.per100.protein) }} Ж{{ Math.round(preview.per100.fat) }} У{{ Math.round(preview.per100.carbs) }}</span>
        </div>
        <div class="spread" style="margin-top: 6px">
          <span class="muted">На порцию ({{ form.portion_g }} г)</span>
          <span>{{ Math.round(preview.perPortion.kcal) }} ккал · Б{{ Math.round(preview.perPortion.protein) }} Ж{{ Math.round(preview.perPortion.fat) }} У{{ Math.round(preview.perPortion.carbs) }}</span>
        </div>
      </div>

      <div class="row" style="margin-top: 10px; gap: 8px">
        <button @click="save">Сохранить</button>
        <button class="ghost" v-if="editing" @click="reset">Отмена</button>
      </div>
      <p v-if="err" class="err">{{ err }}</p>
    </div>

    <div class="card">
      <h2>Готовые блюда</h2>
      <div class="table-wrap" v-if="dishes.length">
      <table>
        <thead><tr><th>Блюдо</th><th style="text-align:right">ккал/порц</th><th></th></tr></thead>
        <tbody>
          <tr v-for="d in dishes" :key="d.id">
            <td @click="edit(d)" style="cursor: pointer">{{ d.name }}<span class="muted"> · {{ d.portion_g }} г</span></td>
            <td style="text-align:right">{{ Math.round(d.per_portion.kcal) }}</td>
            <td><button class="ghost" style="padding: 2px 8px" @click="remove(d.id)">✕</button></td>
          </tr>
        </tbody>
      </table>
      </div>
      <p v-else class="list-empty">Пока нет блюд.</p>
    </div>
  </div>
</template>
