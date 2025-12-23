<template>
  <div class="login-wrapper">
    <div class="login-card">
      <div class="logo-area">
        <div class="logo-sq">L</div> 
        <h1>LEDAX</h1>
        <p>Plataforma de Mapeamento de Vendas</p>
      </div>

      <form @submit.prevent="handleLogin">
        <div class="input-group">
          <label>Usuário</label>
          <input 
            type="text" 
            v-model="user" 
            placeholder="Digite seu usuário" 
            required 
            :disabled="loading"
          />
        </div>

        <div class="input-group">
          <label>Senha</label>
          <div class="password-wrapper">
            <input 
              :type="showPassword ? 'text' : 'password'" 
              v-model="pass" 
              placeholder="••••••" 
              required 
              :disabled="loading"
              class="input-password"
            />
            <button 
              type="button" 
              class="btn-toggle-pass" 
              @click="showPassword = !showPassword"
              :disabled="loading"
              tabindex="-1"
            >
              <svg v-if="!showPassword" xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-eye"><path d="M2 12s3-7 10-7 10 7 10 7-3 7-10 7-10-7-10-7Z"/><circle cx="12" cy="12" r="3"/></svg>
              
              <svg v-else xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" class="icon-eye"><path d="M9.88 9.88a3 3 0 1 0 4.24 4.24"/><path d="M10.73 5.08A10.43 10.43 0 0 1 12 5c7 0 10 7 10 7a13.16 13.16 0 0 1-1.67 2.68"/><path d="M6.61 6.61A13.526 13.526 0 0 0 2 12s3 7 10 7a9.74 9.74 0 0 0 5.39-1.61"/><line x1="2" x2="22" y1="2" y2="22"/></svg>
            </button>
          </div>
        </div>

        <p v-if="error" class="error-msg">Usuário ou senha incorretos.</p>
        <p v-if="serverError" class="error-msg">Erro ao conectar com o servidor.</p>

        <button type="submit" class="btn-entrar" :disabled="loading">
          <span v-if="loading">Entrando...</span>
          <span v-else>Acessar Plataforma</span>
        </button>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter } from 'vue-router';

const router = useRouter();
const user = ref('');
const pass = ref('');
const showPassword = ref(false); // Nova variável para controlar o olho
const error = ref(false);       
const serverError = ref(false); 
const loading = ref(false);

const API_URL = 'https://geo-vendas-backend.onrender.com/token'; 

const handleLogin = async () => {
  error.value = false;
  serverError.value = false;
  loading.value = true;

  try {
    const formData = new URLSearchParams();
    formData.append('username', user.value);
    formData.append('password', pass.value);

    const response = await fetch(API_URL, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/x-www-form-urlencoded',
      },
      body: formData,
    });

    if (response.ok) {
      const data = await response.json();
      localStorage.setItem('user_token', data.access_token);
      if (data.permissoes) {
        localStorage.setItem('user_permissoes', JSON.stringify(data.permissoes));
      }
      router.push('/plataforma'); 
    } else {
      error.value = true;
    }
  } catch (err) {
    console.error('Erro de conexão:', err);
    serverError.value = true;
  } finally {
    loading.value = false;
  }
};
</script>

<style scoped>
/* ========================
   ESTILOS GERAIS
======================== */
.login-wrapper {
  height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  font-family: 'Inter', sans-serif;
}
.login-card {
  background: white;
  padding: 2.5rem;
  border-radius: 16px;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06);
  width: 100%;
  max-width: 400px;
  border: 1px solid #e2e8f0;
}

.logo-area { 
  display: flex; 
  flex-direction: column; 
  align-items: center; 
  margin-bottom: 2rem; 
}

.logo-sq {
  width: 48px;
  height: 48px;
  background: #0f766e;
  color: white;
  border-radius: 12px;
  display: grid;
  place-items: center;
  font-weight: 800;
  font-size: 24px;
  margin-bottom: 12px;
}

.logo-area h1 { color: #0f172a; margin: 0; font-size: 1.5rem; font-weight: 700; letter-spacing: -0.5px; }
.logo-area p { color: #64748b; font-size: 0.875rem; margin-top: 4px; }

.input-group { margin-bottom: 1.25rem; }
.input-group label { display: block; font-size: 0.875rem; color: #334155; margin-bottom: 6px; font-weight: 500; }
.input-group input {
  width: 100%; padding: 10px 12px; border: 1px solid #cbd5e1; border-radius: 8px;
  box-sizing: border-box; font-size: 0.95rem; outline: none; transition: 0.2s;
  color: #0f172a;
}
.input-group input:focus { border-color: #0f766e; box-shadow: 0 0 0 3px rgba(15, 118, 110, 0.1); }
.input-group input:disabled { background-color: #f1f5f9; cursor: not-allowed; }

/* ========================
   ESTILOS DO OLHO (SENHA)
======================== */
.password-wrapper {
  position: relative;
  display: flex;
  align-items: center;
}

/* Padding extra na direita para o texto não ficar por cima do ícone */
.input-password {
  padding-right: 40px !important; 
}

.btn-toggle-pass {
  position: absolute;
  right: 10px;
  background: transparent;
  border: none;
  cursor: pointer;
  display: flex;
  align-items: center;
  justify-content: center;
  color: #64748b;
  padding: 4px;
  border-radius: 4px;
  transition: color 0.2s;
}

.btn-toggle-pass:hover {
  color: #0f766e;
  background-color: #f1f5f9;
}

.btn-toggle-pass:focus {
  outline: none;
}

/* ========================
   BOTÕES E ERROS
======================== */
.btn-entrar {
  width: 100%; padding: 12px; background: #0f766e; color: white; border: none;
  border-radius: 8px; font-weight: 600; cursor: pointer; font-size: 0.95rem; 
  transition: 0.2s; margin-top: 10px;
}
.btn-entrar:hover:not(:disabled) { background: #0d9488; }
.btn-entrar:disabled { opacity: 0.7; cursor: wait; }

.error-msg { 
  color: #ef4444; 
  background-color: #fef2f2; 
  padding: 8px; 
  border-radius: 6px; 
  font-size: 0.85rem; 
  text-align: center; 
  margin-bottom: 16px; 
  border: 1px solid #fee2e2;
}
</style>
