import { createApp } from 'vue'
import App from './App.vue'
import router from './router'

// 1. IMPORTANTE: O CSS do Leaflet TEM que vir antes
import 'leaflet/dist/leaflet.css'
import 'leaflet.markercluster/dist/MarkerCluster.css'
import 'leaflet.markercluster/dist/MarkerCluster.Default.css'

// 2. O seu CSS Global (Garante que o reset funcione)
import './assets/global.css' 

const app = createApp(App)

app.use(router)

app.mount('#app')