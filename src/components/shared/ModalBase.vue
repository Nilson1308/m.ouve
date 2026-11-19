<template>
  <Teleport to="body">
    <Transition name="modal">
      <div v-if="modelValue" class="fixed inset-0 z-50 flex items-center justify-center p-4 safe-area-inset">
        <!-- Backdrop -->
        <div 
          class="absolute inset-0 bg-black/50 transition-opacity"
          @click="handleBackdropClick"
        ></div>

        <!-- Modal Container -->
        <div 
          :class="[
            'relative bg-white rounded-2xl shadow-gov-lg max-w-full overflow-hidden',
            sizeClasses[size],
            'transform transition-all'
          ]"
        >
          <!-- Header -->
          <div v-if="showHeader" class="flex items-center justify-between p-6 border-b border-gov-gray-medium">
            <h3 class="text-xl font-semibold text-gov-gray-dark">
              <slot name="title">{{ title }}</slot>
            </h3>
            <button 
              v-if="closable"
              @click="close"
              class="p-2 hover:bg-gov-gray-light rounded-lg transition-colors"
            >
              <svg class="w-5 h-5 text-gov-gray-dark" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Content -->
          <div :class="['overflow-y-auto', contentClass]">
            <slot></slot>
          </div>

          <!-- Footer -->
          <div v-if="$slots.footer" class="p-6 border-t border-gov-gray-medium bg-gov-gray-light/30">
            <slot name="footer"></slot>
          </div>
        </div>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { watch } from 'vue'

const props = defineProps({
  modelValue: {
    type: Boolean,
    required: true
  },
  title: {
    type: String,
    default: ''
  },
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg', 'xl', 'full'].includes(value)
  },
  closable: {
    type: Boolean,
    default: true
  },
  closeOnBackdrop: {
    type: Boolean,
    default: true
  },
  showHeader: {
    type: Boolean,
    default: true
  },
  contentClass: {
    type: String,
    default: 'p-6'
  }
})

const emit = defineEmits(['update:modelValue', 'close'])

const sizeClasses = {
  sm: 'max-w-sm',
  md: 'max-w-md',
  lg: 'max-w-lg',
  xl: 'max-w-2xl',
  full: 'max-w-4xl'
}

function close() {
  emit('update:modelValue', false)
  emit('close')
}

function handleBackdropClick() {
  if (props.closeOnBackdrop && props.closable) {
    close()
  }
}

// Previne scroll do body quando modal está aberto
watch(() => props.modelValue, (isOpen) => {
  if (isOpen) {
    document.body.style.overflow = 'hidden'
  } else {
    document.body.style.overflow = ''
  }
})
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.modal-enter-active .relative,
.modal-leave-active .relative {
  transition: transform 0.3s ease;
}

.modal-enter-from .relative,
.modal-leave-to .relative {
  transform: scale(0.9);
}
</style>
