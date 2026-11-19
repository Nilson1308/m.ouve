<template>
  <dialog
    ref="dialogRef"
    class="backdrop:bg-black backdrop:bg-opacity-50 rounded-2xl shadow-2xl p-0 max-w-md w-full border-0"
    :class="{
      'dark:bg-gray-800': true,
      'high-contrast:bg-black high-contrast:border-4 high-contrast:border-yellow-300': true
    }"
    @click="handleBackdropClick"
    @cancel.prevent="handleCancel"
  >
    <div class="p-6">
      <!-- Header com ícone -->
      <div class="flex items-start gap-4 mb-4">
        <!-- Ícone baseado no tipo -->
        <div
          :class="[
            'flex-shrink-0 w-12 h-12 rounded-full flex items-center justify-center',
            iconBgClass
          ]"
        >
          <component
            :is="iconComponent"
            :class="['w-6 h-6', iconColorClass]"
          />
        </div>

        <!-- Título e Mensagem -->
        <div class="flex-1 min-w-0">
          <h3
            :class="[
              'text-lg font-semibold mb-2',
              'dark:text-gray-100',
              'high-contrast:text-yellow-300 high-contrast:font-bold'
            ]"
          >
            {{ currentDialog.title }}
          </h3>
          <p
            :class="[
              'text-sm text-gray-600',
              'dark:text-gray-300',
              'high-contrast:text-white high-contrast:font-bold'
            ]"
          >
            {{ currentDialog.message }}
          </p>
        </div>

        <!-- Botão de fechar (apenas para info/success/error) -->
        <button
          v-if="currentDialog.type !== 'confirm'"
          @click="close"
          :class="[
            'flex-shrink-0 p-1 rounded-lg hover:bg-gray-100 transition-colors',
            'dark:hover:bg-gray-700',
            'high-contrast:border-2 high-contrast:border-yellow-300'
          ]"
          aria-label="Fechar"
        >
          <XMarkIcon class="w-5 h-5 text-gray-500 dark:text-gray-400 high-contrast:text-yellow-300" />
        </button>
      </div>

      <!-- Botões de ação -->
      <div class="flex gap-3 mt-6">
        <!-- Botão de cancelar (apenas para confirm) -->
        <button
          v-if="currentDialog.type === 'confirm'"
          @click="handleCancel"
          class="flex-1 btn-secondary"
        >
          {{ currentDialog.cancelText || 'Cancelar' }}
        </button>

        <!-- Botão principal -->
        <button
          @click="handleConfirm"
          :class="[
            'flex-1',
            confirmButtonClass
          ]"
        >
          {{ currentDialog.confirmText || 'OK' }}
        </button>
      </div>
    </div>
  </dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  CheckCircleIcon,
  ExclamationTriangleIcon,
  XCircleIcon,
  InformationCircleIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'

const dialogRef = ref(null)

const currentDialog = ref({
  type: 'info', // 'info', 'success', 'error', 'confirm'
  title: '',
  message: '',
  confirmText: 'OK',
  cancelText: 'Cancelar',
  onConfirm: null,
  onCancel: null
})

// Computeds para estilização baseada no tipo
const iconComponent = computed(() => {
  const icons = {
    success: CheckCircleIcon,
    error: XCircleIcon,
    warning: ExclamationTriangleIcon,
    confirm: ExclamationTriangleIcon,
    info: InformationCircleIcon
  }
  return icons[currentDialog.value.type] || InformationCircleIcon
})

const iconBgClass = computed(() => {
  const classes = {
    success: 'bg-green-100 dark:bg-green-900/30 high-contrast:bg-black high-contrast:border-4 high-contrast:border-yellow-300',
    error: 'bg-red-100 dark:bg-red-900/30 high-contrast:bg-black high-contrast:border-4 high-contrast:border-red-600',
    warning: 'bg-amber-100 dark:bg-amber-900/30 high-contrast:bg-black high-contrast:border-4 high-contrast:border-yellow-300',
    confirm: 'bg-blue-100 dark:bg-blue-900/30 high-contrast:bg-black high-contrast:border-4 high-contrast:border-yellow-300',
    info: 'bg-blue-100 dark:bg-blue-900/30 high-contrast:bg-black high-contrast:border-4 high-contrast:border-yellow-300'
  }
  return classes[currentDialog.value.type] || classes.info
})

const iconColorClass = computed(() => {
  const classes = {
    success: 'text-green-600 dark:text-green-400 high-contrast:text-yellow-300',
    error: 'text-red-600 dark:text-red-400 high-contrast:text-white',
    warning: 'text-amber-600 dark:text-amber-400 high-contrast:text-yellow-300',
    confirm: 'text-blue-600 dark:text-blue-400 high-contrast:text-yellow-300',
    info: 'text-blue-600 dark:text-blue-400 high-contrast:text-yellow-300'
  }
  return classes[currentDialog.value.type] || classes.info
})

const confirmButtonClass = computed(() => {
  const classes = {
    success: 'btn-success',
    error: 'btn-danger',
    warning: 'btn-warning',
    confirm: 'btn-primary',
    info: 'btn-primary'
  }
  return classes[currentDialog.value.type] || 'btn-primary'
})

// Métodos públicos (expostos para o composable)
function show(options) {
  currentDialog.value = {
    type: options.type || 'info',
    title: options.title || getTitleByType(options.type),
    message: options.message || '',
    confirmText: options.confirmText || 'OK',
    cancelText: options.cancelText || 'Cancelar',
    onConfirm: options.onConfirm || null,
    onCancel: options.onCancel || null
  }

  if (dialogRef.value) {
    dialogRef.value.showModal()
  }
}

function close() {
  if (dialogRef.value) {
    dialogRef.value.close()
  }
}

function handleConfirm() {
  if (currentDialog.value.onConfirm) {
    currentDialog.value.onConfirm()
  }
  close()
}

function handleCancel() {
  if (currentDialog.value.onCancel) {
    currentDialog.value.onCancel()
  }
  close()
}

function handleBackdropClick(event) {
  // Fechar apenas se clicar no backdrop (fora do dialog)
  const rect = dialogRef.value.getBoundingClientRect()
  const isInDialog = (
    event.clientX >= rect.left &&
    event.clientX <= rect.right &&
    event.clientY >= rect.top &&
    event.clientY <= rect.bottom
  )
  
  if (!isInDialog && currentDialog.value.type !== 'confirm') {
    close()
  }
}

function getTitleByType(type) {
  const titles = {
    success: 'Sucesso',
    error: 'Erro',
    warning: 'Atenção',
    confirm: 'Confirmação',
    info: 'Informação'
  }
  return titles[type] || 'Informação'
}

// Expor métodos para o componente pai
defineExpose({
  show,
  close
})
</script>

<style scoped>
dialog::backdrop {
  background-color: rgba(0, 0, 0, 0.5);
  backdrop-filter: blur(4px);
}

/* High contrast backdrop */
.high-contrast dialog::backdrop {
  background-color: rgba(0, 0, 0, 0.9);
}
</style>
