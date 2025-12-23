<script setup>
import { RouterView } from 'vue-router'
</script>

<template>
  <RouterView />
</template>

<style>
/* ===============================
   GLOBAL DESIGN SYSTEM
   (Disponível para Login e Layout)
================================ */
:root {
  --bg-app: #f8fafc;
  --bg-panel: #ffffff;
  --bg-hover: #f1f5f9;

  --text-main: #0f172a;
  --text-muted: #64748b;

  --primary: #0f766e;
  --primary-soft: rgba(15, 118, 110, 0.12);

  --border-soft: #e5e7eb;
}

body {
  margin: 0;
  padding: 0;
  font-family: Inter, system-ui, -apple-system, BlinkMacSystemFont, sans-serif;
  background-color: var(--bg-app);
}
</style>