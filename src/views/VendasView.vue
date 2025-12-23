<template>
  <div class="dashboard-container">

    <aside class="sidebar" :class="{ 'collapsed': sidebarCollapsed }">
      <div class="sidebar-header">
        <div v-if="!sidebarCollapsed" class="fade-in">
          <h2 class="title">Geolocalização de Vendas</h2>
          <p class="subtitle">Análise Quantitativa</p>
          
          <p v-if="dataAtualizacao" class="last-update" title="Data da última alteração no banco de dados">
            🕒 Atualizado: {{ dataAtualizacao }}
          </p>
        </div>

        <button @click="sidebarCollapsed = !sidebarCollapsed" class="toggle-btn" title="Expandir/Recolher">
          <span v-if="sidebarCollapsed">☰</span>
          <span v-else>✕</span>
        </button>
      </div>

      <div class="sidebar-content" v-show="!sidebarCollapsed">

        <section class="filter-group">
          <label class="section-label">Filtros Globais</label>
          
          <div class="search-box">
            <input v-model="filtros.busca" placeholder="Buscar cliente, cidade..." class="input-modern">
          </div>
          
          <div class="date-row">
            <div class="date-wrapper">
              <span class="date-label">De</span>
              <input type="date" v-model="filtros.data_inicio" class="input-modern small">
            </div>
            <div class="date-wrapper">
              <span class="date-label">Até</span>
              <input type="date" v-model="filtros.data_fim" class="input-modern small">
            </div>
          </div>

          <div class="date-row" style="margin-top: 5px;">
            <div class="date-wrapper">
              <span class="date-label">Valor Min (R$)</span>
              <input type="number" v-model.lazy="filtros.valor_min" placeholder="0,00" class="input-modern small">
            </div>
            <div class="date-wrapper">
              <span class="date-label">Valor Max (R$)</span>
              <input type="number" v-model.lazy="filtros.valor_max" placeholder="Max" class="input-modern small">
            </div>
          </div>
        </section>

        <section class="visual-toggles">
          <label class="toggle-row">
            <span>Agrupar Pontos (Clusters)</span>
            <input type="checkbox" v-model="toggles.clusters" class="toggle-switch">
          </label>
          <label class="toggle-row">
            <span>Mapa de Calor</span>
            <input type="checkbox" v-model="toggles.heat" class="toggle-switch">
          </label>
        </section>

        <section class="dashboard-panel">
          <h3 class="dash-title">Resumo Qualitativo</h3>

          <div class="total-highlight">
            <span class="lbl">Total em Vendas</span>
            <span class="val">{{ formatarMoeda(kpis.totalValor) }}</span>
          </div>

          <div class="kpi-grid-mini">
            <div class="kpi-mini">
              <span class="kpi-mini-label">Total Vendas</span>
              <span class="kpi-mini-value">{{ kpis.totalClientes }}</span>
            </div>
            <div class="kpi-mini">
              <span class="kpi-mini-label">Redes Ativas</span>
              <span class="kpi-mini-value">{{ kpis.redesAtivas }}</span>
            </div>
            <div class="kpi-mini">
              <span class="kpi-mini-label">Reps. Ativos</span>
              <span class="kpi-mini-value">{{ kpis.repsAtivos }}</span>
            </div>
          </div>

          <div class="mini-list-box">
            <div class="mini-header-row">
              <div class="mini-title">Top Redes</div>
              <select v-model="ordenacaoRedes" class="sort-select" title="Ordenar por">
                <option value="qtd">Vol.</option>
                <option value="valor">R$</option>
              </select>
            </div>

            <ul class="list-presenca custom-scroll">
              <li v-for="(item, index) in redesOrdenadasWidget" :key="index" class="top-item">
                <div class="top-item-left">
                  <span class="rank">#{{ index + 1 }}</span>
                  <span class="name" :title="item.nome">{{ item.nome }}</span>
                </div>
                <div class="top-item-right">
                  <span class="money-badge">{{ formatarMoeda(item.total) }}</span>
                  <span class="count" title="Quantidade de vendas">{{ item.qtd }}</span>
                </div>
              </li>
              <li v-if="redesOrdenadasWidget.length === 0" class="empty-list">Sem dados</li>
            </ul>
          </div>
        </section>

        <hr class="divider">

        <section class="filter-group flex-grow">
          <div class="group-header">
            <label class="section-label">
              Redes
              <span class="badge-count" v-if="opcoesFiltros.rede.length">
                {{ listaRedesReativa.length }} / {{ opcoesFiltros.rede.length }}
              </span>
            </label>
            <button class="btn-text" @click="limparFiltroUnico('rede')" v-if="filtrosSelecionados.rede.length > 0">
              Limpar
            </button>
          </div>

          <div class="search-container flex-row">
            <input type="text" v-model="buscaRede" placeholder="Filtrar lista..." class="search-input" />
            
            <select v-model="ordenacaoListaRedes" class="sort-select-mini" title="Ordenar Lista">
              <option value="qtd">Vol.</option>
              <option value="valor">R$</option>
              <option value="az">A-Z</option>
              <option value="za">Z-A</option>
            </select>
          </div>

          <div class="scroll-list custom-scroll">
            <div v-if="listaRedesReativa.length === 0"
              style="padding:10px; color:#64748b; font-size:0.8rem; text-align:center;">
              Nenhuma rede encontrada.
            </div>

            <div v-for="item in listaRedesReativa" :key="item.nome" class="list-item">
              <label class="checkbox-wrapper">
                <input type="checkbox" :value="item.nome" v-model="filtrosSelecionados.rede">
                <span class="color-marker" :style="{ backgroundColor: stringToColor(item.nome) }"></span>
                <span class="item-name" :title="item.nome + ' (' + formatarMoeda(item.total) + ')'">{{ item.nome }}</span>
                <span class="item-count" v-if="ordenacaoListaRedes === 'valor'">{{ formatarMoedaCompacta(item.total) }}</span>
                <span class="item-count" v-else>({{ item.qtd }})</span>
              </label>
            </div>
          </div>
        </section>

        <template v-for="(lista, chave) in opcoesFiltros" :key="chave">
          <section class="filter-group flex-grow" v-if="chave !== 'rede'">
            <div class="group-header">
              <label class="section-label">
                {{ formatarTitulo(chave) }}
              </label>
              <button class="btn-text" @click="limparFiltroUnico(chave)" v-if="filtrosSelecionados[chave].length > 0">
                Limpar
              </button>
            </div>

            <div class="scroll-list custom-scroll">
               <div v-for="item in getListaReativa(chave)" :key="item.nome" class="list-item">
                <label class="checkbox-wrapper">
                  <input type="checkbox" :value="item.nome" v-model="filtrosSelecionados[chave]">
                  <span class="color-marker"
                    :style="{ backgroundColor: chave === 'regional' ? (CORES_MAP[item.nome] || '#999') : stringToColor(item.nome) }">
                  </span>
                  <span class="item-name" :title="item.nome">{{ item.nome }}</span>
                  <span class="item-count">({{ item.qtd }})</span>
                </label>
              </div>
              <div v-if="getListaReativa(chave).length === 0" class="empty-list" style="padding:5px;">
                Sem opções
              </div>
            </div>
          </section>
        </template>

      </div>

      <div class="sidebar-footer" v-show="!sidebarCollapsed">
        <button @click="limparTudo" class="btn-secondary" title="Resetar filtros e mapa">
          Restaurar Visão Original
        </button>
      </div>
    </aside>

    <main class="map-wrapper">
      <div class="map-floating-total">
        <div class="float-label">Total Filtrado</div>
        <div class="float-value">{{ formatarMoeda(kpis.totalValor) }}</div>
      </div>

      <div ref="mapContainer" id="map"></div>

      <transition name="fade">
        <div v-if="loading" class="loading-overlay">
          <div class="spinner"></div>
        </div>
      </transition>
    </main>
  </div>
