<template>
  <Teleport to="body">
    <transition name="pwa-toast">
      <div
        v-if="needRefresh && !dispensado"
        class="pwa-updater-toast"
        role="status"
        aria-live="polite"
      >
        <p class="pwa-updater-toast__text">
          Nova atualização disponível. Clique para recarregar.
        </p>
        <button
          type="button"
          class="pwa-updater-toast__action"
          @click="aplicarAtualizacao"
        >
          Atualizar
        </button>
        <button
          type="button"
          class="pwa-updater-toast__dismiss"
          aria-label="Fechar"
          @click="dispensar"
        >
          ×
        </button>
      </div>
    </transition>
  </Teleport>
</template>

<script setup>
import { ref } from 'vue'
import { useRegisterSW } from 'virtual:pwa-register/vue'

const dispensado = ref(false)

const { needRefresh, updateServiceWorker } = useRegisterSW({
  immediate: true,
  onRegisterError(error) {
    console.error('[PWA] Falha ao registrar o Service Worker:', error)
  }
})

function dispensar() {
  dispensado.value = true
}

async function aplicarAtualizacao() {
  await updateServiceWorker(true)
}
</script>

<style scoped>
.pwa-updater-toast {
  position: fixed;
  left: 50%;
  bottom: 1.25rem;
  z-index: 9999;
  display: flex;
  align-items: center;
  gap: 0.75rem;
  max-width: min(28rem, calc(100vw - 2rem));
  padding: 0.875rem 1rem;
  transform: translateX(-50%);
  border-radius: 0.75rem;
  background: #0f172a;
  color: #f8fafc;
  box-shadow:
    0 10px 25px rgb(15 23 42 / 0.35),
    0 4px 10px rgb(15 23 42 / 0.2);
}

.pwa-updater-toast__text {
  margin: 0;
  flex: 1;
  font-size: 0.875rem;
  line-height: 1.35;
}

.pwa-updater-toast__action {
  flex-shrink: 0;
  padding: 0.4rem 0.85rem;
  border: none;
  border-radius: 0.5rem;
  background: #f8fafc;
  color: #0f172a;
  font-size: 0.8125rem;
  font-weight: 600;
  cursor: pointer;
}

.pwa-updater-toast__action:hover {
  background: #e2e8f0;
}

.pwa-updater-toast__dismiss {
  flex-shrink: 0;
  padding: 0 0.25rem;
  border: none;
  background: transparent;
  color: #94a3b8;
  font-size: 1.25rem;
  line-height: 1;
  cursor: pointer;
}

.pwa-updater-toast__dismiss:hover {
  color: #e2e8f0;
}

.pwa-toast-enter-active,
.pwa-toast-leave-active {
  transition:
    opacity 0.25s ease,
    transform 0.25s ease;
}

.pwa-toast-enter-from,
.pwa-toast-leave-to {
  opacity: 0;
  transform: translateX(-50%) translateY(0.75rem);
}
</style>
