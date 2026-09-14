<script setup>
import { ref, onMounted } from 'vue'
import { api } from '../api.js'

const form = ref(null)
const err = ref('')
const ok = ref(false)

async function load() {
  form.value = await api.profile.get()
}
onMounted(load)

async function save() {
  ok.value = false
  err.value = ''
  try {
    await api.profile.update(form.value)
    ok.value = true
  } catch (e) {
    err.value = e.message
  }
}
</script>

<template>
  <div>
    <div class="card" v-if="form">
      <h2>Дневные цели</h2>
      <div class="grid2">
        <div><label>Калории, ккал</label><input type="number" step="1" v-model.number="form.target_kcal" /></div>
        <div><label>Белки, г</label><input type="number" step="1" v-model.number="form.target_protein_g" /></div>
        <div><label>Жиры, г</label><input type="number" step="1" v-model.number="form.target_fat_g" /></div>
        <div><label>Углеводы, г</label><input type="number" step="1" v-model.number="form.target_carbs_g" /></div>
      </div>

      <h2 style="margin-top: 16px">Профиль</h2>
      <div class="grid2">
        <div><label>Рост, см</label><input type="number" step="1" v-model.number="form.height_cm" /></div>
        <div><label>Стартовый вес, кг</label><input type="number" step="0.1" v-model.number="form.start_weight_kg" /></div>
      </div>
      <label>Уровень активности</label>
      <select v-model="form.activity_level">
        <option value="low">Низкий</option>
        <option value="medium">Средний</option>
        <option value="high">Высокий</option>
      </select>

      <button style="margin-top: 12px" @click="save">Сохранить</button>
      <span v-if="ok" style="color: var(--good); margin-left: 10px">Сохранено ✓</span>
      <p v-if="err" class="err">{{ err }}</p>
    </div>
    <p v-else class="muted">Загрузка…</p>
  </div>
</template>
