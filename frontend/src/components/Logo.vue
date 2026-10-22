<template>
  <RouterLink :to="to" class="logo">
    <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true">
      <path d="M3 7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v2a3 3 0 0 0 0 6v2a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-2a3 3 0 0 0 0-6z" />
    </svg>
    TurnoFácil
  </RouterLink>
</template>

<script setup>
defineProps({ to: { type: String, default: '/' } })
</script>