</template>

<script setup>
import { ref, onMounted, reactive, watch, nextTick, shallowRef, computed } from 'vue';
import { useRouter } from 'vue-router';
import L from 'leaflet';

import 'leaflet/dist/leaflet.css';
import 'leaflet.markercluster/dist/leaflet.markercluster.js';
import 'leaflet.markercluster/dist/MarkerCluster.css';
import 'leaflet.markercluster/dist/MarkerCluster.Default.css';
import 'leaflet.heat/dist/leaflet-heat.js';

// --- CONFIGURAÇÕES ---
const API_BASE = import.meta.env.VITE_API_BASE_URL;
const URL_CONFIG = "/data/config_redes.json";
const URL_ESTADOS = "/static/brasil_estados.geojson";

// --- ESTADO REATIVO ---
const router = useRouter();
const mapContainer = ref(null);
const map = shallowRef(null);

const markersLayer = shallowRef(null);
const clusterGroup = shallowRef(null);
const heatLayer = shallowRef(null);
const regionalLayer = shallowRef(null);

// Armazena pontos do heatmap
const storedHeatPoints = shallowRef([]); 

const sidebarCollapsed = ref(false);
const loading = ref(false);
let searchTimeout = null;

const dataAtualizacao = ref(''); 
const geoJsonEstados = shallowRef(null);
const CORES_MAP = reactive({});
const COBERTURA_MAP = reactive({});

