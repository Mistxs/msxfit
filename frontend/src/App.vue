<script setup>
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'

// «Ещё» закрывается при любой смене маршрута.
const route = useRoute()
const moreOpen = ref(false)
watch(() => route.fullPath, () => { moreOpen.value = false })
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand-logo">
        <span class="brand-mistxs">mistxs</span><span class="brand-sep">|</span><span class="brand-suffix">fitness</span>
      </div>
    </header>

    <RouterView />

    <nav class="tabbar">
      <RouterLink to="/" class="tab"><span class="tab-ico">🏠</span><span class="tab-label">Сегодня</span></RouterLink>
      <RouterLink to="/diary" class="tab"><span class="tab-ico">🍽</span><span class="tab-label">Дневник</span></RouterLink>
      <RouterLink to="/suggest" class="tab"><span class="tab-ico">💡</span><span class="tab-label">Что съесть</span></RouterLink>
      <RouterLink to="/scan" class="tab"><span class="tab-ico">📷</span><span class="tab-label">Скан</span></RouterLink>
      <button class="tab" :class="{ active: moreOpen }" @click="moreOpen = !moreOpen">
        <span class="tab-ico">⋯</span><span class="tab-label">Ещё</span>
      </button>
    </nav>

    <div v-if="moreOpen" class="more-backdrop" @click="moreOpen = false"></div>
    <div v-if="moreOpen" class="more-panel">
      <RouterLink to="/foods" class="more-item">🍎 Продукты</RouterLink>
      <RouterLink to="/dishes" class="more-item">🍳 Блюда</RouterLink>
      <RouterLink to="/weight" class="more-item">⚖️ Вес</RouterLink>
      <RouterLink to="/settings" class="more-item">⚙️ Настройки</RouterLink>
    </div>
  </div>
</template>
