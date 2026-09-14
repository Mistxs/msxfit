import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from './views/Dashboard.vue'
import Diary from './views/Diary.vue'
import Foods from './views/Foods.vue'
import Dishes from './views/Dishes.vue'
import Weight from './views/Weight.vue'
import Suggest from './views/Suggest.vue'
import Scan from './views/Scan.vue'
import Settings from './views/Settings.vue'

export default createRouter({
  history: createWebHistory(),
  routes: [
    { path: '/', name: 'dashboard', component: Dashboard },
    { path: '/diary', name: 'diary', component: Diary },
    { path: '/foods', name: 'foods', component: Foods },
    { path: '/dishes', name: 'dishes', component: Dishes },
    { path: '/weight', name: 'weight', component: Weight },
    { path: '/suggest', name: 'suggest', component: Suggest },
    { path: '/scan', name: 'scan', component: Scan },
    { path: '/settings', name: 'settings', component: Settings },
  ],
})