// 1. Opções Disponíveis
const opcoesFiltros = reactive({ 
  rede: [], 
  tipo_cliente: [], 
  funil: [], 
  representante: [], 
  uf: [],           
  responsavel: []   
});

// 2. Seleções do Usuário
const filtrosSelecionados = reactive({ 
  rede: [], 
  tipo_cliente: [], 
  funil: [], 
  representante: [], 
  uf: [], 
  responsavel: [] 
});

// 3. Filtros Globais
const filtros = reactive({ 
  busca: '', 
  data_inicio: '', 
  data_fim: '', 
  valor_min: '',    
  valor_max: ''     
});

// 4. Contadores
const contadores = reactive({
  rede: {},
  tipo_cliente: {},
  funil: {},
  representante: {},
  uf: {},          
  responsavel: {} 
});

// NOVO: Totais em R$ por rede (para permitir ordenação na lista)
const totaisRede = reactive({});

// --- LÓGICA DE COMPUTED ---

// A. Lógica da LISTA DE FILTROS
const buscaRede = ref('');
const ordenacaoListaRedes = ref('qtd');

const listaRedesReativa = computed(() => {
  const todas = opcoesFiltros.rede || [];
  
  let lista = todas.map(nome => ({
    nome,
    qtd: contadores.rede[nome] || 0,
    total: totaisRede[nome] || 0 // Pega o total R$ computado
  }));

  if (buscaRede.value) {
    const termo = buscaRede.value.toLowerCase();
    lista = lista.filter(item => item.nome.toLowerCase().includes(termo));
  }

  return lista.sort((a, b) => {
    // 1. Prioridade: Selecionados no topo
    const aSelected = filtrosSelecionados.rede.includes(a.nome);
    const bSelected = filtrosSelecionados.rede.includes(b.nome);
    
    if (aSelected && !bSelected) return -1; 
    if (!aSelected && bSelected) return 1;  
    
    // 2. Critérios de ordenação
    if (ordenacaoListaRedes.value === 'az') return a.nome.localeCompare(b.nome);
    if (ordenacaoListaRedes.value === 'za') return b.nome.localeCompare(a.nome);
    if (ordenacaoListaRedes.value === 'valor') return b.total - a.total; // Ordenar por R$
    
    // Padrão: Volume
    return b.qtd - a.qtd; 
  });
});

const getListaReativa = (chave) => {
  const lista = opcoesFiltros[chave] || [];
  return lista
    .map(nome => ({ nome, qtd: contadores[chave]?.[nome] || 0 }))
    .sort((a, b) => {
       const aSelected = filtrosSelecionados[chave]?.includes(a.nome);
       const bSelected = filtrosSelecionados[chave]?.includes(b.nome);
       if (aSelected && !bSelected) return -1;
       if (!aSelected && bSelected) return 1;
       return b.qtd - a.qtd;
    });
};

// Toggles Visuais
const toggles = reactive({
  clusters: true,
  heat: false,
  regional: false
});

// KPIs
const kpis = reactive({
  totalValor: 0,
  totalClientes: 0,
  redesAtivas: 0,
  repsAtivos: 0,
  rawRedes: [] 
});

// B. Lógica do WIDGET DE RESUMO (Top Redes)
const ordenacaoRedes = ref('qtd');
const redesOrdenadasWidget = computed(() => {
  const lista = [...kpis.rawRedes]; // rawRedes já tem {nome, qtd, total}
  
  if (ordenacaoRedes.value === 'qtd') return lista.sort((a, b) => b.qtd - a.qtd).slice(0, 5);
  else if (ordenacaoRedes.value === 'valor') return lista.sort((a, b) => b.total - a.total).slice(0, 5);
  else if (ordenacaoRedes.value === 'nome') return lista.sort((a, b) => a.nome.localeCompare(b.nome)).slice(0, 5);
  
  return lista.slice(0, 5);
});

// Helpers
const formatarTitulo = (str) => {
  if (str === 'uf') return 'Estados (UF)';
  if (str === 'responsavel') return 'Responsáveis';
  if (str === 'tipo_cliente') return 'Tipo Cliente';
  return str.replace(/_/g, ' ').toUpperCase();
};

const stringToColor = (str) => {
  let hash = 0;
  for (let i = 0; i < str.length; i++) hash = str.charCodeAt(i) + ((hash << 5) - hash);
  const h = Math.abs(hash % 360);
  return `hsl(${h}, 65%, 45%)`;
};

const formatarMoeda = (valor) => {
  return new Intl.NumberFormat('pt-BR', { style: 'currency', currency: 'BRL' }).format(valor || 0);
};

