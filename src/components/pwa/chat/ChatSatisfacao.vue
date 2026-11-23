<template>
  <div class="card bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/10 high-contrast:bg-transparent border-2 border-blue-300 dark:border-blue-700 high-contrast:border-yellow-300 p-5 max-w-lg animate-scale-in">
    <!-- Header -->
    <div class="flex items-start gap-3 mb-4">
      <div class="flex-shrink-0 w-12 h-12 bg-gradient-to-br from-blue-500 to-blue-600 high-contrast:from-yellow-300 high-contrast:to-yellow-400 rounded-avatar flex items-center justify-center shadow-button">
        <ChatBubbleBottomCenterTextIcon class="w-6 h-6 text-white high-contrast:text-black" />
      </div>
      <div class="flex-1">
        <h3 class="text-base font-bold text-blue-900 dark:text-blue-100 high-contrast:text-yellow-300 mb-1">
          Avalie como foi abrir sua solicitação
        </h3>
        <p class="text-sm text-blue-800 dark:text-blue-200 high-contrast:text-white high-contrast:font-bold">
          Sua opinião sobre o registro no aplicativo (não é a avaliação final do atendimento).
        </p>
      </div>
    </div>

    <!-- Avaliação por Estrelas -->
    <div class="mb-5">
      <label class="block text-sm font-bold text-blue-900 dark:text-blue-100 high-contrast:text-yellow-300 mb-3">
        Como foi o processo de abertura?
      </label>
      <div class="flex items-center justify-center gap-3 py-3">
        <button
          v-for="estrela in 5"
          :key="estrela"
          @click="nota = estrela"
          @mouseenter="hoverNota = estrela"
          @mouseleave="hoverNota = 0"
          class="transition-all duration-200 hover:scale-110 focus:outline-none focus:ring-2 focus:ring-yellow-400 rounded-full p-1"
          :disabled="props.enviando"
        >
          <StarIcon
            :class="[
              'w-10 h-10 sm:w-12 sm:h-12 transition-colors',
              (hoverNota >= estrela || nota >= estrela)
                ? 'text-yellow-400 fill-yellow-400'
                : 'text-gray-300 dark:text-gray-600 high-contrast:text-gray-500'
            ]"
          />
        </button>
      </div>
      
      <!-- Labels de Satisfação -->
      <div class="text-center">
        <p v-if="nota > 0" class="text-sm font-semibold transition-opacity" :class="getLabelSatisfacaoClass(nota)">
          {{ getLabelSatisfacao(nota) }}
        </p>
      </div>
    </div>

    <!-- Comentário Opcional -->
    <div class="mb-5">
      <label class="block text-sm font-bold text-blue-900 dark:text-blue-100 high-contrast:text-yellow-300 mb-2">
        Conte-nos mais (opcional)
      </label>
      <textarea
        v-model="comentario"
        rows="3"
        class="input resize-none"
        placeholder="O que podemos melhorar? Ou o que fez bem?"
        :disabled="props.enviando"
      ></textarea>
    </div>

    <!-- Info Box -->
    <div class="flex items-start gap-2 p-3 bg-blue-100/50 dark:bg-blue-800/20 high-contrast:bg-transparent border border-blue-200 dark:border-blue-700 high-contrast:border-yellow-300 rounded-card mb-4">
      <InformationCircleIcon class="w-5 h-5 text-blue-600 dark:text-blue-400 high-contrast:text-yellow-300 flex-shrink-0 mt-0.5" />
      <p class="text-xs text-blue-800 dark:text-blue-200 high-contrast:text-white high-contrast:font-bold leading-relaxed">
        Sua avaliação é anônima e será usada apenas para melhorar nossos serviços.
      </p>
    </div>

    <!-- Ações -->
    <div class="flex gap-3">
      <button
        @click="$emit('cancelar')"
        class="btn-secondary flex-1"
        :disabled="props.enviando"
      >
        Pular
      </button>
      <button
        @click="enviarAvaliacao"
        :disabled="nota === 0 || props.enviando"
        class="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <span v-if="props.enviando" class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span>
        <PaperAirplaneIcon v-else class="w-4 h-4 inline-block mr-1" />
        {{ props.enviando ? 'Enviando...' : 'Enviar Avaliação' }}
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  StarIcon,
  ChatBubbleBottomCenterTextIcon,
  InformationCircleIcon,
  PaperAirplaneIcon
} from '@heroicons/vue/24/solid'

const props = defineProps({
  enviando: { type: Boolean, default: false }
})

const emit = defineEmits(['enviar', 'cancelar'])

const nota = ref(0)
const hoverNota = ref(0)
const comentario = ref('')

function getLabelSatisfacao(nota) {
  const labels = {
    1: '😞 Muito Insatisfeito',
    2: '😕 Insatisfeito',
    3: '😐 Neutro',
    4: '😊 Satisfeito',
    5: '😍 Muito Satisfeito'
  }
  return labels[nota] || ''
}

function getLabelSatisfacaoClass(nota) {
  if (nota <= 2) return 'text-red-600 dark:text-red-400 high-contrast:text-red-300'
  if (nota === 3) return 'text-amber-600 dark:text-amber-400 high-contrast:text-yellow-300'
  return 'text-green-600 dark:text-green-400 high-contrast:text-green-300'
}

function enviarAvaliacao() {
  if (nota.value === 0 || props.enviando) return
  emit('enviar', {
    nota: nota.value,
    comentario: comentario.value.trim() || null
  })
}
</script>
