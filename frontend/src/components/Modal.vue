<template>
  <div class="velo" @mousedown.self="$emit('cerrar')">
    <div class="modal" role="dialog" aria-modal="true" :aria-label="titulo" @keydown.esc="$emit('cerrar')">
      <div class="modal-h">
        <div class="icono-caja" aria-hidden="true"><slot name="icono">＋</slot></div>
        <div style="flex:1">
          <h2>{{ titulo }}</h2>
          <p v-if="subtitulo">{{ subtitulo }}</p>
        </div>
        <button class="btn-icono" aria-label="Cerrar" @click="$emit('cerrar')">✕</button>
      </div>
      <form @submit.prevent="$emit('guardar')">
        <div class="modal-b"><slot /></div>
        <div class="modal-f">
          <button type="button" class="btn btn-gris" @click="$emit('cerrar')">Cancelar</button>
          <button type="submit" class="btn btn-azul" :disabled="guardando">✓ {{ textoGuardar }}</button>
        </div>
      </form>
    </div>
  </div>
</template>

<script setup>
defineProps({ titulo: String, subtitulo: String, textoGuardar: { type: String, default: 'Guardar' }, guardando: Boolean })
defineEmits(['cerrar', 'guardar'])
</script>