// Formata abreviado (10k, 1M) para caber na lista
const formatarMoedaCompacta = (valor) => {
  if (!valor) return 'R$ 0';
  if (valor >= 1000000) return `R$ ${(valor/1000000).toFixed(1)}M`;
  if (valor >= 1000) return `R$ ${(valor/1000).toFixed(1)}k`;
  return `R$ ${valor.toFixed(0)}`;
};

// --- MAPA ---
const initMap = () => {
  if (!mapContainer.value) return;
  if (map.value) { map.value.remove(); map.value = null; }

  map.value = L.map(mapContainer.value, { zoomControl: false, preferCanvas: true }).setView([-15.79, -47.88], 4);

  L.tileLayer('https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png', {
    attribution: '&copy; CARTO', subdomains: 'abcd', maxZoom: 19
  }).addTo(map.value);

  L.control.zoom({ position: 'topright' }).addTo(map.value);

  markersLayer.value = L.featureGroup();
  clusterGroup.value = L.markerClusterGroup({ maxClusterRadius: 50, showCoverageOnHover: false });
  map.value.addLayer(clusterGroup.value);
};

// --- API ---
const carregarStatusAtualizacao = async () => {
  const token = localStorage.getItem('user_token');
  if (!token) return; 

  try {
    const res = await fetch(`${API_BASE}/status-dados`, {
      method: 'GET',
      headers: { 'Authorization': `Bearer ${token}` }
    });
    if (res.ok) {
      const data = await res.json();
      dataAtualizacao.value = data.data_atualizacao;
    }
  } catch (e) {}
};

const carregarOpcoesFiltros = async () => {
  const token = localStorage.getItem('user_token');
  if (!token) return;

  const params = new URLSearchParams();
  if (filtros.busca) params.append('busca_texto', filtros.busca);
  if (filtros.data_inicio) params.append('data_inicio', filtros.data_inicio);
  if (filtros.data_fim) params.append('data_fim', filtros.data_fim);
  if (filtros.valor_min) params.append('valor_min', filtros.valor_min);
  if (filtros.valor_max) params.append('valor_max', filtros.valor_max);

  try {
    const res = await fetch(`${API_BASE}/filtros?${params.toString()}`, {
       headers: { 'Authorization': `Bearer ${token}` }
    });
    
    if (res.ok) {
      const data = await res.json();
      Object.keys(opcoesFiltros).forEach(key => {
        if (data[key]) opcoesFiltros[key] = data[key];
      });
    }
  } catch (err) { console.error(err); }
};

const carregarDados = async () => {
  loading.value = true;
  const token = localStorage.getItem('user_token');
  if (!token) { router.push('/'); return; }

  const params = new URLSearchParams();
  if (filtros.busca) params.append('busca_texto', filtros.busca);
  if (filtros.data_inicio) params.append('data_inicio', filtros.data_inicio);
  if (filtros.data_fim) params.append('data_fim', filtros.data_fim);
  if (filtros.valor_min) params.append('valor_min', filtros.valor_min);
  if (filtros.valor_max) params.append('valor_max', filtros.valor_max);

  Object.keys(filtrosSelecionados).forEach(key => {
    const arr = filtrosSelecionados[key];
    if (arr && arr.length) arr.forEach(val => params.append(key, val));
  });

  try {
    const res = await fetch(`${API_BASE}/dados?${params.toString()}`, {
      method: 'GET',
      headers: { 'Authorization': `Bearer ${token}`, 'Content-Type': 'application/json' }
    });

    if (res.status === 401) { router.push('/'); return; }

    const vendas = await res.json();
    if (Array.isArray(vendas)) {
      atualizarKPIs(vendas); 
      plotarNoMapa(vendas);
      desenharRegional();
    }
  } catch (err) { console.error(err); }
  finally { loading.value = false; }
};

const atualizarKPIs = (dados) => {
  kpis.totalClientes = dados.length;
  kpis.totalValor = dados.reduce((acc, item) => acc + (parseFloat(item.valor_venda || item.valor) || 0), 0);

  // Zera contadores
  Object.keys(contadores).forEach(key => contadores[key] = {});
  // Zera totalizador de redes (NOVO)
  Object.keys(totaisRede).forEach(key => delete totaisRede[key]);
  
  const redesStats = {};
  const repsSet = new Set();

  dados.forEach(item => {
    const rep = item.representante || item.responsavel;
    if (rep) repsSet.add(rep);
    
    const valorItem = parseFloat(item.valor_venda || item.valor) || 0;

    if (item.rede) {
      // Para o Widget
      if (!redesStats[item.rede]) redesStats[item.rede] = { count: 0, total: 0 };
      redesStats[item.rede].count++;
      redesStats[item.rede].total += valorItem;

      // Para a Lista (Reatividade Global)
      if (!totaisRede[item.rede]) totaisRede[item.rede] = 0;
      totaisRede[item.rede] += valorItem;
    }

    ['rede', 'tipo_cliente', 'funil', 'representante', 'uf', 'responsavel'].forEach(chave => {
       let valor = item[chave];
       if (chave === 'responsavel' && !valor) valor = item.responsavel_do_negocio; 
       if (valor) {
         if (!contadores[chave][valor]) contadores[chave][valor] = 0;
         contadores[chave][valor]++;
       }
    });
  });

  kpis.redesAtivas = Object.keys(redesStats).length;
  kpis.repsAtivos = repsSet.size;
  kpis.rawRedes = Object.entries(redesStats).map(([nome, stat]) => ({
    nome, qtd: stat.count, total: stat.total
  }));
};

