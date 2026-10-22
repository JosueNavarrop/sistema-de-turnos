<template>
  <section class="view">
    <header class="k-top">
      <Logo to="/kiosco" />
      <div><div class="hora">{{ reloj.hora }}</div><div class="fecha">{{ reloj.fecha }}</div></div>
    </header>

    <div class="k-body">
      <!-- P1 · Elegir servicio -->
      <div v-if="!ticket" class="k-elegir">
        <div class="hola">Bienvenido</div>
        <h1>Toque el servicio que necesita</h1>
        <p v-if="error" class="alerta" style="justify-content:center">{{ error }}</p>
        <div v-else-if="cargando" class="muted">Cargando servicios…</div>
        <div v-else-if="!servicios.length" class="muted">No hay servicios disponibles en este momento.</div>
        <div class="cards">
          <button v-for="s in servicios" :key="s.id_servicio" class="svc" :disabled="generando" @click="generar(s)">
            <span class="pref">{{ s.prefijo }}</span>
            <h3>{{ s.nombre }}</h3>
            <p>{{ s.descripcion }}</p>
          </button>
        </div>
        <p class="ayuda">ⓘ Su turno aparecerá en pantalla. Espere a que llamen su número.</p>
      </div>

      <!-- P1b · Turno generado -->
      <div v-else class="ticket-wrap">
        <span class="ok">✓ Turno generado con éxito</span>
        <div class="ticket">
          <div class="lbl">SU TURNO ES</div>
          <div class="code">{{ ticket.codigo }}</div>
          <div class="svcname">{{ ticket.servicio }} · {{ ticket.descripcion }}</div>
          <div class="stats">
            <div><b>{{ ticket.delante }}</b><span>personas delante</span></div>
            <div><b>{{ ticket.delante ? '~ ' + ticket.espera_estimada_min + ' min' : 'Ahora' }}</b><span>espera estimada</span></div>
          </div>
        </div>
        <div class="cuenta">Esta pantalla volverá al inicio en {{ segundos }} segundos ·
          <button class="link" @click="volver">Volver ahora</button></div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue'
import Logo from '../components/Logo.vue'
import api, { mensaje } from '../api'
import { useReloj } from '../reloj'

const reloj = useReloj()
const servicios = ref([])
const cargando = ref(true)
const error = ref('')
const ticket = ref(null)
const generando = ref(false)
const segundos = ref(5)
let cuenta, refresco

async function cargar() {
  try {
    servicios.value = (await api.get('/servicios', { params: { activos: true } })).data
    error.value = ''
  } catch (e) {
    error.value = mensaje(e)
  } finally {
    cargando.value = false
  }
}

async function generar(s) {
  generando.value = true
  try {
    const { data } = await api.post('/turnos', { id_servicio: s.id_servicio })
    ticket.value = { ...data, descripcion: s.descripcion }
    segundos.value = 5
    clearInterval(cuenta)
    cuenta = setInterval(() => { if (--segundos.value <= 0) volver() }, 1000)
  } catch (e) {
    error.value = mensaje(e) + ' Intente de nuevo.'
    setTimeout(() => (error.value = ''), 4000)
    cargar()
  } finally {
    generando.value = false
  }
}

function volver() {
  clearInterval(cuenta)
  ticket.value = null
}

onMounted(() => { cargar(); refresco = setInterval(cargar, 30000) })
onUnmounted(() => { clearInterval(cuenta); clearInterval(refresco) })
</script>

<style scoped>
.k-top{background:var(--noche);color:#fff;display:flex;justify-content:space-between;align-items:center;padding:16px 32px}
.k-top .hora{font-family:var(--f-titulo);font-weight:600;font-size:20px;text-align:right}
.k-top .fecha{font-size:12px;opacity:.75;text-align:right}
.k-body{flex:1;display:flex;align-items:center;justify-content:center;padding:40px 24px}
.k-elegir{text-align:center;width:100%;max-width:1000px}
.hola{color:var(--azul);font-size:15px;font-weight:500}
.k-elegir h1{font-size:clamp(26px,3.4vw,38px);margin:6px 0 32px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(240px,1fr));gap:24px}
.svc{background:var(--surface);border:1px solid var(--borde);border-radius:16px;padding:26px;text-align:left;box-shadow:var(--sombra);min-height:190px;display:flex;flex-direction:column;transition:transform .12s,border-color .12s}
.svc:hover{border-color:var(--azul)}
.svc:active{transform:scale(.98)}
.svc h3{font-size:21px;margin-top:auto;padding-top:28px}
.svc p{margin:2px 0 0;color:var(--gris);font-size:14px}
.ayuda{margin-top:28px;color:var(--gris);font-size:14px}
.ticket-wrap{text-align:center}
.ok{display:inline-flex;align-items:center;gap:6px;background:#CCFBF1;color:#0F766E;font-weight:600;font-size:14px;border-radius:999px;padding:6px 16px}
.ticket{background:var(--surface);border-radius:20px;box-shadow:0 10px 40px rgba(15,23,42,.12);padding:36px 44px;margin:20px auto 16px;width:min(460px,100%);animation:pop .35s ease-out}
@keyframes pop{from{transform:scale(.94);opacity:0}to{transform:none;opacity:1}}
.ticket .lbl{font-size:13px;letter-spacing:.12em;color:var(--gris);font-weight:600}
.ticket .code{font-family:var(--f-titulo);font-weight:800;color:var(--azul);font-size:clamp(64px,10vw,112px);line-height:1;margin:12px 0}
.ticket .stats{display:grid;grid-template-columns:1fr 1fr;border-top:1px solid var(--borde);margin-top:22px;padding-top:18px}
.ticket .stats b{font-family:var(--f-titulo);font-size:24px;display:block}
.ticket .stats span{font-size:13px;color:var(--gris)}
.cuenta{color:var(--gris);font-size:14px}
.link{background:none;border:0;color:var(--azul);font-weight:600;text-decoration:underline;padding:4px}
</style>
