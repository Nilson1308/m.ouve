<template>
  <div class="min-h-[70vh] flex items-center justify-center px-6 py-16">
    <div
      class="max-w-lg w-full rounded-2xl border border-slate-200/80 dark:border-slate-700/80 bg-white/80 dark:bg-slate-900/60 backdrop-blur-xl shadow-2xl p-8 text-center"
    >
      <div
        class="mx-auto mb-6 w-16 h-16 rounded-2xl bg-red-500/10 border border-red-500/30 flex items-center justify-center"
      >
        <ShieldExclamationIcon class="w-9 h-9 text-red-500 dark:text-red-400" />
      </div>
      <h1 class="text-2xl font-bold text-slate-900 dark:text-white mb-2">Acesso negado</h1>
      <p class="text-sm text-slate-600 dark:text-slate-400 leading-relaxed mb-6">
        Você não possui a permissão necessária para acessar esta área
        <span v-if="codigo" class="font-mono text-xs block mt-2 text-red-600 dark:text-red-400">
          {{ codigo }}
        </span>
      </p>
      <div class="flex flex-col sm:flex-row gap-3 justify-center">
        <router-link
          to="/backoffice/mesa-trabalho"
          class="inline-flex items-center justify-center px-5 py-2.5 rounded-xl bg-primary-600 hover:bg-primary-700 text-white text-sm font-semibold transition-colors"
        >
          Ir para a Mesa de Trabalho
        </router-link>
        <button
          type="button"
          class="inline-flex items-center justify-center px-5 py-2.5 rounded-xl border border-slate-300 dark:border-slate-600 text-slate-700 dark:text-slate-200 text-sm font-medium hover:bg-slate-50 dark:hover:bg-slate-800 transition-colors"
          @click="router.back()"
        >
          Voltar
        </button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ShieldExclamationIcon } from '@heroicons/vue/24/outline'

const route = useRoute()
const router = useRouter()
const codigo = computed(() => route.query.perm || '')
</script>