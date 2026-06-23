<!-- App.vue -->
<template>
  <template v-if="$route.meta.layout === 'none'">
    <RouterView />
    <ConfirmModal />
    <ToastContainer />
  </template>
</template>

<script setup>
import ConfirmModal         from '@/components/modals/ConfirmModal.vue'
import ToastContainer from '@/components/modals/ToastContainer.vue'
</script>
