import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
import './assets/main.css'
import { bootstrapTheme } from '@/utils/themeBootstrap'
import { bootstrapA11y } from '@/utils/a11yBootstrap'

bootstrapTheme()
bootstrapA11y()

const app = createApp(App)

app.use(createPinia())
app.use(router)

app.mount('#app')
