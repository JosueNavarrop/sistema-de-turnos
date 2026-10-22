<template>
  <div class="view">
    <StaffHeader />
    <p v-if="error" class="alerta" style="margin:20px 28px 0">⚠ {{ error }}</p>
    <div v-if="panel" class="r-grid">
      <!-- P4 · Atendiendo -->
      <div v-if="panel.abierto" class="panel atn">
        <div class="atn-h"><h2>Atendiendo ahora</h2><EstadoBadge estado="LLAMADO" /></div>
        <div class="code">{{ panel.abierto.codigo }}</div>
        <div class="meta">{{ panel.abierto.servicio }} · llamado a las {{ hora(panel.abierto.hora_llamado) }} · esperó {{ minutos(panel.abierto.espera_min) }}</div>
        <div class="acciones">
          <button class="btn btn-verde" :disabled="ocupado" @click="cerrar('ATENDIDO')">✓ Atendido</button>
          <button class="btn btn-rojo" :disabled="ocupado" @click="cerrar('NO_PRESENTADO')">✕ No se presentó</button>
          <button class="btn btn-linea" :disabled="ocupado" @click="rellamar">↻ Volver a llamar</button>
        </div>
      </div>

      <!-- P4b · Sin turno abierto -->
      <div v-else class="panel atn">
        <div class="vacio">
          <div class="ico">
            <svg width="30" height="30" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8"><circle cx="12" cy="7" r="3.5" /><path d="M5 20a7 7 0 0 1 14 0" /></svg>
          </div>
          <h2>No está atendiendo a nadie</h2>
          <p v-if="panel.en_espera">Hay {{ panel.en_espera }} {{ panel.en_espera === 1 ? 'cliente esperando' : 'clientes esperando' }}. Pulse «Llamar siguiente» para anunciar el próximo turno en pantalla.</p>
          <p v-else>No hay clientes en espera. Los turnos nuevos del kiosco aparecerán aquí.</p>
          <span v-if="panel.ultimo" class="chip">Último atendido: {{ panel.ultimo.codigo }} a las {{ hora(panel.ultimo.hora_fin) }}</span>
        </div>
      </div>

      <div>
        <div class="panel cola">
          <h3>Clientes en espera</h3>
          <div v-for="c in panel.cola" :key="c.prefijo" class="fila">
            <span class="pref sm">{{ c.prefijo }}</span><span>{{ c.servicio }}</span><b>{{ c.en_espera }}</b>
          </div>
          <button class="btn btn-azul siguiente" :disabled="!!panel.abierto || !panel.en_espera || ocupado" @click="llamar">
            📣 Llamar siguiente
          </button>
          <p class="nota">{{ nota }}</p>
        </div>
        <div class="kpis">
          <div class="panel kpi"><b>{{ panel.atendidos }}</b><span>Atendidos hoy</span></div>
          <div class="panel kpi"><b>{{ panel.no_presentados }}</b><span>No presentados</span></div>
          <div class="panel kpi"><b>{{ minutos(panel.espera_promedio_min) }}</b><span>Espera prom.</span></div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, onMounted, onUnmounted, ref } from 'vue'
import StaffHeader from '../components/StaffHeader.vue'
import EstadoBadge from '../components/EstadoBadge.vue'
import api, { mensaje } from '../api'
import { hora, minutos } from '../formato'
import { toast } from '../toast'

const panel = ref(null)
const error = ref('')
const ocupado = ref(false)
let intervalo

const nota = computed(() => {
  const p = panel.value
  if (p.abierto) return 'Cierre el turno actual para llamar al siguiente.'
  if (p.en_espera) return 'Se llamará al turno en espera más antiguo de ' + p.cola.map(c => c.servicio).join(' o ') + '.'
  return 'No hay turnos en espera para esta ventanilla.'
})

async function cargar() {
  try {
    panel.value = (await api.get('/turnos/mi-ventanilla')).data
    error.value = ''
  } catch (e) {
    error.value = mensaje(e)
  }
}

async function accion(fn, exito) {
  ocupado.value = true
  try {
    const { data } = await fn()
    toast(exito(data))
  } catch (e) {
    toast(mensaje(e), true)
  } finally {
    ocupado.value = false
    cargar()
  }
}

const llamar = () => accion(() => api.post('/turnos/siguiente'), t => `${t.codigo} llamado a ${t.ventanilla}`)
const rellamar = () => accion(() => api.post(`/turnos/${panel.value.abierto.id_turno}/rellamar`), t => `${t.codigo} llamado otra vez`)
const cerrar = estado => accion(() => api.put(`/turnos/${panel.value.abierto.id_turno}/estado`, { estado }),
  t => `${t.codigo} marcado como ${estado === 'ATENDIDO' ? 'atendido' : 'no presentado'}`)

onMounted(() => { cargar(); intervalo = setInterval(cargar, 3000) })
onUnmounted(() => clearInterval(intervalo))
</script>

<style scoped>
.r-grid{flex:1;display:grid;grid-template-columns:1.65fr 1fr;gap:24px;padding:28px;align-items:start;max-width:1400px;width:100%;margin:0 auto}
.atn{min-height:480px;padding:36px;display:flex;flex-direction:column}
.atn-h{display:flex;justify-content:space-between;align-items:center}
.atn-h h2{font-size:19px}
.atn .code{font-family:var(--f-titulo);font-weight:800;color:var(--azul);font-size:clamp(72px,9vw,128px);line-height:1;margin-top:auto}
.atn .meta{color:var(--gris);font-size:15px;margin:10px 0 auto}
.acciones{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:36px}
.acciones .btn{padding:15px}
.vacio{margin:auto;text-align:center;max-width:420px}
.vacio .ico{width:80px;height:80px;border-radius:50%;background:var(--azul-suave);color:var(--azul);display:grid;place-items:center;margin:0 auto 18px}
.vacio h2{font-size:24px;margin-bottom:8px}
.vacio p{color:var(--gris);font-size:15px;margin:0 0 16px}
.cola{padding:24px}
.cola h3{font-size:16px;margin-bottom:12px}
.fila{display:flex;align-items:center;gap:12px;padding:8px 0}
.fila span:not(.pref){flex:1}
.fila b{font-family:var(--f-titulo);font-size:24px}
.siguiente{width:100%;margin-top:14px;padding:16px;font-size:16px}
.nota{font-size:13px;color:var(--gris);margin:10px 0 0}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-top:16px}
.kpi{padding:16px}
.kpi b{font-family:var(--f-titulo);font-size:22px;display:block}
.kpi span{font-size:12px;color:var(--gris)}
@media (max-width:860px){.r-grid{grid-template-columns:1fr;padding:16px}.acciones{grid-template-columns:1fr}.atn{min-height:auto;padding:24px}}
</style>
