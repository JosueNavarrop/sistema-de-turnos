<template>
  <span class="badge" :class="'b-' + estado">{{ ETIQUETAS[estado] || estado }}</span>
</template>

<script setup>
defineProps({ estado: String })
const ETIQUETAS = {
  EN_ESPERA: 'En espera', LLAMADO: 'Llamado', ATENDIDO: 'Atendido',
  NO_PRESENTADO: 'No se presentó', CANCELADO: 'Cancelado', activo: 'Activo', inactivo: 'Inactivo'
}
</script>
