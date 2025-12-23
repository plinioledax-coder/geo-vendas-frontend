import { createRouter, createWebHistory } from 'vue-router'

// Importamos a Login e o Layout diretamente (carregamento rápido)
import LoginView from '../views/LoginView.vue'
import MainLayout from '../components/MainLayout.vue'

// Importamos a RedesView (pode manter assim ou fazer lazy load como as outras)
import RedesView from '../views/RedesView.vue'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    // 1. Rota de Login (Pública e fora do Layout)
    {
      path: '/login',
      name: 'Login',
      component: LoginView
    },

    // 2. Rota Pai (O Layout com Sidebar)
    {
      path: '/plataforma',
      component: MainLayout, // Todo mundo aqui dentro herda a Sidebar
      // Proteção: Se alguém tentar entrar aqui sem logar, o beforeEach barra.
      children: [
        {
          path: 'redes', // Fica: /plataforma/redes
          name: 'redes',
          component: RedesView
        },
        {
          path: 'vendas', // Fica: /plataforma/vendas
          name: 'vendas',
          component: () => import('../views/VendasView.vue')
        },
        {
          path: 'uc', // Fica: /plataforma/uc
          name: 'uc',
          component: () => import('../views/UcView.vue')
        },
        // Se acessar só /plataforma, joga para redes por padrão
        {
          path: '', 
          redirect: { name: 'vendas' }
        }
      ]
    },

    // 3. Rota Raiz (Redireciona para o fluxo principal)
    {
      path: '/',
      redirect: '/plataforma/vendas' 
      // Nota: O "Guard" abaixo vai interceptar isso e jogar pro Login se não tiver token.
    },
    
    // 4. Qualquer rota não existente (404) joga para login ou home
    {
      path: '/:pathMatch(.*)*',
      redirect: '/login'
    }
  ]
})

// === GUARDA DE ROTAS (A SEGURANÇA) ===
router.beforeEach((to, from, next) => {
  // Pega o token salvo no navegador
  const isAuthenticated = localStorage.getItem('user_token');
  
  // Se a rota NÃO for 'Login' e o usuário NÃO tiver token
  if (to.name !== 'Login' && !isAuthenticated) {
    next({ name: 'Login' }); // Manda pro login
  } 
  // Se o usuário TIVER token e tentar acessar o 'Login' (já estando logado)
  else if (to.name === 'Login' && isAuthenticated) {
    next({ name: 'vendas' }); // Manda direto pra dentro da plataforma
  } 
  else {
    next(); // Deixa passar normal
  }
});

export default router