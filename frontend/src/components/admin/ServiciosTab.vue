<template>
  <div class="panel tabla-wrap">
    <table class="tabla">
      <thead><tr><th>Prefijo</th><th>Servicio</th><th>Descripción</th><th>Ventanillas</th><th>Turnos hoy</th><th>Estado</th><th></th></tr></thead>
      <tbody>
        <tr v-for="s in servicios" :key="s.id_servicio">
          <td><span class="pref sm" :class="{ off: !s.activo }">{{ s.prefijo }}</span></td>
          <td><b>{{ s.nombre }}</b></td>
          <td class="muted">{{ s.descripcion || '—' }}</td>
          <td>{{ ventanillasDe(s) }}</td>
          <td>{{ s.turnos_hoy }}</td>
          <td><EstadoBadge :estado="s.activo ? 'activo' : 'inactivo'" /></td>
          <td style="white-space:nowrap;text-align:right">
            <button class="btn-icono" :aria-label="'Editar ' + s.nombre" title="Editar" @click="abrir(s)">✎</button>
            <button class="btn-icono" :aria-label="(s.activo ? 'Desactivar ' : 'Activar ') + s.nombre" :title="s.activo ? 'Desactivar' : 'Activar'" @click="alternar(s)">{{ s.activo ? '⏻' : '○' }}</button>
          </td>
        </tr>
      </tbody>
    </table>
    <div v-if="!servicios.length" class="vacio-tabla">No hay servicios. Cree el primero con «Nuevo servicio».</div>
  </div>

  <Modal v-if="form" :titulo="form.id_servicio ? 'Editar servicio' : 'Nuevo servicio'" subtitulo="Aparecerá en el kiosco al guardarlo si está activo"
         :texto-guardar="form.id_servicio ? 'Guardar cambios' : 'Guardar servicio'" :guardando="guardando" @cerrar="form = null" @guardar="guardar">
    <div class="campo"><label for="s-nombre">Nombre del servicio</label><input id="s-nombre" v-model="form.nombre" required maxlength="80"></div>
    <div class="fila2">
      <div class="campo" :class="{ error: errorPrefijo }" style="width:140px">
        <label for="s-pref">Prefijo</label>
        <input id="s-pref" v-model="form.prefijo" required maxlength="1" style="text-transform:uppercase;font-weight:700">
      </div>
      <div class="campo" style="flex:1">
        <label>Vista previa del turno</label>
        <input :value="vista" disabled>
      </div>
    </div>
    <div class="campo"><label for="s-desc">Descripción (opcional)</label><input id="s-desc" v-model="form.descripcion" maxlength="200"></div>
    <label class="interruptor"><span><b>Activo</b><br><small class="muted">Mostrar este servicio en el kiosco</small></span><input v-model="form.activo" type="checkbox"></label>
    <p v-if="errorForm" class="alerta" role="alert">⚠ {{ errorForm }}</p>
  </Modal>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue'
import Modal from '../Modal.vue'
import EstadoBadge from '../EstadoBadge.vue'
import api, { mensaje } from '../../api'
import { toast } from '../../toast'

const servicios = ref([])
const ventanillas = ref([])
const form = ref(null)
const errorForm = ref('')
const guardando = ref(false)

const errorPrefijo = computed(() => errorForm.value.includes('prefijo'))
const vista = computed(() => {
  const p = (form.value?.prefijo || '').toUpperCase()
  return /^[A-Z]$/.test(p) ? `${p}-001, ${p}-002, ${p}-003…` : 'Escriba una letra'
})

async function cargar() {
  const [s, v] = await Promise.all([api.get('/servicios'), api.get('/ventanillas')])
  servicios.value = s.data
  ventanillas.value = v.data
}
const ventanillasDe = s => ventanillas.value.filter(v => v.servicios.some(x => x.id_servicio === s.id_servicio)).map(v => v.nombre).join(', ') || '—'

function abrir(s = null) {
  errorForm.value = ''
  form.value = s ? { ...s, descripcion: s.descripcion || '' } : { nombre: '', prefijo: '', descripcion: '', activo: true }
}

async function guardar() {
  guardando.value = true
  errorForm.value = ''
  const datos = { nombre: form.value.nombre, prefijo: form.value.prefijo, descripcion: form.value.descripcion || null, activo: form.value.activo }
  try {
    if (form.value.id_servicio) await api.put(`/servicios/${form.value.id_servicio}`, datos)
    else await api.post('/servicios', datos)
    toast(`Servicio «${datos.nombre}» guardado`)
    form.value = null
    cargar()
  } catch (e) {
    errorForm.value = mensaje(e)
  } finally {
    guardando.value = false
  }
}

async function alternar(s) {
  try {
    await api.put(`/servicios/${s.id_servicio}`, { nombre: s.nombre, prefijo: s.prefijo, descripcion: s.descripcion, activo: !s.activo })
    toast(`«${s.nombre}» ${s.activo ? 'desactivado: ya no aparece en el kiosco' : 'activado'}`)
    cargar()
  } catch (e) { toast(mensaje(e), true) }
}

onMounted(cargar)
defineExpose({ abrir: () => abrir() })
</script>

<style scoped>
.fila2{display:flex;gap:16px}
</style>
