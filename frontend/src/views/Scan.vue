<script setup>
import { ref } from 'vue'
import { api } from '../api.js'

const preview = ref('')
const parsed = ref(null)
const err = ref('')
const saved = ref('')
const form = ref({ name: '', kcal: 0, protein: 0, fat: 0, carbs: 0 })

async function onFile(e) {
  const file = e.target.files && e.target.files[0]
  if (!file) return
  preview.value = URL.createObjectURL(file)
  err.value = ''
  parsed.value = null
  try {
    const r = await api.ocr.label(file)
    parsed.value = r.parsed
    const p = r.parsed
    if (p.kcal != null) form.value.kcal = p.kcal
    if (p.protein != null) form.value.protein = p.protein
    if (p.fat != null) form.value.fat = p.fat
    if (p.carbs != null) form.value.carbs = p.carbs
  } catch (e2) {
    err.value = e2.message
  }
}

async function save() {
  try {
    await api.foods.create({ ...form.value, brand: '' })
    saved.value = 'Сохранено в справочник: ' + form.value.name
    form.value = { name: '', kcal: 0, protein: 0, fat: 0, carbs: 0 }
    parsed.value = null
    preview.value = ''
  } catch (e) {
    err.value = e.message
  }
}
</script>

<template>
  <div>
    <div class="card">
      <h2>Скан этикетки</h2>
      <p class="hint">Сфотографируйте этикетку продукта — КБЖУ подставятся автоматически. Проверьте и сохраните в справочник.</p>
      <input type="file" accept="image/*" capture="environment" @change="onFile" />
      <img v-if="preview" :src="preview" style="max-width: 100%; border-radius: 10px; margin-top: 10px" />
      <p v-if="parsed?.note" class="hint" style="margin-top: 10px">{{ parsed.note }}</p>
      <details v-if="parsed?.raw_text" style="margin-top: 10px">
        <summary class="hint">Распознанный текст<span v-if="parsed.backend"> · {{ parsed.backend }}</span></summary>
        <pre class="hint" style="white-space: pre-wrap; background: var(--surface-2); padding: 8px; border-radius: 8px; overflow: auto; max-height: 220px">{{ parsed.raw_text }}</pre>
      </details>
      <p v-if="err" class="err">{{ err }}</p>
    </div>

    <div class="card" v-if="parsed">
      <h2>Проверьте значения (на 100 г)</h2>
      <label>Название продукта</label>
      <input v-model="form.name" placeholder="Напр. Творог 5%" />
      <div class="grid2">
        <div><label>Калории</label><input type="number" step="0.1" v-model.number="form.kcal" /></div>
        <div><label>Белки</label><input type="number" step="0.1" v-model.number="form.protein" /></div>
        <div><label>Жиры</label><input type="number" step="0.1" v-model.number="form.fat" /></div>
        <div><label>Углеводы</label><input type="number" step="0.1" v-model.number="form.carbs" /></div>
      </div>
      <button style="margin-top: 10px" @click="save">Сохранить в справочник</button>
      <p v-if="saved" style="color: var(--good); margin-top: 8px">{{ saved }}</p>
    </div>
  </div>
</template>
