export const hora = t => (t ? new Date(t).toLocaleTimeString('es-DO', { hour: 'numeric', minute: '2-digit' }) : '—')
export const minutos = m => (m == null ? '—' : m < 1 ? '< 1 min' : `${m} min`)
export const hoyISO = () => new Date().toLocaleDateString('en-CA')

export function fechaLarga(d = new Date()) {
  const f = d.toLocaleDateString('es-DO', { weekday: 'long', day: 'numeric', month: 'long', year: 'numeric' })
  return f.charAt(0).toUpperCase() + f.slice(1)
}

export function fechaHora(t) {
  if (!t) return '—'
  const d = new Date(t)
  return d.toLocaleDateString('en-CA') === hoyISO() ? `Hoy, ${hora(t)}` : d.toLocaleDateString('es-DO')
}