const plotarNoMapa = (dados) => {
  if (!map.value) return;
  clusterGroup.value.clearLayers();
  markersLayer.value.clearLayers();
  if (heatLayer.value) { map.value.removeLayer(heatLayer.value); heatLayer.value = null; }

  const heatPoints = [];
  const markers = [];

  dados.forEach(item => {
    let lat = parseFloat(String(item.latitude).replace(',', '.'));
    let lng = parseFloat(String(item.longitude).replace(',', '.'));
    if (isNaN(lat) || isNaN(lng) || lat === 0) return;
    
    heatPoints.push([lat, lng, 1]);
    const color = stringToColor(item.rede || 'Outros');
    const icon = L.divIcon({ className: 'custom-pin', html: `<span style="background-color: ${color};"></span>`, iconSize: [12, 12], iconAnchor: [6, 6] });
    
    const m = L.marker([lat, lng], { icon });
    const val = parseFloat(item.valor_venda || item.valor) || 0;
    
    m.bindPopup(`
      <div style="font-family:'Segoe UI', sans-serif; min-width: 320px; padding: 5px;">
        <div style="font-weight:700; color:#0f766e; font-size:15px; margin-bottom: 6px;">${item.titulo || 'Cliente'}</div>
        <div style="margin-bottom: 10px;"><span style="background-color: ${color}; color: #fff; font-size: 11px; font-weight: 600; padding: 3px 8px; border-radius: 4px;">${item.rede || 'SEM REDE'}</span></div>
        <div style="border-top: 1px solid #e2e8f0; margin: 10px 0;"></div>
        <div style="font-size:13px; line-height: 1.6; color: #334155;">
          <div><b>Rep:</b> ${item.representante || item.responsavel || 'N/D'}</div>
          <div><b>Valor:</b> <span style="color:#16a34a; font-weight:700;">${formatarMoeda(val)}</span></div>
          <div><b>Loc:</b> ${item.cidade} - ${item.uf}</div>
        </div>
      </div>
    `, { maxWidth: 400 });
    
    markers.push(m);
  });

  storedHeatPoints.value = heatPoints;
  clusterGroup.value.addLayers(markers);
  markers.forEach(m => markersLayer.value.addLayer(m));
  gerenciarCamadas();
};

const gerenciarCamadas = () => {
   if(!map.value) return;
   if(toggles.clusters) { 
     map.value.removeLayer(markersLayer.value); 
     map.value.addLayer(clusterGroup.value); 
   } else { 
     map.value.removeLayer(clusterGroup.value); 
     map.value.addLayer(markersLayer.value); 
   }

   if(toggles.heat && storedHeatPoints.value.length > 0) {
      if (heatLayer.value) map.value.removeLayer(heatLayer.value);
      heatLayer.value = L.heatLayer(storedHeatPoints.value, { radius: 25, blur: 15, maxZoom: 17 }).addTo(map.value);
   } else {
     if(heatLayer.value) { map.value.removeLayer(heatLayer.value); heatLayer.value = null; }
   }
};

const desenharRegional = () => {
  if (!map.value || !geoJsonEstados.value) return;
  if (regionalLayer.value) { map.value.removeLayer(regionalLayer.value); regionalLayer.value = null; }
  if (!toggles.regional) return;

  const regionaisAtivas = Object.keys(CORES_MAP); 
  const ufsComCor = {};
  regionaisAtivas.forEach(regNome => {
    const ufs = COBERTURA_MAP[regNome];
    const cor = CORES_MAP[regNome];
    if (Array.isArray(ufs)) ufs.forEach(uf => ufsComCor[uf] = cor);
  });

  regionalLayer.value = L.geoJSON(geoJsonEstados.value, {
    style: (f) => ({ fillColor: ufsComCor[f.properties.sigla] || 'transparent', weight: 1, color: 'white', fillOpacity: 0.4 }),
    onEachFeature: (f, l) => {
       if (ufsComCor[f.properties.sigla]) l.bindTooltip(`${f.properties.name}`, { sticky: true });
    }
  }).addTo(map.value);
  regionalLayer.value.bringToBack();
};

