<template>
  <div
    class="mt-3 ml-10 max-w-md rounded-xl border border-amber-200 dark:border-amber-700 high-contrast:border-yellow-300 bg-amber-50/90 dark:bg-amber-950/30 high-contrast:bg-gray-900 p-4 space-y-3"
    role="region"
    aria-label="Atendimento encerrado — próximos passos"
  >
    <p class="text-xs text-amber-900 dark:text-amber-100 high-contrast:text-white leading-relaxed">
      Este canal não pode seguir com o assunto informado. Você pode escolher outro serviço ou voltar ao início.
    </p>
    <div class="flex flex-col sm:flex-row gap-2">
      <button
        type="button"
        class="min-h-11 px-4 py-3 text-sm font-semibold rounded-xl bg-primary-600 hover:bg-primary-700 text-white high-contrast:bg-yellow-300 high-contrast:text-black high-contrast:hover:bg-yellow-400 transition-colors shadow-button text-center"
        @click="$emit('escolher-outro-servico')"
      >
        Escolher outro serviço
      </button>
      <button
        type="button"
        class="min-h-11 px-4 py-3 text-sm font-semibold rounded-xl border-2 border-gray-300 dark:border-gray-600 high-contrast:border-yellow-300 text-gray-800 dark:text-gray-100 high-contrast:text-yellow-300 hover:bg-gray-100 dark:hover:bg-gray-800 high-contrast:hover:bg-gray-900 transition-colors text-center"
        @click="$emit('voltar-inicio')"
      >
        Voltar ao início
      </button>
    </div>
  </div>
</template>

<script setup>
defineEmits(['escolher-outro-servico', 'voltar-inicio'])
</script>