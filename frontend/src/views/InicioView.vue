<template>
  <div class="view inicio">
    <header class="i-top"><Logo /></header>
    <main class="i-main">
      <h1>Sistema de turnos</h1>
      <p class="muted">Abra cada parte del sistema en el dispositivo que corresponde.</p>
      <div class="i-grid">
        <RouterLink v-for="o in opciones" :key="o.to" :to="o.to" class="panel i-card">
          <span class="pref">{{ o.p }}</span>
          <h2>{{ o.titulo }}</h2>
          <p class="muted">{{ o.texto }}</p>
          <span class="chip">{{ o.donde }}</span>
        </RouterLink>
      </div>
    </main>
    <footer class="muted i-pie">TurnoFácil · Grupo 2 · Ingeniería de Software II · UNICARIBE</footer>
  </div>
</template>

<script setup>
import Logo from '../components/Logo.vue'

const opciones = [
  { to: '/kiosco', p: 'K', titulo: 'Kiosco', texto: 'El cliente elige un servicio y recibe su turno.', donde: 'Tablet en la entrada' },
  { to: '/pantalla', p: 'P', titulo: 'Pantalla pública', texto: 'Muestra el turno que se está llamando.', donde: 'TV de la sala' },
  { to: '/login', p: 'A', titulo: 'Personal', texto: 'Recepción y administración, con usuario y contraseña.', donde: 'PC de ventanilla' }
]
</script>

<style scoped>
.i-top{padding:20px 32px}
.i-main{flex:1;max-width:1000px;width:100%;margin:0 auto;padding:24px}
.i-main h1{font-size:34px;margin:24px 0 6px}
.i-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:20px;margin-top:28px}
.i-card{padding:24px;text-decoration:none;color:inherit;display:flex;flex-direction:column;gap:10px;transition:border-color .12s}
.i-card:hover{border-color:var(--azul)}
.i-card h2{font-size:20px;margin-top:8px}
.i-card p{margin:0;flex:1}
.i-card .chip{align-self:flex-start}
.i-pie{text-align:center;font-size:13px;padding:24px}
</style>
