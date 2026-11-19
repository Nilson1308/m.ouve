<template>
  <div id="app" class="min-h-screen flex flex-col">
    <router-view v-slot="{ Component }">
      <transition name="fade" mode="out-in">
        <component :is="Component" />
      </transition>
    </router-view>

    <!-- Dialog Global -->
    <AppDialog ref="appDialogRef" />

    <PwaUpdater />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { useThemeStore } from '@/stores/theme'
import { useDialog } from '@/composables/useDialog'
import AppDialog from '@/components/shared/AppDialog.vue'
import PwaUpdater from '@/components/pwa/PwaUpdater.vue'

useThemeStore()
const authStore = useAuthStore()
const appDialogRef = ref(null)
const { registerDialog } = useDialog()

onMounted(() => {
  authStore.checkSession()
  if (authStore.isAuthenticated) {
    authStore.refreshPerfil().catch(() => {})
  }
  
  // Registra o dialog globalmente
  if (appDialogRef.value) {
    registerDialog(appDialogRef.value)
  }
})
</script>

<style>
/* Transições suaves entre views */
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>
