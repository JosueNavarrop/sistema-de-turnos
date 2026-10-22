<template>
  <div class="panel tabla-wrap">
    <table class="tabla">
      <thead><tr><th>Nombre</th><th>Usuario</th><th>Rol</th><th>Ventanilla</th><th>Último acceso</th><th>Estado</th><th></th></tr></thead>
      <tbody>
        <tr v-for="u in usuarios" :key="u.id_usuario">
          <td><span class="persona"><span class="avatar">{{ iniciales(u.nombre) }}</span><b>{{ u.nombre }}</b></span></td>
          <td class="muted">{{ u.usuario }}</td>
          <td><span class="rol" :class="u.rol">{{ u.rol === 'ADMIN' ? 'Administrador' : 'Recepcionista' }}</span></td>
          <td :class="{ muted: !u.ventanilla }">{{ u.ventanilla || (u.rol === 'ADMIN' ? '—' : 'Sin asignar') }}</td>
          <td>{{ fechaHora(u.ultimo_acceso) }}</td>
          <td><EstadoBadge :estado="u.activo ? 'activo' : 'inactivo'" /></td>
          <td style="text-align:right"><button class="btn-icono" :aria-label="'Editar ' + u.nombre" title="Editar" @click="abrir(u)">✎</button></td>
        </tr>
      </tbody>
    </table>
  </div>

  <Modal v-if="form" :titulo="form.id_usuario ? 'Editar usuario' : 'Nuevo usuario'" subtitulo="Acceso del personal al sistema"
         :texto-guardar="form.id_usuario ? 'Guardar cambios' : 'Crear usuario'" :guardando="guardando" @cerrar="form = null" @guardar="guardar">
    <template #icono>👤</template>
    <div class="campo"><label for="u-nombre">Nombre completo</label><input id="u-nombre" v-model="form.nombre" required maxlength="100"></div>
    <div class="fila2">
      <div class="campo"><label for="u-user">Usuario</label><input id="u-user" v-model.trim="form.usuario" required minlength="3" maxlength="50" pattern="[a-zA-Z0-9._\-]+" autocomplete="off"></div>
      <div class="campo">
        <label for="u-clave">Contraseña</label>
        <input id="u-clave" v-model="form.contrasena" type="password" :required="!form.id_usuario" minlength="6" autocomplete="new-password">
        <small>{{ form.id_usuario ? 'Déjela vacía para no cambiarla' : 'Mínimo 6 caracteres' }}</small>
      </div>
    </div>
    <div class="campo">
      <label>Rol</label>
      <div class="roles">
        <label v-for="r in ROLES" :key="r.valor" class="rol-op" :class="{ on: form.rol === r.valor }">
          <input v-model="form.rol" type="radio" :value="r.valor"><span><b>{{ r.nombre }}</b><br><small class="muted">{{ r.ayuda }}</small></span>
        </label>
      </div>
    </div>
    <div v-if="form.rol === 'RECEPCIONISTA'" class="campo">
      <label for="u-vent">Ventanilla asignada</label>
      <select id="u-vent" v-model="form.id_ventanilla">
        <option :value="null">Sin asignar</option>
        <option v-for="v in ventanillas" :key="v.id_ventanilla" :value="v.id_ventanilla">
          {{ v.nombre }} · {{ v.servicios.map(s => s.nombre).join(', ') || 'sin servicios' }}{{ v.activo ? '' : ' (inactiva)' }}
        </option>
      </select>
    </div>
    <label class="interruptor"><span><b>Activo</b><br><small class="muted">Puede iniciar sesión</small></span><input v-model="form.activo" type="checkbox"></label>
    <p v-if="errorForm" class="alerta" role="alert">⚠ {{ errorForm }}</p>
  </Modal>
</template>

<script setup>
import { onMounted, ref } from 'vue'
import Modal from '../Modal.vue'
import EstadoBadge from '../EstadoBadge.vue'
import api, { mensaje } from '../../api'
import { fechaHora } from '../../formato'
import { toast } from '../../toast'

const ROLES = [
  { valor: 'RECEPCIONISTA', nombre: 'Recepcionista', ayuda: 'Llama y cierra turnos' },
  { valor: 'ADMIN', nombre: 'Administrador', ayuda: 'Configura el sistema' }
]
const usuarios = ref([])
const ventanillas = ref([])
const form = ref(null)
const errorForm = ref('')
const guardando = ref(false)

const iniciales = n => n.split(' ').map(p => p[0]).slice(0, 2).join('').toUpperCase()

async function cargar() {
  const [u, v] = await Promise.all([api.get('/usuarios'), api.get('/ventanillas')])
  usuarios.value = u.data
  ventanillas.value = v.data
}

function abrir(u = null) {
  errorForm.value = ''
  form.value = u
    ? { id_usuario: u.id_usuario, nombre: u.nombre, usuario: u.usuario, contrasena: '', rol: u.rol, id_ventanilla: u.id_ventanilla, activo: u.activo }
    : { nombre: '', usuario: '', contrasena: '', rol: 'RECEPCIONISTA', id_ventanilla: null, activo: true }
}

async function guardar() {
  guardando.value = true
  errorForm.value = ''
  const { id_usuario, ...datos } = form.value
  if (!datos.contrasena) datos.contrasena = null
  try {
    if (id_usuario) await api.put(`/usuarios/${id_usuario}`, datos)
    else await api.post('/usuarios', datos)
    toast(`Usuario «${datos.usuario}» guardado`)
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
.persona{display:flex;align-items:center;gap:10px}
.rol{font-size:12px;font-weight:600;border-radius:8px;padding:3px 10px;background:var(--azul-suave);color:var(--azul)}
.rol.ADMIN{background:var(--bg);color:var(--noche);border:1px solid var(--borde)}
.fila2{display:grid;grid-template-columns:1fr 1fr;gap:16px}
.roles{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.rol-op{display:flex;gap:10px;align-items:flex-start;border:1px solid var(--borde);border-radius:12px;padding:12px;cursor:pointer}
.rol-op.on{border:2px solid var(--azul);background:var(--azul-suave)}
.rol-op input{accent-color:var(--azul);margin-top:3px}
@media (max-width:560px){.fila2,.roles{grid-template-columns:1fr}}
</style>
