<template>
  <div class="dashboard-container">
    
    <aside class="sidebar">
      <div class="sidebar-header">
        <h2 class="title">Mapa de Redes</h2>
        <p class="subtitle">Gerenciamento de cobertura e vendas</p>
      </div>

      <div class="sidebar-content">
        
        <section class="filter-group">
          <label class="section-label">Situação de Venda</label>
          <div class="kpi-grid">
            <label class="kpi-card success" :class="{ active: filtros.vendaSim }">
              <input type="checkbox" v-model="filtros.vendaSim" hidden>
              <div class="kpi-info">
                <span class="kpi-title">Com Venda</span>
                <span class="kpi-value">{{ stats.comVenda }}</span>
              </div>
              <div class="kpi-indicator"></div>
            </label>
            
            <label class="kpi-card danger" :class="{ active: filtros.vendaNao }">
              <input type="checkbox" v-model="filtros.vendaNao" hidden>
              <div class="kpi-info">
                <span class="kpi-title">Sem Venda</span>
                <span class="kpi-value">{{ stats.semVenda }}</span>
              </div>
              <div class="kpi-indicator"></div>
            </label>
          </div>
        </section>

        <section class="filter-group flex-grow">
          <div class="group-header">
            <label class="section-label">Redes <span class="badge-count">{{ listaRedes.length }}</span></label>
            <button class="btn-text" @click="toggleTodasRedes">
              {{ todosRedesChecked ? 'Desmarcar' : 'Todas' }}
            </button>
          </div>
          
          <div class="scroll-list">
            <div 
              v-for="rede in listaRedes" 
              :key="rede.nome" 
              class="list-item"
              :class="{ 'dimmed': rede.count === 0 }"
            >
              <label class="checkbox-wrapper">
                <input type="checkbox" :value="rede.nome" v-model="filtros.redesSelecionadas">
                <span class="color-marker" :style="{ backgroundColor: rede.cor }"></span>
                <span class="item-name">{{ rede.nome }}</span>
              </label>
              <span class="item-count" v-if="rede.count > 0">{{ rede.count }}</span>
            </div>
          </div>
        </section>

        <section class="filter-group flex-grow">
          <div class="group-header">
            <label class="section-label">Cobertura (Representantes)</label>
            <button class="btn-text" @click="toggleTodosReps">
              {{ filtros.repsSelecionados.length > 0 ? 'Limpar' : 'Todos' }}
            </button>
          </div>

          <div class="scroll-list">
            <div v-for="rep in listaRepresentantes" :key="rep.nome" class="list-item">
              <label class="checkbox-wrapper">
                <input 
                  type="checkbox" 
                  :value="rep.nome" 
                  v-model="filtros.repsSelecionados"
                  @change="toggleLayerRepresentante(rep.nome)"
                >
                <span class="color-marker square" :style="{ backgroundColor: rep.cor }"></span>
                <span class="item-name">{{ rep.nome }}</span>
              </label>
            </div>
          </div>
        </section>

      </div>
    </aside>

    <main class="map-wrapper">
      <div id="map"></div>
      
      <transition name="fade">
        <div v-if="loading" class="loading-overlay">
          <div class="spinner"></div>
          <span class="loading-text">Carregando dados geográficos...</span>
        </div>
      </transition>
    </main>

  </div>
</template>

<script setup>
import { ref, reactive, computed, onMounted, watch, shallowRef } from 'vue';
import L from 'leaflet';
import 'leaflet.markercluster';

// ==========================================
// LÓGICA (Mantida idêntica, apenas ajustes finos)
// ==========================================

const loading = ref(true);
const config = ref(null);
const lojasData = ref([]);
const map = shallowRef(null);
const markerClusterGroup = shallowRef(null);
const activeLayers = {}; 
let geoJsonEstados = null;
let geoJsonMunicipios = null;

const filtros = reactive({
  vendaSim: true,
  vendaNao: true,
  redesSelecionadas: [],
  repsSelecionados: []
});

// --- COMPUTEDS ---

const lojasFiltradas = computed(() => {
  return lojasData.value.filter(loja => {
    const filterVenda = (loja.teve_venda && filtros.vendaSim) || (!loja.teve_venda && filtros.vendaNao);
    const filterRede = filtros.redesSelecionadas.includes(loja.rede);
    return filterVenda && filterRede;
  });
});

const stats = computed(() => {
  let com = 0, sem = 0;
  lojasData.value.forEach(loja => {
    if (filtros.redesSelecionadas.includes(loja.rede)) {
      loja.teve_venda ? com++ : sem++;
    }
  });
  return { comVenda: com, semVenda: sem };
});