const carregarConfiguracoes = async () => {
  try {
    const res = await fetch(URL_CONFIG);
    const data = await res.json();
    data.forEach(reg => { CORES_MAP[reg.nome] = reg.cor; COBERTURA_MAP[reg.nome] = reg.estados; });
  } catch (e) {}
};
const carregarGeoJSON = async () => { try { const res = await fetch(URL_ESTADOS); if(res.ok) geoJsonEstados.value = await res.json(); } catch(e){} };

// --- ACTIONS ---
const limparFiltroUnico = (k) => filtrosSelecionados[k] = [];
const limparTudo = () => {
  Object.keys(filtrosSelecionados).forEach(k => filtrosSelecionados[k] = []);
  filtros.busca = ''; filtros.data_inicio = ''; filtros.data_fim = '';
  filtros.valor_min = ''; filtros.valor_max = '';
  buscaRede.value = '';
  toggles.clusters = true; toggles.heat = false; toggles.regional = false;
};

// --- WATCHERS ---
watch(filtrosSelecionados, () => carregarDados(), { deep: true });

watch(() => [filtros.data_inicio, filtros.data_fim, filtros.valor_min, filtros.valor_max], () => {
  carregarDados();
  carregarOpcoesFiltros();
});

watch(() => filtros.busca, () => { 
  clearTimeout(searchTimeout); 
  searchTimeout = setTimeout(() => {
    carregarDados();
    carregarOpcoesFiltros();
  }, 500); 
});

watch(() => toggles, () => { gerenciarCamadas(); desenharRegional(); }, { deep: true });
watch(sidebarCollapsed, () => setTimeout(() => map.value?.invalidateSize(), 300));

onMounted(async () => {
  await nextTick();
  setTimeout(async () => {
    initMap(); await carregarConfiguracoes(); await carregarGeoJSON();
    await carregarOpcoesFiltros(); 
    await carregarDados();         
    carregarStatusAtualizacao();
  }, 100);
});
</script>

<style scoped>
/* Variáveis de Tema */
.dashboard-container {
  --ledax: #0f766e;
  --bg-panel: rgba(255, 255, 255, 0.96);
  --border-color: #e2e8f0;
  --text-main: #334155;
  --text-muted: #64748b;

  display: flex;
  height: 100vh;
  width: 100vw;
  font-family: 'Segoe UI', Tahoma, sans-serif;
  overflow: hidden;
  background: #f8fafc;
}

.sidebar {
  width: 320px;
  background: var(--bg-panel);
  border-right: 1px solid var(--border-color);
  display: flex;
  flex-direction: column;
  transition: width 0.3s ease;
  z-index: 1000;
  box-shadow: 2px 0 10px rgba(0, 0, 0, 0.03);
}

.sidebar.collapsed {
  width: 60px;
}

.sidebar-header {
  height: 60px;
  padding: 0 16px;
  border-bottom: 1px solid var(--border-color);
  display: flex;
  align-items: center;
  justify-content: space-between;
}

.title {
  font-size: 1rem;
  font-weight: 700;
  color: var(--ledax);
  margin: 0;
}

.subtitle {
  font-size: 0.7rem;
  color: var(--text-muted);
  margin: 0;
}

.last-update {
  font-size: 0.6rem;
  color: #94a3b8;
  margin-top: 4px;
  display: flex;
  align-items: center;
  gap: 4px;
  font-style: italic;
}

.toggle-btn {
  background: none;
  border: 1px solid var(--border-color);
  border-radius: 4px;
  color: var(--text-muted);
  cursor: pointer;
  width: 28px;
  height: 28px;
}

.sidebar-content {
  flex: 1;
  overflow-y: auto;
  padding: 16px;
  display: flex;
  flex-direction: column;
  gap: 16px;
}

/* INPUTS */
.filter-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.input-modern {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  font-size: 0.85rem;
}

.input-modern:focus {
  border-color: var(--ledax);
  outline: none;
}

.date-row {
  display: flex;
  gap: 10px;
}

.date-wrapper {
  flex: 1;
  display: flex;
  flex-direction: column;
}

.date-label {
  font-size: 0.65rem;
  color: var(--text-muted);
  font-weight: 600;
  margin-bottom: 2px;
}

/* TOGGLES VISUAIS */
.visual-toggles {
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 8px;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.toggle-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 0.8rem;
  color: var(--text-main);
  cursor: pointer;
}

