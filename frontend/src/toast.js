import { reactive } from 'vue'

export const aviso = reactive({ texto: '', error: false, visible: false })
let temporizador

export function toast(texto, error = false) {
  Object.assign(aviso, { texto, error, visible: true })
  clearTimeout(temporizador)
  temporizador = setTimeout(() => (aviso.visible = false), 3000)
}