const listaRedes = computed(() => {
  const redesMap = new Map();
  // 1. Coleta todas as redes
  lojasData.value.forEach(loja => {
    if (!redesMap.has(loja.rede)) {
      redesMap.set(loja.rede, { 
        nome: loja.rede, 
        cor: stringToHslColor(loja.rede), 
        count: 0 
      });
    }
  });
  // 2. Conta baseado no filtro de venda
  lojasData.value.forEach(loja => {
    const passaVenda = (loja.teve_venda && filtros.vendaSim) || (!loja.teve_venda && filtros.vendaNao);
    if (passaVenda && redesMap.has(loja.rede)) {
      redesMap.get(loja.rede).count++;
    }
  });
  return Array.from(redesMap.values()).sort((a, b) => a.nome.localeCompare(b.nome));
});

const todosRedesChecked = computed(() => {
    return listaRedes.value.length > 0 && filtros.redesSelecionadas.length === listaRedes.value.length;
});

const listaRepresentantes = computed(() => {
  if (!config.value) return [];
  const estaduais = Object.keys(config.value.cobertura_estados);
  const municipais = config.value.reps_municipais;
  const todos = [...new Set([...estaduais, ...municipais])].sort();
  return todos.map(nome => ({
    nome,
    cor: config.value.cores[nome] || stringToHslColor(nome)
  }));
});

// --- ACTIONS ---

function toggleTodasRedes() {
  if (todosRedesChecked.value) {
    filtros.redesSelecionadas = [];
  } else {
    filtros.redesSelecionadas = listaRedes.value.map(r => r.nome);
  }
}

function toggleTodosReps() {
  if (filtros.repsSelecionados.length > 0) {
    filtros.repsSelecionados = [];
  } else {
    filtros.repsSelecionados = listaRepresentantes.value.map(r => r.nome);
  }
  // Sincroniza layers
  listaRepresentantes.value.forEach(r => {
    const isAtivo = !!activeLayers[r.nome];
    const deveEstarAtivo = filtros.repsSelecionados.includes(r.nome);
    if (isAtivo !== deveEstarAtivo) toggleLayerRepresentante(r.nome);
  });
}

function stringToHslColor(str) {
  let hash = 0;
  for (let i = 0; i < str.length; i++) hash = str.charCodeAt(i) + ((hash << 5) - hash);
  const h = Math.abs(hash % 360);
  return `hsl(${h}, 60%, 45%)`; // Saturação ajustada para o tema
}

// --- LIFECYCLE ---

onMounted(async () => {
  initMap();
  try {
    // Carrega Config
    const resConfig = await fetch('/data/config_redes.json');
    config.value = await resConfig.json();
    
    // Carrega Lojas
    const resLojas = await fetch('http://127.0.0.1:8000/api/lojas_rede/');    const data = await resLojas.json();
    lojasData.value = data;
    filtros.redesSelecionadas = [...new Set(data.map(d => d.rede))];
  } catch (err) {
    console.error("Erro dados:", err);
  } finally {
    loading.value = false;
  }
});

function initMap() {
  map.value = L.map('map', { zoomControl: false }).setView([-15.7801, -47.9292], 4);
  
  // Tile Layer clean (CartoDB Positron combina muito com o tema Ledax)
  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; OpenStreetMap &copy; CARTO',
    subdomains: 'abcd',
    maxZoom: 19
  }).addTo(map.value);

  L.control.zoom({ position: 'topright' }).addTo(map.value);
  markerClusterGroup.value = L.markerClusterGroup({
    showCoverageOnHover: false,
    maxClusterRadius: 50
  });
  map.value.addLayer(markerClusterGroup.value);
}

watch(lojasFiltradas, (novasLojas) => {
  if (!markerClusterGroup.value) return;
  markerClusterGroup.value.clearLayers();
  
  const markers = novasLojas.map(item => {
    if (!item.latitude || !item.longitude) return null;
    const color = stringToHslColor(item.rede);
    
    // Ícone CSS Puro
    const icon = L.divIcon({
      className: 'custom-pin',
      html: `<span style="background-color: ${color};"></span>`,
      iconSize: [14, 14],
      iconAnchor: [7, 7]
    });

    const m = L.marker([item.latitude, item.longitude], { icon });
    // Popup estilizado via CSS global
    m.bindPopup(`
      <div style="font-weight: 600; color: var(--ledax); margin-bottom: 4px;">${item.rede}</div>
      <div style="font-size: 12px; color: #64748b; margin: 4px 0; border-top: 1px solid #eee; padding-top: 4px;">
        ${item.endereco || 'Endereço não informado'}
      </div>
      <div style="font-size: 13px; color: var(--text-secondary);">${item.loja}</div>
      <div style="margin-top: 6px; font-size: 12px; font-weight: bold; color: ${item.teve_venda ? '#10b981' : '#ef4444'}">
        ${item.teve_venda ? 'Venda Realizada' : 'Sem Venda'}
      </div>
    `);
    return m;
  }).filter(Boolean);
  
  markerClusterGroup.value.addLayers(markers);
});