.toggle-switch {
  accent-color: var(--ledax);
  transform: scale(1.1);
}

/* DASHBOARD PANEL */
.dashboard-panel {
  background: #f1f5f9;
  border-radius: 8px;
  padding: 12px;
  border: 1px solid var(--border-color);
}

.dash-title {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--ledax);
  margin-top: 0;
  margin-bottom: 10px;
  border-bottom: 1px solid #e2e8f0;
  padding-bottom: 5px;
}

.total-highlight {
  background: #ffffff;
  border-left: 4px solid var(--ledax);
  padding: 10px;
  border-radius: 4px;
  margin-bottom: 12px;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
  display: flex;
  flex-direction: column;
}

.total-highlight .lbl {
  font-size: 0.7rem;
  color: var(--text-muted);
  text-transform: uppercase;
  font-weight: 700;
}

.total-highlight .val {
  font-size: 1.1rem;
  color: var(--text-main);
  font-weight: 800;
}


.kpi-grid-mini {
  display: grid;
  grid-template-columns: 1fr 1fr 1fr;
  gap: 8px;
  margin-bottom: 12px;
}

.kpi-mini {
  background: white;
  border-radius: 6px;
  padding: 6px;
  text-align: center;
  box-shadow: 0 1px 2px rgba(0, 0, 0, 0.05);
}

.kpi-mini-label {
  display: block;
  font-size: 0.6rem;
  color: var(--text-muted);
  margin-bottom: 2px;
}

.kpi-mini-value {
  display: block;
  font-size: 0.9rem;
  font-weight: 700;
  color: var(--text-main);
}

.mini-list-box {
  background: white;
  border-radius: 6px;
  padding: 8px;
  margin-bottom: 10px;
  border: 1px solid var(--border-color);
}

/* NOVO HEADER DO LIST BOX */
.mini-header-row {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
  gap: 8px;
  flex-wrap: nowrap;
}

.mini-title {
  font-size: 0.75rem;
  font-weight: 700;
  color: var(--text-muted);
  margin: 0;
  white-space: nowrap;
  flex-shrink: 0;
}

.sort-select {
  font-size: 0.7rem;
  padding: 2px 4px;
  border-radius: 4px;
  border: 1px solid #cbd5e1;
  color: #475569;
  background-color: #f8fafc;
  outline: none;
  cursor: pointer;
  width: auto;
  max-width: 85px;
  height: 24px;
  line-height: 1;
}

.sort-select:focus {
  border-color: var(--ledax);
  background-color: white;
}

/* NOVO: MINI SELECT PARA A LISTA */
.sort-select-mini {
  font-size: 0.7rem;
  padding: 2px 4px;
  border-radius: 4px;
  border: 1px solid #cbd5e1;
  color: #475569;
  background-color: #ffffff;
  outline: none;
  cursor: pointer;
  height: 30px; /* Mesma altura aproximada do input */
  width: 50px;
}

.sort-select-mini:focus {
  border-color: var(--ledax);
}

.list-presenca {
  list-style: none;
  padding: 0;
  margin: 0;
  max-height: 100px;
  overflow-y: auto;
}

/* AJUSTE LISTA DE REDES TOP 5 */
.top-item {
  display: flex;
  align-items: center;
  justify-content: space-between;
  font-size: 0.75rem;
  padding: 3px 0;
  border-bottom: 1px dashed #f1f5f9;
}

.top-item:last-child {
  border-bottom: none;
}

.top-item-left {
  display: flex;
  align-items: center;
  gap: 6px;
  overflow: hidden;
}

.top-item-right {
  display: flex;
  align-items: center;
  gap: 6px;
}

.rank {
  font-weight: bold;
  color: var(--ledax);
  width: 15px;
}

.name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 90px;
  color: var(--text-main);
}

.money-badge {
  background: #dcfce7;
  color: #166534;
  padding: 1px 5px;
  border-radius: 4px;
  font-weight: 600;
  font-size: 0.65rem;
}

.count {
  font-weight: bold;
  background: #e2e8f0;
  padding: 1px 5px;
  border-radius: 4px;
  font-size: 0.7rem;
}

.empty-list {
  font-size: 0.7rem;
  color: var(--text-muted);
  font-style: italic;
  text-align: center;
}

.divider {
  border: 0;
  border-top: 1px solid var(--border-color);
  margin: 5px 0;
}

/* FILTROS LISTAS */
.section-label {
  font-size: 0.7rem;
  font-weight: 700;
  color: var(--text-muted);
  text-transform: uppercase;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-top: 5px;
}

.badge-count {
  background: #e2e8f0;
  padding: 1px 5px;
  border-radius: 3px;
  font-size: 0.7em;
  margin-left: 5px;
}

