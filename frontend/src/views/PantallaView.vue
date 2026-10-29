<template>
  <section class="view tv">
    <header class="tv-top">
      <Logo to="/pantalla" />
      <div class="hora">{{ reloj.hora }}</div>
    </header>

    <div class="tv-grid">
      <div ref="caja" class="actual">
        <template v-if="datos.actual">
          <div class="lbl">TURNO ACTUAL</div>
          <div class="code">{{ datos.actual.codigo }}</div>
          <div class="pill">➜ {{ datos.actual.ventanilla?.toUpperCase() }}</div>
          <div class="svc-n">{{ datos.actual.servicio }}</div>
        </template>
        <div v-else class="vacio-tv">Bienvenido, en breve le atenderemos</div>
      </div>
      <aside class="ultimos">
        <h2>Últimos llamados</h2>
        <div v-for="t in datos.ultimos" :key="t.id_turno" class="ult">
          <div><b>{{ t.codigo }}</b><small>{{ t.servicio }}</small></div>
          <span>{{ t.ventanilla }}</span>
        </div>
        <p v-if="!datos.ultimos.length" class="tenue">Los turnos anteriores aparecerán aquí.</p>
      </aside>
    </div>

    <div class="tv-aviso">
      <span>{{ sinConexion ? '⚠ Sin conexión con el servidor. Reintentando…' : 'Por favor, esté atento a su número. Si no se presenta al ser llamado, su turno será marcado como no presentado.' }}</span>
      <button @click="activarSonido">{{ audio ? 'Sonido activado' : 'Activar sonido' }}</button>
    </div>
  </section>
</template>

<script setup>
import { onMounted, onUnmounted, reactive, ref } from 'vue'
import Logo from '../components/Logo.vue'
import api from '../api'
import { useReloj } from '../reloj'

const reloj = useReloj()
const datos = reactive({ actual: null, ultimos: [] })
const caja = ref(null)
const audio = ref(null)
const sinConexion = ref(false)
let ultimoAnuncio, intervalo

// RNF-02: consulta cada 3 segundos
async function consultar() {
  try {
    const { data } = await api.get('/turnos/actual')
    Object.assign(datos, data)
    sinConexion.value = false
    if (ultimoAnuncio !== undefined && data.anuncio && data.anuncio !== ultimoAnuncio) anunciar()
    ultimoAnuncio = data.anuncio
  } catch {
    sinConexion.value = true
  }
}

function anunciar() {
  const el = caja.value
  el.classList.remove('flash'); void el.offsetWidth; el.classList.add('flash')
  tono()
}

function tono() {
  const ctx = audio.value
  if (!ctx) return
  ;[880, 660].forEach((f, i) => {
    const o = ctx.createOscillator(), g = ctx.createGain()
    o.frequency.value = f; o.connect(g); g.connect(ctx.destination)
    const t = ctx.currentTime + i * 0.35
    g.gain.setValueAtTime(0.0001, t)
    g.gain.exponentialRampToValueAtTime(0.3, t + 0.03)
    g.gain.exponentialRampToValueAtTime(0.0001, t + 0.3)
    o.start(t); o.stop(t + 0.32)
  })
}

// Los navegadores solo permiten sonido después de una interacción del usuario.
function activarSonido() {
  try {
    audio.value = audio.value || new (window.AudioContext || window.webkitAudioContext)()
    audio.value.resume()
    tono()
  } catch { /* sin soporte de audio */ }
}

onMounted(() => { consultar(); intervalo = setInterval(consultar, 3000) })
onUnmounted(() => clearInterval(intervalo))
</script>

<style scoped>
.tv{background:var(--noche);color:#fff}
.tv-top{display:flex;justify-content:space-between;align-items:center;padding:18px 36px;border-bottom:1px solid rgba(255,255,255,.08)}
.tv-top .hora{font-family:var(--f-titulo);font-weight:600;font-size:24px}
.tv-grid{flex:1;display:grid;grid-template-columns:1.6fr 1fr;gap:28px;padding:32px 36px}
.actual{border:3px solid var(--turq);border-radius:24px;background:rgba(255,255,255,.06);display:flex;flex-direction:column;align-items:center;justify-content:center;padding:32px;text-align:center}
.actual .lbl{letter-spacing:.25em;font-size:clamp(16px,1.6vw,28px);opacity:.8;font-weight:600}
.actual .code{font-family:var(--f-titulo);font-weight:800;font-size:clamp(96px,13vw,240px);line-height:1;margin:14px 0 24px}
.pill{display:inline-flex;align-items:center;gap:10px;background:var(--turq);color:var(--noche);font-family:var(--f-titulo);font-weight:700;font-size:clamp(22px,2.6vw,44px);border-radius:999px;padding:10px 36px}
.svc-n{margin-top:14px;opacity:.85;font-size:clamp(18px,1.6vw,28px)}
.actual.flash{animation:flash 1s ease-in-out 3}
@keyframes flash{0%,100%{background:rgba(255,255,255,.06)}50%{background:rgba(20,184,166,.4)}}
.vacio-tv{opacity:.75;font-size:clamp(22px,2vw,32px)}
.ultimos h2{font-size:clamp(18px,1.6vw,28px);margin-bottom:14px}
.ult{display:flex;justify-content:space-between;align-items:center;background:rgba(255,255,255,.08);border-radius:14px;padding:14px 20px;margin-bottom:12px}
.ult b{font-family:var(--f-titulo);font-size:clamp(24px,2.4vw,44px);display:block;line-height:1.1}
.ult small{opacity:.7;font-size:clamp(12px,1vw,18px)}
.ult span{font-weight:600;font-size:clamp(14px,1.3vw,24px);opacity:.9}
.tenue{opacity:.6;font-size:14px}
.tv-aviso{background:rgba(0,0,0,.25);padding:12px 36px;font-size:clamp(13px,1.1vw,20px);display:flex;justify-content:space-between;gap:12px;align-items:center}
.tv-aviso button{background:transparent;border:1px solid rgba(255,255,255,.35);color:#fff;border-radius:999px;padding:5px 14px;font-size:13px;flex:none}
.actual .code,.pill{white-space:nowrap}
.actual,.ultimos{min-width:0}
@media (max-width:860px){.tv-grid{grid-template-columns:1fr;padding:20px 16px}.tv-top,.tv-aviso{padding:14px 16px}.actual{padding:24px 12px}.actual .code{font-size:19vw}.pill{font-size:5.5vw;padding:8px 22px}}
</style>
