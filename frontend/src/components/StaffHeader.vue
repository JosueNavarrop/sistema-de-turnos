<template>
  <header class="s-top">
    <Logo :to="sesion.inicio" />
    <nav class="s-nav" aria-label="Menú principal">
      <RouterLink v-if="sesion.rol === 'RECEPCIONISTA'" to="/recepcion">Atención</RouterLink>
      <RouterLink v-if="sesion.rol === 'ADMIN'" to="/admin">Administración</RouterLink>
      <RouterLink to="/turnos">Consultar turnos</RouterLink>
    </nav>
    <span class="sp"></span>
    <span v-if="ventanilla" class="vent" title="Ventanilla asignada">▣ <span>{{ ventanilla }}</span></span>
    <div class="user">
      <div class="avatar" aria-hidden="true">{{ sesion.iniciales }}</div>
      <span>{{ sesion.usuario?.nombre }}</span>
    </div>
    <button class="btn-icono" title="Cerrar sesión" aria-label="Cerrar sesión" @click="salir">
      <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M15 3h4a2 2 0 0 1 2 2v14a2 2 0 0 1-2 2h-4M10 17l5-5-5-5M15 12H3" /></svg>
    </button>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import Logo from './Logo.vue'
import { useSesion } from '../stores/sesion'

const sesion = useSesion()
const router = useRouter()
const ventanilla = computed(() => sesion.usuario?.ventanilla)

function salir() {
  sesion.salir()
  router.push('/login')
}
</script>
