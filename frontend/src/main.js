import { createApp } from 'vue'
import { Quasar, Dark } from 'quasar'
import { createPinia } from 'pinia'

import App from './App.vue'

import 'quasar/src/css/index.sass'
import '@quasar/extras/material-icons/material-icons.css'

Dark.set(true)

const app = createApp(App)
app.use(Quasar, { plugins: {} })
app.use(createPinia())
app.mount('#app')
