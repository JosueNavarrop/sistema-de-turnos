<template>
  <div class="view">
    <StaffHeader />
    <main class="page">
      <div class="page-h">
        <div><h1>Consultar turnos</h1><p>Historial de turnos por fecha, servicio y estado</p></div>
      </div>

      <form class="panel filtros" @submit.prevent="buscar">
        <div class="campo"><label for="f-fecha">Fecha</label><input id="f-fecha" v-model="filtro.fecha" type="date" :max="hoyISO()"></div>
        <div class="campo"><label for="f-serv">Servicio</label>
          <select id="f-serv" v-model="filtro.servicio">
            <option :value="null">Todos</option>
            <option v-for="s in servicios" :key="s.id_servicio" :value="s.id_servicio">{{ s.prefijo }} · {{ s.nombre }}</option>
          </select>
        </div>
        <div class="campo"><label for="f-est">Estado</label>
          <select id="f-est" v-model="filtro.estado">
            <option value="">Todos</option>
            <option v-for="(t, k) in ESTADOS" :key="k" :value="k">{{ t }}</option>
          </select>
        </div>
        <button class="btn btn-azul">🔍 Buscar</button>
      </form>

      <div v-if="datos" class="totales">
        <div class="panel tot"><b>{{ datos.totales.total }}</b><span>Turnos del día</span></div>
        <div class="panel tot"><b style="color:var(--verde)">{{ datos.totales.atendido }}</b><span>Atendidos</span></div>
        <div class="panel tot"><b style="color:var(--rojo)">{{ datos.totales.no_presentado }}</b><span>No se presentaron</span></div>
        <div class="panel tot"><b style="color:var(--ambar)">{{ datos.totales.en_espera }}</b><span>En espera</span></div>
        <div class="panel tot"><b style="color:var(--azul)">{{ minutos(datos.totales.espera_promedio_min) }}</b><span>Espera promedio</span></div>
      </div>

      <div v-if="datos" class="panel tabla-wrap">
        <table class="tabla">
          <thead><tr><th>Turno</th><th>Servicio</th><th>Llegada</th><th>Llamado</th><th>Espera</th><th>Ventanilla</th><th>Atendió</th><th>Estado</th><th v-if="esAdmin"></th></tr></thead>
          <tbody>
            <tr v-for="t in datos.turnos" :key="t.id_turno">
              <td class="cod">{{ t.codigo }}</td>
              <td>{{ t.servicio }}</td>
              <td>{{ hora(t.hora_creacion) }}</td>
              <td :class="{ muted: !t.hora_llamado }">{{ hora(t.hora_llamado) }}</td>
              <td>{{ t.espera_min != null ? minutos(t.espera_min) : minutos(esperaActual(t)) }}</td>
              <td :class="{ muted: !t.ventanilla }">{{ t.ventanilla || '—' }}</td>
              <td :class="{ muted: !t.atendio }">{{ t.atendio || '—' }}</td>
              <td><EstadoBadge :estado="t.estado" /></td>
              <td v-if="esAdmin" style="text-align:right">
                <button v-if="t.estado === 'EN_ESPERA'" class="btn-icono" title="Cancelar turno" :aria-label="'Cancelar ' + t.codigo" @click="cancelar(t)">✕</button>
              </td>
            </tr>
          </tbody>
        </table>
        <div v-if="!datos.turnos.length" class="vacio-tabla">Sin turnos para ese filtro.</div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref } from 'vue'
import StaffHeader from '../components/StaffHeader.vue'
import EstadoBadge from '../components/EstadoBadge.vue'
import api, { mensaje } from '../api'
import { hora, hoyISO, minutos } from '../formato'
import { toast } from '../toast'
import { useSesion } from '../stores/sesion'

const ESTADOS = { EN_ESPERA: 'En espera', LLAMADO: 'Llamado', ATENDIDO: 'Atendido', NO_PRESENTADO: 'No se presentó', CANCELADO: 'Cancelado' }
const sesion = useSesion()
const esAdmin = computed(() => sesion.rol === 'ADMIN')
const filtro = reactive({ fecha: hoyISO(), servicio: null, estado: '' })
const servicios = ref([])
const datos = ref(null)

const esperaActual = t => (t.estado === 'EN_ESPERA' && filtro.fecha === hoyISO()
  ? Math.round((Date.now() - new Date(t.hora_creacion)) / 60000) : null)

async function buscar() {
  try {
    const params = { fecha: filtro.fecha || undefined, servicio: filtro.servicio ?? undefined, estado: filtro.estado || undefined }
    datos.value = (await api.get('/turnos', { params })).data
  } catch (e) { toast(mensaje(e), true) }
}

async function cancelar(t) {
  if (!confirm(`¿Cancelar el turno ${t.codigo}? El cliente ya no será llamado.`)) return
  try {
    await api.put(`/turnos/${t.id_turno}/estado`, { estado: 'CANCELADO' })
    toast(`${t.codigo} cancelado`)
    buscar()
  } catch (e) { toast(mensaje(e), true) }
}

onMounted(async () => {
  servicios.value = (await api.get('/servicios')).data
  buscar()
})
</script>

<style scoped>
.filtros{display:grid;grid-template-columns:repeat(3,1fr) auto;gap:16px;padding:20px;align-items:end;margin-bottom:20px}
.filtros .btn{height:44px}
.totales{display:grid;grid-template-columns:repeat(5,1fr);gap:16px;margin-bottom:20px}
.tot{padding:18px 20px}
.tot b{font-family:var(--f-titulo);font-size:28px;display:block}
.tot span{font-size:13px;color:var(--gris)}
@media (max-width:900px){.filtros{grid-template-columns:1fr 1fr}.totales{grid-template-columns:repeat(2,1fr)}}
</style>
