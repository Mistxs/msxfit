<script setup>
import { todayISO } from './api.js'
</script>

<template>
  <div class="app-shell">
    <header class="topbar">
      <div class="brand-logo">
        <span class="brand-mistxs">mistxs</span><span class="brand-sep">|</span><span class="brand-suffix">fitness</span>
      </div>
      <nav class="nav">
        <RouterLink to="/">Сегодня</RouterLink>
        <RouterLink to="/diary">Дневник</RouterLink>
        <RouterLink to="/suggest">Что съесть</RouterLink>
        <RouterLink to="/scan">Скан</RouterLink>
        <RouterLink to="/foods">Продукты</RouterLink>
        <RouterLink to="/dishes">Блюда</RouterLink>
        <RouterLink to="/weight">Вес</RouterLink>
        <RouterLink to="/settings">Настройки</RouterLink>
      </nav>
    </header>

    <RouterView />
  </div>
</template>
