<template>
  <div class="card text-center py-12">
    <!-- Ícone -->
    <div class="w-20 h-20 mx-auto mb-6 rounded-full bg-gov-gray-medium/30 flex items-center justify-center">
      <slot name="icon">
        <svg class="w-10 h-10 text-gov-gray-dark/40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 13V6a2 2 0 00-2-2H6a2 2 0 00-2 2v7m16 0v5a2 2 0 01-2 2H6a2 2 0 01-2-2v-5m16 0h-2.586a1 1 0 00-.707.293l-2.414 2.414a1 1 0 01-.707.293h-3.172a1 1 0 01-.707-.293l-2.414-2.414A1 1 0 006.586 13H4" />
        </svg>
      </slot>
    </div>

    <!-- Título -->
    <h3 class="text-xl font-semibold text-gov-gray-dark mb-3">
      {{ title }}
    </h3>

    <!-- Descrição -->
    <p class="text-gov-gray-dark/70 mb-6 max-w-md mx-auto">
      {{ description }}
    </p>

    <!-- Ação -->
    <slot name="action">
      <button v-if="actionText" @click="$emit('action')" class="btn btn-primary">
        {{ actionText }}
      </button>
    </slot>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  description: {
    type: String,
    required: true
  },
  actionText: {
    type: String,
    default: ''
  }
})

defineEmits(['action'])
</script>