// --- LÓGICA DE LAYERS DE COBERTURA ---

async function toggleLayerRepresentante(repNome) {
  if (activeLayers[repNome]) {
    map.value.removeLayer(activeLayers[repNome]);
    delete activeLayers[repNome];
    return;
  }
  if (!filtros.repsSelecionados.includes(repNome)) return;

  loading.value = true;
  const isMunicipal = config.value.reps_municipais.includes(repNome);

  if (isMunicipal) {
    if (!geoJsonMunicipios) geoJsonMunicipios = await (await fetch('/static/brasil_municipios.geojson')).json();
    adicionarCamadaMunicipal(repNome);
  } else {
    if (!geoJsonEstados) geoJsonEstados = await (await fetch('/static/brasil_estados.geojson')).json();
    adicionarCamadaEstadual(repNome);
  }
  loading.value = false;
}

function adicionarCamadaEstadual(repNome) {
  const estadosDoRep = config.value.cobertura_estados[repNome] || [];
  const corBase = config.value.cores[repNome] || stringToHslColor(repNome);
  
  const layer = L.geoJSON(geoJsonEstados, {
    filter: (f) => estadosDoRep.includes(f.properties.sigla),
    style: { fillColor: corBase, weight: 1, color: '#fff', fillOpacity: 0.5 }
  });
  layer.addTo(map.value);
  activeLayers[repNome] = layer;
}

function adicionarCamadaMunicipal(repNome) {
  const corBase = config.value.cores[repNome] || stringToHslColor(repNome);
  const layer = L.geoJSON(geoJsonMunicipios, {
    style: { fillColor: corBase, weight: 0.2, color: '#fff', fillOpacity: 0.6 },
    filter: (f) => {
      const nomeMuni = f.properties.name;
      const ufNome = f.properties.uf_municipio.split(' - ')[0];
      
      if (repNome === "ERNESTO (LLAMPE)") return config.value.municipios_especificos.ernesto.includes(nomeMuni);
      if (repNome === "CLECIO SALVIANO") return ufNome === 'São Paulo' && config.value.municipios_especificos.capital_sp.includes(nomeMuni);
      if (repNome === "MARCOS BARIANO") {
        return (ufNome === 'Alagoas') || (ufNome === 'São Paulo' && config.value.municipios_especificos.ribeirao_campinas.includes(nomeMuni));
      }
      if (repNome === "SEM COBERTURA") return filterSemCobertura(nomeMuni, ufNome);
      return false;
    }
  });
  layer.addTo(map.value);
  activeLayers[repNome] = layer;
}

function filterSemCobertura(nome, estado) {
  const ufsEstaduais = getUfsCobertasPorEstaduais();
  if (config.value.estados_com_logica_municipal.includes(estado)) {
    return !isMunicipioCobertoPorAlguem(nome, estado);
  }
  const ESTADOS_NOMES = {'Acre':'AC','Alagoas':'AL','Amapá':'AP','Amazonas':'AM','Bahia':'BA','Ceará':'CE','Distrito Federal':'DF','Espírito Santo':'ES','Goiás':'GO','Maranhão':'MA','Mato Grosso':'MT','Mato Grosso do Sul':'MS','Minas Gerais':'MG','Pará':'PA','Paraíba':'PB','Paraná':'PR','Pernambuco':'PE','Piauí':'PI','Rio de Janeiro':'RJ','Rio Grande do Norte':'RN','Rio Grande do Sul':'RS','Rondônia':'RO','Roraima':'RR','Santa Catarina':'SC','São Paulo':'SP','Sergipe':'SE','Tocantins':'TO'};
  const ufSigla = ESTADOS_NOMES[estado] || estado;
  return !ufsEstaduais.includes(ufSigla);
}

function isMunicipioCobertoPorAlguem(nome, estado) {
  const c = config.value.municipios_especificos;
  if (c.ernesto.includes(nome)) return true;
  if (estado === 'São Paulo' && (c.capital_sp.includes(nome) || c.ribeirao_campinas.includes(nome))) return true;
  return false;
}

function getUfsCobertasPorEstaduais() {
  const ufs = new Set();
  const especiais = ["ERNESTO (LLAMPE)", "CLECIO SALVIANO", "MARCOS BARIANO", "SEM COBERTURA"];
  for (const [rep, lista] of Object.entries(config.value.cobertura_estados)) {
    if (!especiais.includes(rep)) lista.forEach(u => ufs.add(u));
  }
  if (!config.value.cobertura_estados["MARCOS BARIANO"]) ufs.add('AL');
  return Array.from(ufs);
}
</script>

