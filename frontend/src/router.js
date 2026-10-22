import { createRouter, createWebHistory } from 'vue-router'
import { useSesion } from './stores/sesion'

const routes = [
  { path: '/', component: () => import('./views/InicioView.vue') },
  { path: '/kiosco', component: () => import('./views/KioscoView.vue') },
  { path: '/pantalla', component: () => import('./views/PantallaView.vue') },
  { path: '/login', component: () => import('./views/LoginView.vue') },
  { path: '/recepcion', component: () => import('./views/RecepcionView.vue'), meta: { roles: ['RECEPCIONISTA'] } },
  { path: '/admin', component: () => import('./views/AdminView.vue'), meta: { roles: ['ADMIN'] } },
  { path: '/turnos', component: () => import('./views/TurnosView.vue'), meta: { roles: ['ADMIN', 'RECEPCIONISTA'] } },
  { path: '/:pathMatch(.*)*', redirect: '/' }
]

const router = createRouter({ history: createWebHistory(), routes })

// Guardia por rol: sin sesión → login; rol equivocado → su propio panel.
router.beforeEach(to => {
  const roles = to.meta.roles
  if (!roles) return true
  const sesion = useSesion()
  if (!sesion.token) return { path: '/login', query: { volver: to.fullPath } }
  if (!roles.includes(sesion.rol)) return sesion.inicio
  return true
})

export default router
