import axios from 'axios'

const api = axios.create({ baseURL: '/api' })

api.interceptors.request.use(config => {
  const token = localStorage.getItem('turnofacil-token')
  if (token) config.headers.Authorization = `Bearer ${token}`
  return config
})

api.interceptors.response.use(r => r, error => {
  if (error.response?.status === 401 && localStorage.getItem('turnofacil-token')) {
    localStorage.removeItem('turnofacil-token')
    localStorage.removeItem('turnofacil-usuario')
    if (!location.pathname.startsWith('/login')) location.href = '/login'
  }
  return Promise.reject(error)
})

/** Mensaje legible de un error de la API. */
export function mensaje(error) {
  const d = error?.response?.data?.detail
  if (typeof d === 'string') return d
  if (Array.isArray(d)) return d.map(e => e.msg.replace(/^Value error, /, '')).join('. ')
  if (!error?.response) return 'No hay conexión con el servidor. Intente de nuevo.'
  return 'Ocurrió un error inesperado.'
}

export default api
