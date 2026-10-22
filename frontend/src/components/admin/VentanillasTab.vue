<template>
  <div class="panel tabla-wrap">
    <table class="tabla">
      <thead><tr><th>Ventanilla</th><th>Servicios que atiende</th><th>Recepcionista</th><th>Turno actual</th><th>Estado</th><th></th></tr></thead>
      <tbody>
        <tr v-for="v in ventanillas" :key="v.id_ventanilla">
          <td><b>{{ v.nombre }}</b></td>
          <td><span v-for="s in v.servicios" :key="s.id_servicio" class="etq">{{ s.prefijo }} · {{ s.nombre }}</span><span v-if="!v.servicios.length" class="muted">Ninguno</span></td>
          <td :class="{ muted: !v.recepcionistas.length }">{{ v.recepcionistas.join(', ') || 'Sin asignar' }}</td>
          <td><span v-if="v.turno_actual" class="cod" style="color:var(--azul)">{{ v.turno_actual }}</span><span v-else class="muted">—</span></td>
          <td><EstadoBadge :estado="v.activo ? 'activo' : 'inactivo'" /></td>
          <td style="text-align:right"><button class="btn-icono" :aria-label="'Editar ' + v.nombre" title="Editar" @click="abrir(v)">✎</button></td>
        </tr>
      </tbody>
    </table>
    <div v-if="!ventanillas.length" class="vacio-tabla">No hay ventanillas. Cree la primera con «Nueva ventanilla».</div>
  </div>

  <Modal v-if="form" :titulo="form.id_ventanilla ? 'Editar ventanilla' : 'Nueva ventanilla'" subtitulo="Elija los servicios que se atienden en ella"
         :guardando="guardando" @cerrar="form = null" @guardar="guardar">
    <template #icono>▣</template>
    <div class="campo"><label for="v-nombre">Nombre</label><input id="v-nombre" v-model="form.nombre" required maxlength="30" placeholder="Ej. Ventanilla 4"></div>
    <fieldset class="servicios">
      <legend>Servicios que atiende</legend>
      <label v-for="s in servicios" :key="s.id_servicio" class="opcion">
        <input v-model="form.servicios" type="checkbox" :value="s.id_servicio">
        <span class="pref sm" :class="{ off: !s.activo }">{{ s.prefijo }}</span>{{ s.nombre }}<small v-if="!s.activo" class="muted">(inactivo)</small>
      </label>
    </fieldset>
    <label class="interruptor"><span><b>Activa</b><br><small class="muted">Los recepcionistas pueden llamar turnos desde ella</small></span><input v-model="form.activo" type="checkbox"></label>
    <p v-if="errorForm" class="alerta" role="alert">⚠ {{ errorForm }}</p>
  </Modal>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import Modal from '../Modal.vue'
import EstadoBadge from '../EstadoBadge.vue'
import api, { mensaje } from '../../api'
import { toast } from '../../toast'

const ventanillas = ref([])
const servicios = ref([])
const form = ref(null)
const errorForm = ref('')
const guardando = ref(false)

async function cargar() {
  const [v, s] = await Promise.all([api.get('/ventanillas'), api.get('/servicios')])
  ventanillas.value = v.data
  servicios.value = s.data
}

function abrir(v = null) {
  errorForm.value = ''
  form.value = v
    ? { id_ventanilla: v.id_ventanilla, nombre: v.nombre, activo: v.activo, servicios: v.servicios.map(s => s.id_servicio) }
    : { nombre: '', activo: true, servicios: [] }
}

async function guardar() {
  guardando.value = true
  errorForm.value = ''
  const { id_ventanilla, ...datos } = form.value
  try {
    if (id_ventanilla) await api.put(`/ventanillas/${id_ventanilla}`, datos)
    else await api.post('/ventanillas', datos)
    toast(`«${datos.nombre}» guardada`)
    form.value = null
    cargar()
  } catch (e) {
    errorForm.value = mensaje(e)
  } finally {
    guardando.value = false
  }
}

onMounted(cargar)
defineExpose({ abrir: () => abrir() })
</script>

<style scoped>
.etq{display:inline-block;border:1px solid var(--borde);background:var(--bg);border-radius:8px;padding:2px 10px;font-size:13px;font-weight:500;margin:2px 6px 2px 0}
.servicios{border:0;padding:0;margin:0;display:flex;flex-direction:column;gap:8px}
.servicios legend{font-size:13px;font-weight:500;margin-bottom:6px}
.opcion{display:flex;align-items:center;gap:10px;padding:8px 12px;border:1px solid var(--borde);border-radius:10px;cursor:pointer}
.opcion input{width:18px;height:18px;accent-color:var(--azul)}
</style>
