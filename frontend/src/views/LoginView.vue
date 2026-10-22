<template>
  <div class="login">
    <aside class="marca">
      <Logo />
      <div>
        <h1>Atención ordenada, clientes tranquilos.</h1>
        <p>Acceso exclusivo para recepcionistas y administradores del centro de atención.</p>
      </div>
      <small>Grupo 2 · Ingeniería de Software II · UNICARIBE</small>
    </aside>
    <main class="zona">
      <form class="form" @submit.prevent="entrar">
        <div>
          <h2>Iniciar sesión</h2>
          <p class="muted">Ingrese sus credenciales para continuar</p>
        </div>
        <div class="campo">
          <label for="usuario">Usuario</label>
          <input id="usuario" v-model.trim="usuario" autocomplete="username" placeholder="Ej. aperez" required autofocus>
        </div>
        <div class="campo">
          <label for="clave">Contraseña</label>
          <input id="clave" v-model="contrasena" type="password" autocomplete="current-password" required>
        </div>
        <p v-if="error" class="alerta" role="alert">⚠ {{ error }}</p>
        <button class="btn btn-azul" :disabled="cargando">{{ cargando ? 'Entrando…' : 'Entrar' }}</button>
        <RouterLink to="/" class="muted volver">← Volver al inicio</RouterLink>
      </form>
    </main>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import Logo from '../components/Logo.vue'
import { mensaje } from '../api'
import { useSesion } from '../stores/sesion'

const sesion = useSesion()
const router = useRouter()
const route = useRoute()
const usuario = ref('')
const contrasena = ref('')
const error = ref('')
const cargando = ref(false)

async function entrar() {
  error.value = ''
  cargando.value = true
  try {
    await sesion.entrar(usuario.value, contrasena.value)
    const volver = route.query.volver
    router.push(volver && volver !== '/login' ? volver : sesion.inicio)
  } catch (e) {
    error.value = mensaje(e)
  } finally {
    cargando.value = false
  }
}
</script>

<style scoped>
.login{min-height:100vh;display:grid;grid-template-columns:minmax(320px,520px) 1fr}
.marca{background:var(--noche);color:#fff;padding:56px;display:flex;flex-direction:column;justify-content:space-between;gap:32px}
.marca h1{font-size:clamp(28px,3vw,40px);line-height:1.2}
.marca p{color:#C7D2FE;font-size:17px;line-height:1.5}
.marca small{color:#A5B4FC}
.zona{display:grid;place-items:center;padding:32px}
.form{width:min(400px,100%);display:flex;flex-direction:column;gap:20px}
.form h2{font-size:30px}
.form p{margin:6px 0 0}
.form .btn{height:48px}
.volver{font-size:14px;text-align:center;text-decoration:none}
@media (max-width:760px){.login{grid-template-columns:1fr}.marca{padding:28px;gap:16px}.marca p,.marca small{display:none}}
</style>