<style scoped>
/* =========================================================
   ESTILOS ESPECÍFICOS DO COMPONENTE
   (Herda variáveis do global.css)
========================================================= */

.dashboard-container {
  display: flex;
  height: 100vh;
  width: 100%;
  position: relative;
}

/* --- SIDEBAR --- */
.sidebar {
  width: 320px;
  background: var(--bg-panel);
  border-right: 1px solid var(--border-subtle);
  backdrop-filter: blur(12px); /* Efeito Glass */
  display: flex;
  flex-direction: column;
  z-index: 10;
  box-shadow: var(--shadow-sm);
  transition: transform var(--ease-fast);
}

.sidebar-header {
  padding: 24px 20px;
  border-bottom: 1px solid var(--border-subtle);
}

.title {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--ledax);
  margin-bottom: 4px;
}

.subtitle {
  font-size: 0.8rem;
  color: var(--text-muted);
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 20px;
}

/* --- GRUPOS DE FILTRO --- */
.filter-group {
  margin-bottom: 24px;
  display: flex;
  flex-direction: column;
}

.filter-group.flex-grow {
  max-height: 40vh; /* Limita altura para scroll interno */
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 10px;
}

.section-label {
  font-size: 0.75rem;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  font-weight: 600;
  color: var(--text-muted);
  margin-bottom: 8px;
  display: block;
}

.btn-text {
  background: none;
  border: none;
  color: var(--accent);
  font-size: 0.75rem;
  cursor: pointer;
  font-weight: 500;
}
.btn-text:hover { text-decoration: underline; }

/* --- KPIs (Vendas) --- */
.kpi-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
}

.kpi-card {
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 12px;
  border-radius: var(--radius-sm);
  border: 1px solid var(--border-subtle);
  background: white;
  cursor: pointer;
  transition: all 0.2s ease;
  position: relative;
  overflow: hidden;
}

.kpi-card:hover {
  border-color: var(--ledax-soft);
  box-shadow: 0 2px 8px rgba(0,0,0,0.03);
}

.kpi-card.active {
  background: white;
  border-color: var(--ledax);
  box-shadow: 0 0 0 1px var(--ledax) inset;
}

.kpi-info {
  display: flex;
  flex-direction: column;
}

.kpi-title {
  font-size: 0.75rem;
  color: var(--text-secondary);
}

.kpi-value {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--text-main);
  line-height: 1.2;
}

.kpi-indicator {
  width: 8px;
  height: 8px;
  border-radius: 50%;
}

.kpi-card.success .kpi-indicator { background: #10b981; }
.kpi-card.danger .kpi-indicator { background: #ef4444; }

/* --- LISTAS SCROLLÁVEIS --- */
.scroll-list {
  flex: 1;
  overflow-y: auto;
  padding-right: 4px; /* Espaço pro scrollbar */
}

.list-item {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 6px 0;
  border-bottom: 1px solid transparent;
  transition: opacity 0.2s;
}
.list-item.dimmed { opacity: 0.4; }

.checkbox-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 0.9rem;
  color: var(--text-secondary);
  width: 100%;
}

.checkbox-wrapper:hover {
  color: var(--ledax);
}

.checkbox-wrapper input {
  margin-right: 10px;
}

.color-marker {
  width: 10px;
  height: 10px;
  border-radius: 50%;
  margin-right: 10px;
  display: inline-block;
  flex-shrink: 0;
}
.color-marker.square { border-radius: 2px; }

.item-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 160px;
}

.badge-count {
  background: var(--bg-hover);
  color: var(--ledax-strong);
  padding: 2px 6px;
  border-radius: 4px;
  font-size: 0.7em;
  margin-left: 6px;
}

.item-count {
  font-size: 0.75rem;
  color: var(--text-muted);
  background: #f1f5f9;
  padding: 2px 6px;
  border-radius: 4px;
}

/* --- MAPA --- */
.map-wrapper {
  flex: 1;
  position: relative;
  background: #e5e7eb; /* Cor de fundo enquanto carrega */
}

#map {
  width: 100%;
  height: 100%;
  z-index: 1;
}

/* --- LOADING --- */
.loading-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(255,255,255,0.8);
  backdrop-filter: blur(2px);
  z-index: 2000;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 40px;
  height: 40px;
  border: 3px solid var(--border-subtle);
  border-top-color: var(--ledax);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
  margin-bottom: 10px;
}

.loading-text {
  font-size: 0.9rem;
  color: var(--ledax-strong);
  font-weight: 500;
}

@keyframes spin {
  to { transform: rotate(360deg); }
}

/* LEAFLET CUSTOMIZATIONS GLOBAL.CSS-AWARE */
:deep(.custom-pin) span {
  display: block;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 2px 5px rgba(0,0,0,0.2);
}
</style>