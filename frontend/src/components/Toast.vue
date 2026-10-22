<template>
  <div v-if="aviso.visible" class="toast" :class="{ error: aviso.error }" role="status" aria-live="polite">{{ aviso.texto }}</div>
</template>

<script setup>
import { aviso } from '../toast'
</script>
