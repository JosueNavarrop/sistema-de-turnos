<template>
  <div class="view">
    <StaffHeader />
    <main class="page">
      <div class="page-h">
        <div>
          <h1>Administración</h1>
          <p>{{ SUBTITULOS[pestana] }}</p>
        </div>
        <button class="btn btn-azul" @click="nuevo">＋ {{ BOTONES[pestana] }}</button>
      </div>
      <div class="pestanas" role="tablist">
        <button v-for="(t, k) in TITULOS" :key="k" role="tab" :aria-selected="pestana === k" @click="cambiar(k)">{{ t }}</button>
      </div>
      <ServiciosTab v-if="pestana === 'servicios'" ref="tab" />
      <VentanillasTab v-else-if="pestana === 'ventanillas'" ref="tab" />
      <UsuariosTab v-else ref="tab" />
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import StaffHeader from '../components/StaffHeader.vue'
import ServiciosTab from '../components/admin/ServiciosTab.vue'
import VentanillasTab from '../components/admin/VentanillasTab.vue'
import UsuariosTab from '../components/admin/UsuariosTab.vue'

const TITULOS = { servicios: 'Servicios', ventanillas: 'Ventanillas', usuarios: 'Usuarios' }
const SUBTITULOS = {
  servicios: 'Configure los servicios que aparecen en el kiosco',
  ventanillas: 'Defina las ventanillas y los servicios que atiende cada una',
  usuarios: 'Gestione los recepcionistas y su ventanilla asignada'
}
const BOTONES = { servicios: 'Nuevo servicio', ventanillas: 'Nueva ventanilla', usuarios: 'Nuevo usuario' }

const route = useRoute()
const router = useRouter()
const pestana = ref(TITULOS[route.query.tab] ? route.query.tab : 'servicios')
const tab = ref(null)

function cambiar(k) {
  pestana.value = k
  router.replace({ query: { tab: k } })
}
const nuevo = () => tab.value?.abrir()
</script>

<style scoped>
.pestanas{display:inline-flex;gap:4px;padding:4px;border-radius:12px;background:var(--borde);margin-bottom:20px}
.pestanas button{border:0;background:transparent;padding:8px 20px;border-radius:9px;font-size:14px;font-weight:500;color:var(--gris)}
.pestanas button[aria-selected="true"]{background:var(--surface);color:var(--texto);font-weight:600;box-shadow:0 1px 3px rgba(0,0,0,.1)}
</style>
