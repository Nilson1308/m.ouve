<template>
  <section class="pb-6 border-b border-gray-200 dark:border-gray-700 last:border-0 last:pb-0">
    <div class="mb-4">
      <h3 class="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
        <component :is="icon" class="w-5 h-5 text-primary-600 dark:text-primary-400" />
        {{ titulo }}
      </h3>
      <p v-if="subtitulo" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
        {{ subtitulo }}
      </p>
    </div>
    <slot />
  </section>
</template>

<script setup>
defineProps({
  titulo: { type: String, required: true },
  subtitulo: { type: String, default: '' },
  icon: { type: [Object, Function], required: true }
})
</script>