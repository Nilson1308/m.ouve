<template>
  <div class="card bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/10 high-contrast:bg-transparent border-2 border-blue-300 dark:border-blue-700 high-contrast:border-yellow-300 p-5 space-y-4 max-w-lg animate-scale-in">
    <div class="flex items-start gap-3 pb-3 border-b border-blue-200 dark:border-blue-700 high-contrast:border-yellow-300">
      <div class="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-primary-500 to-primary-600 high-contrast:from-yellow-300 high-contrast:to-yellow-400 rounded-avatar flex items-center justify-center shadow-button">
        <DocumentCheckIcon class="w-6 h-6 text-white high-contrast:text-black" />
      </div>
      <div class="flex-1">
        <h3 class="text-base font-bold text-blue-900 dark:text-blue-100 high-contrast:text-yellow-300 mb-1">
          Revisão da Solicitação
        </h3>
        <p class="text-xs text-blue-700 dark:text-blue-300 high-contrast:text-white high-contrast:font-bold">
          Confira o resumo antes de gerar o protocolo
        </p>
      </div>
    </div>

    <div class="space-y-3">
      <div
        v-if="resumo.servico_nome"
        class="bg-white/60 dark:bg-gray-800/40 high-contrast:bg-gray-900 rounded-card p-3"
      >
        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-1">
          Serviço
        </label>
        <div class="flex items-center gap-2">
          <TagIcon class="w-4 h-4 text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300 flex-shrink-0" />
          <span class="text-sm font-semibold text-gray-900 dark:text-white high-contrast:text-white">
            {{ resumo.servico_nome }}
          </span>
          <span
            v-if="resumo.categoria"
            class="text-xs text-gray-600 dark:text-gray-400 high-contrast:text-gray-300"
          >
            · {{ resumo.categoria }}
          </span>
        </div>
      </div>

      <div
        v-if="resumo.descricao_inicial"
        class="bg-white/60 dark:bg-gray-800/40 high-contrast:bg-gray-900 rounded-card p-3"
      >
        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-1">
          O que você relatou
        </label>
        <p class="text-sm text-gray-900 dark:text-white high-contrast:text-white high-contrast:font-bold leading-relaxed">
          {{ resumo.descricao_inicial }}
        </p>
      </div>

      <div
        v-for="campo in resumo.campos || []"
        :key="campo.chave"
        class="bg-white/60 dark:bg-gray-800/40 high-contrast:bg-gray-900 rounded-card p-3"
      >
        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-1">
          {{ campo.rotulo }}
        </label>
        <p class="text-sm text-gray-900 dark:text-white high-contrast:text-white high-contrast:font-bold">
          {{ campo.valor }}
        </p>
      </div>

      <div
        v-if="resumo.localizacao"
        class="bg-white/60 dark:bg-gray-800/40 high-contrast:bg-gray-900 rounded-card p-3"
      >
        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-1">
          Localização
        </label>
        <div class="flex items-start gap-2">
          <MapPinIcon class="w-4 h-4 text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300 flex-shrink-0 mt-0.5" />
          <div class="flex-1">
            <p class="text-sm text-gray-900 dark:text-white high-contrast:text-white high-contrast:font-bold">
              {{ resumo.localizacao.endereco }}
            </p>
          </div>
        </div>
      </div>

      <div
        v-if="resumo.fotos && resumo.fotos.length > 0"
        class="bg-white/60 dark:bg-gray-800/40 high-contrast:bg-gray-900 rounded-card p-3"
      >
        <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-2">
          Fotos anexadas ({{ resumo.fotos.length }})
        </label>
        <ChatPhotoPreview
          :fotos="resumo.fotos"
          :editavel="false"
          :mostrarContador="false"
        />
      </div>
      <div
        v-else-if="resumo.total_anexos > 0"
        class="bg-white/60 dark:bg-gray-800/40 high-contrast:bg-gray-900 rounded-card p-3 text-sm text-gray-800 dark:text-gray-200"
      >
        {{ resumo.total_anexos }} anexo(s) na solicitação
      </div>
    </div>

    <div class="flex items-start gap-2 p-3 bg-blue-100/50 dark:bg-blue-800/20 high-contrast:bg-transparent border border-blue-200 dark:border-blue-700 high-contrast:border-yellow-300 rounded-card">
      <InformationCircleIcon class="w-5 h-5 text-blue-600 dark:text-blue-400 high-contrast:text-yellow-300 flex-shrink-0 mt-0.5" />
      <p class="text-xs text-blue-800 dark:text-blue-200 high-contrast:text-white high-contrast:font-bold leading-relaxed">
        Ao confirmar, um protocolo será gerado e você receberá o código de acompanhamento.
      </p>
    </div>

    <div class="flex gap-2 pt-2">
      <button type="button" @click="$emit('editar')" class="btn-secondary flex-1" :disabled="confirmando">
        <PencilIcon class="w-4 h-4 inline-block mr-1" />
        Editar
      </button>
      <button
        type="button"
        @click="$emit('confirmar')"
        :disabled="confirmando"
        class="btn-primary flex-1 text-base font-bold disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span
          v-if="confirmando"
          class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"
        ></span>
        <CheckCircleIcon v-else class="w-5 h-5 inline-block mr-1" />
        {{ confirmando ? 'Gerando...' : 'Confirmar e Gerar Protocolo' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import ChatPhotoPreview from './ChatPhotoPreview.vue'
import {
  DocumentCheckIcon,
  TagIcon,
  MapPinIcon,
  InformationCircleIcon,
  PencilIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'

defineProps({
  resumo: {
    type: Object,
    default: () => ({})
  },
  confirmando: {
    type: Boolean,
    default: false
  }
})

defineEmits(['confirmar', 'editar'])
</script>
