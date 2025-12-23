<script setup>
import { useRouter, useRoute } from 'vue-router'

const router = useRouter()
const route = useRoute()

// Verifica se o link está ativo para pintar de verde
const isAtivo = (nomeRota) => route.name === nomeRota

const navegarPara = (nomeRota) => {
  router.push({ name: nomeRota })
}

const logout = () => {
  localStorage.removeItem('user_token') // Remove o token
  router.push('/login') // Chuta para fora
}
</script>

<template>
  <div class="app-grid">

    <header class="header">
      <div class="brand">
        <div class="logo-sq">L</div>
        <div class="brand-text">
          <h1>LEDAX</h1>
          <span>Plataforma de Mapeamento de Vendas</span>
        </div>
      </div>

      <div class="user-info">
         <span style="font-size:12px; color:var(--text-muted)">Admin Logado</span>
      </div>
    </header>

    <aside class="sidebar-main">
      <div class="nav-title">MÓDULOS</div>

      <nav class="nav-list">
        <div 
          class="nav-link" 
          :class="{ active: isAtivo('vendas') }"
          @click="navegarPara('vendas')"
        >
          Mapa de Vendas
        </div>

        <div 
          class="nav-link" 
          :class="{ active: isAtivo('redes') }"
          @click="navegarPara('redes')"
        >
          Redes
        </div>

        <div 
          class="nav-link" 
          :class="{ active: isAtivo('uc') }"
          @click="navegarPara('uc')"
        >
          Unidades Consumidoras
        </div>
      </nav>

      <div class="footer-area">
        <button @click="logout" class="btn-logout">
          Sair da Plataforma
        </button>
        <div class="copy">LEDAX © 2025</div>
      </div>
    </aside>

    <main class="content-area">
      <RouterView v-slot="{ Component }">
        <transition name="fade" mode="out-in">
          <component :is="Component" />
        </transition>
      </RouterView>
    </main>

  </div>
</template>

<style scoped>
/* ===============================
   GRID & LAYOUT
================================ */
.app-grid {
  display: grid;
  height: 100vh;
  width: 100vw;
  grid-template-rows: 64px 1fr;
  grid-template-columns: 260px 1fr;
  grid-template-areas:
    "header header"
    "sidebar content";
  background: var(--bg-app);
}

/* ===============================
   HEADER
================================ */
.header {
  grid-area: header;
  background: var(--bg-panel);
  border-bottom: 1px solid var(--border-soft);
  display: flex;
  align-items: center;
  padding: 0 24px;
  justify-content: space-between;
}

.brand { display: flex; align-items: center; gap: 14px; }

.logo-sq {
  width: 38px; height: 38px;
  background: var(--primary); color: white;
  border-radius: 8px; display: grid; place-items: center;
  font-weight: 800; font-size: 18px;
}

.brand-text h1 { margin: 0; font-size: 17px; font-weight: 700; color: var(--text-main); }
.brand-text span { font-size: 11px; color: var(--text-muted); }

/* ===============================
   SIDEBAR
================================ */
.sidebar-main {
  grid-area: sidebar;
  background: var(--bg-panel);
  border-right: 1px solid var(--border-soft);
  padding: 24px 16px;
  display: flex;
  flex-direction: column;
}

.nav-title {
  font-size: 11px; font-weight: 700; color: var(--text-muted);
  letter-spacing: 0.12em; margin-bottom: 16px;
}

.nav-list { display: flex; flex-direction: column; gap: 4px; flex: 1; }

.nav-link {
  padding: 10px 14px; border-radius: 8px;
  font-size: 14px; font-weight: 500; color: var(--text-main);
  cursor: pointer; transition: background 0.15s, color 0.15s;
}

.nav-link:hover { background: var(--bg-hover); }

/* Classe ativa (controlada pelo Vue) */
.nav-link.active {
  background: var(--primary-soft);
  color: var(--primary);
  font-weight: 600;
}

/* FOOTER / LOGOUT */
.footer-area { margin-top: auto; border-top: 1px solid var(--border-soft); padding-top: 15px; }
.btn-logout {
  width: 100%; border: 1px solid var(--border-soft); background: white;
  padding: 8px; border-radius: 6px; cursor: pointer; color: #ef4444; font-size: 13px; font-weight: 600;
  transition: 0.2s;
}
.btn-logout:hover { background: #fef2f2; border-color: #ef4444; }

.copy { font-size: 11px; color: var(--text-muted); text-align: center; margin-top: 12px; }

/* ===============================
   CONTENT AREA
================================ */
.content-area {
  grid-area: content;
  background: var(--bg-app);
  overflow: hidden; /* Importante para o mapa não vazar */
  position: relative;
}

/* Transição de rotas */
.fade-enter-active, .fade-leave-active { transition: opacity 0.2s ease; }
.fade-enter-from, .fade-leave-to { opacity: 0; }
</style>