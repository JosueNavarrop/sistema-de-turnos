import { onMounted, onUnmounted, reactive } from 'vue'
import { fechaLarga, hora } from './formato'

/** Hora y fecha que se actualizan cada segundo. */
export function useReloj() {
  const r = reactive({ hora: '', fecha: '' })
  const tic = () => { const d = new Date(); r.hora = hora(d); r.fecha = fechaLarga(d) }
  let id
  onMounted(() => { tic(); id = setInterval(tic, 1000) })
  onUnmounted(() => clearInterval(id))
  return r
}
