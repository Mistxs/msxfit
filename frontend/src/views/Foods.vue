<script setup>
import { ref, onMounted, computed } from 'vue'
import { api } from '../api.js'

const foods = ref([])
const q = ref('')
const err = ref('')
const editing = ref(null)
const form = ref(blank())

function blank() {
  return { name: '', brand: '', kcal: 0, protein: 0, fat: 0, carbs: 0 }
}

async function load() {
  const r = await api.foods.list(q.value)
  foods.value = r.foods
}
onMounted(load)

function edit(f) {
  editing.value = f.id
  form.value = { ...f }
}
function reset() {
  editing.value = null
  form.value = blank()
}

async function save() {
  try {
    if (editing.value) {
      await api.foods.update(editing.value, form.value)
    } else {
      await api.foods.create(form.value)
    }
    reset()
    await load()
  } catch (e) {
    err.value = e.message
  }
}

async function remove(id) {
  await api.foods.remove(id)
  await load()
}
</script>

<template>
  <div>
    <div class="card">
      <h2>{{ editing ? 'Редактировать продукт' : 'Новый продукт' }}</h2>
      <label>Название</label>
      <input v-model="form.name" placeholder="Напр. Творог 5%" />
      <label>Бренд (необязательно)</label>
      <input v-model="form.brand" />
      <p class="hint">Значения — на 100 г.</p>
      <div class="grid2">
        <div><label>Калории</label><input type="number" step="0.1" v-model.number="form.kcal" /></div>
        <div><label>Белки</label><input type="number" step="0.1" v-model.number="form.protein" /></div>
        <div><label>Жиры</label><input type="number" step="0.1" v-model.number="form.fat" /></div>
        <div><label>Углеводы</label><input type="number" step="0.1" v-model.number="form.carbs" /></div>
      </div>
      <div class="row" style="margin-top: 10px; gap: 8px">
        <button @click="save">Сохранить</button>
        <button class="ghost" v-if="editing" @click="reset">Отмена</button>
      </div>
      <p v-if="err" class="err">{{ err }}</p>
    </div>

    <div class="card">
      <h2>Справочник продуктов</h2>
      <input v-model="q" placeholder="Поиск…" @input="load" />
      <div class="table-wrap" v-if="foods.length">
      <table>
        <thead><tr><th>Название</th><th>ккал</th><th>Б/Ж/У</th><th></th></tr></thead>
        <tbody>
          <tr v-for="f in foods" :key="f.id">
            <td @click="edit(f)" style="cursor: pointer">{{ f.name }}<span v-if="f.brand" class="muted"> · {{ f.brand }}</span></td>
            <td>{{ f.kcal }}</td>
            <td class="muted">{{ f.protein }}/{{ f.fat }}/{{ f.carbs }}</td>
            <td><button class="ghost" style="padding: 2px 8px" @click="remove(f.id)">✕</button></td>
          </tr>
        </tbody>
      </table>
      </div>
      <p v-else class="list-empty">Ничего не найдено.</p>
    </div>
  </div>
</template>
