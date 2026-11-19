<template>
  <div :class="['flex items-center justify-center', containerClass]">
    <div :class="[
      'animate-spin rounded-full border-4 border-t-transparent',
      sizeClasses[size],
      colorClass
    ]"></div>
    <p v-if="text" :class="['ml-3', textSizeClasses[size], 'text-gov-gray-dark']">
      {{ text }}
    </p>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  size: {
    type: String,
    default: 'md',
    validator: (value) => ['sm', 'md', 'lg', 'xl'].includes(value)
  },
  color: {
    type: String,
    default: 'primary'
  },
  text: {
    type: String,
    default: ''
  },
  containerClass: {
    type: String,
    default: ''
  }
})

const sizeClasses = {
  sm: 'h-4 w-4',
  md: 'h-8 w-8',
  lg: 'h-12 w-12',
  xl: 'h-16 w-16'
}

const textSizeClasses = {
  sm: 'text-xs',
  md: 'text-sm',
  lg: 'text-base',
  xl: 'text-lg'
}

const colorClass = computed(() => {
  const colors = {
    primary: 'border-gov-blue-warm',
    success: 'border-gov-green-cool',
    white: 'border-white'
  }
  return colors[props.color] || colors.primary
})
</script>
