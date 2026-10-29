export const hora = t => (t ? new Date(t).toLocaleTimeString('es-DO', { hour: 'numeric', minute: '2-digit' }) : '—')
export function minutos(m) {
  if (m == null) return '—'
  if (m < 1) return '< 1 min'
  if (m < 60) return `${m} min`
  const h = Math.floor(m / 60), resto = m % 60
  return resto ? `${h} h ${resto} min` : `${h} h`
}
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
