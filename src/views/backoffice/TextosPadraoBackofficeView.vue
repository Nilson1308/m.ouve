<template>
  <div class="px-4 sm:px-6 lg:px-8 py-6">
    <header class="mb-6">
      <h2 class="text-xl font-bold text-slate-900 dark:text-white">Textos padrão de despacho</h2>
      <p class="text-sm text-slate-600 dark:text-slate-400 mt-1">
        Modelos reutilizáveis no formalizador setorial
      </p>
    </header>
    <GestaoTextosPadrao />
  </div>
</template>

<script setup>
import GestaoTextosPadrao from '@/components/backoffice/admin/GestaoTextosPadrao.vue'
</script>