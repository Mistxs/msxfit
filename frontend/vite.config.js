import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 7801,
    // Чтобы открыть UI с iPhone по локальной сети — добавьте host:
    // host: '0.0.0.0',
    proxy: {
      '/api': 'http://127.0.0.1:7800',
      '/health': 'http://127.0.0.1:7800',
    },
  },
})