.btn-text {
  background: none;
  border: none;
  color: var(--ledax);
  font-size: 0.7rem;
  cursor: pointer;
}

.scroll-list {
  max-height: 120px;
  overflow-y: auto;
  background: white;
  border: 1px solid var(--border-color);
  border-radius: 6px;
  padding: 4px 0;
  margin-top: 4px;
}

.list-item {
  padding: 4px 8px;
}

.list-item:hover {
  background: #f8fafc;
}

.checkbox-wrapper {
  display: flex;
  align-items: center;
  cursor: pointer;
  font-size: 0.8rem;
  width: 100%;
}

.checkbox-wrapper input {
  margin-right: 6px;
  accent-color: var(--ledax);
}

.color-marker {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  margin-right: 6px;
}

.item-name {
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  max-width: 140px;
}

.item-count {
    color: var(--text-muted);
    font-size: 0.75em;
    margin-left: auto;
    padding-left: 8px;
    font-weight: 600;
}

/* SEARCH REDE */
.search-container {
  padding: 0 2px 8px 2px;
}

.flex-row {
  display: flex;
  gap: 5px;
  align-items: center;
}

.search-input {
  flex: 1; /* Ocupa o espaço restante */
  padding: 6px 10px;
  font-size: 0.8rem;
  color: #334155;
  background-color: #f8fafc;
  border: 1px solid #e2e8f0;
  border-radius: 6px;
  outline: none;
  transition: all 0.2s;
}

.search-input:focus {
  border-color: #0f766e;
  background-color: #fff;
  box-shadow: 0 0 0 2px rgba(15, 118, 110, 0.1);
}

.search-input::placeholder {
  color: #94a3b8;
}


/* FOOTER */
.sidebar-footer {
  padding: 12px;
  border-top: 1px solid var(--border-color);
  background: white;
}

.btn-secondary {
  width: 100%;
  padding: 8px;
  border: 1px solid var(--border-color);
  background: white;
  border-radius: 6px;
  cursor: pointer;
  color: var(--text-muted);
}

.btn-secondary:hover {
  background: #f1f5f9;
  color: var(--text-main);
}

/* MAP AREA */
.map-wrapper {
  flex: 1;
  position: relative;
}

#map {
  width: 100%;
  height: 100%;
  z-index: 1;
  background: #e2e8f0;
}

/* FLOAT TOTAL CARD */
.map-floating-total {
  position: absolute;
  top: 15px;
  right: 15px;
  z-index: 999;
  background: white;
  padding: 10px 15px;
  border-radius: 8px;
  box-shadow: 0 4px 15px rgba(0, 0, 0, 0.15);
  border-left: 4px solid var(--ledax);
  display: flex;
  flex-direction: column;
  align-items: flex-end;
  min-width: 140px;
}

.float-label {
  font-size: 0.7rem;
  color: #64748b;
  font-weight: 700;
  text-transform: uppercase;
}

.float-value {
  font-size: 1.2rem;
  color: #1e293b;
  font-weight: 800;
  letter-spacing: -0.5px;
}

.loading-overlay {
  position: absolute;
  inset: 0;
  background: rgba(255, 255, 255, 0.7);
  z-index: 2000;
  display: flex;
  align-items: center;
  justify-content: center;
}

.spinner {
  width: 30px;
  height: 30px;
  border: 3px solid #e2e8f0;
  border-top-color: var(--ledax);
  border-radius: 50%;
  animation: spin 0.8s linear infinite;
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

/* Leaflet Custom */
:deep(.custom-pin) span {
  display: block;
  width: 100%;
  height: 100%;
  border-radius: 50%;
  border: 2px solid white;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.3);
}

.custom-scroll::-webkit-scrollbar {
  width: 4px;
}

.custom-scroll::-webkit-scrollbar-thumb {
  background: #cbd5e1;
  border-radius: 2px;
}

/* --- AJUSTE DO BOTÃO FECHAR DO POPUP --- */
:deep(.leaflet-popup-close-button) {
  top: 12px !important;
  right: 12px !important;
  width: 24px !important;
  height: 24px !important;
  color: #64748b !important;
  font-size: 18px !important;
  font-weight: bold !important;
  line-height: 24px !important;
  text-align: center;
  border-radius: 50%;
  transition: all 0.2s ease;
}

:deep(.leaflet-popup-close-button:hover) {
  color: #ef4444 !important;
  background-color: #f1f5f9;
}

:deep(.leaflet-popup-content) {
  margin: 10px 14px 10px 10px !important;
  line-height: 1.5;
}

:deep(.leaflet-popup-content-wrapper) {
  border-radius: 8px !important;
  padding: 0 !important;
}
</style>