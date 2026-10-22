import { defineStore } from 'pinia'
import api from '../api'

export const useSesion = defineStore('sesion', {
  state: () => ({
    token: localStorage.getItem('turnofacil-token'),
    usuario: JSON.parse(localStorage.getItem('turnofacil-usuario') || 'null')
  }),
  getters: {
    rol: s => s.usuario?.rol,
    iniciales: s => (s.usuario?.nombre || '').split(' ').map(p => p[0]).slice(0, 2).join('').toUpperCase(),
    inicio: s => (s.usuario?.rol === 'ADMIN' ? '/admin' : '/recepcion')
  },
  actions: {
    async entrar(usuario, contrasena) {
      const { data } = await api.post('/auth/login', { usuario, contrasena })
      this.token = data.access_token
      this.usuario = data.usuario
      localStorage.setItem('turnofacil-token', this.token)
      localStorage.setItem('turnofacil-usuario', JSON.stringify(this.usuario))
    },
    salir() {
      this.token = null
      this.usuario = null
      localStorage.removeItem('turnofacil-token')
      localStorage.removeItem('turnofacil-usuario')
    }
  }
})
