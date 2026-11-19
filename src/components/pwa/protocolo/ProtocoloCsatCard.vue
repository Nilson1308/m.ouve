<template>
  <section
    class="card border-2 border-primary-200 dark:border-primary-800 high-contrast:border-yellow-300 bg-gradient-to-br from-primary-50/80 to-white dark:from-primary-950/40 dark:to-gray-900 high-contrast:bg-black"
    :aria-labelledby="tituloSecaoId"
  >
    <!-- Modo visualização -->
    <template v-if="avaliacaoExistente">
      <div class="flex items-start gap-3 mb-4">
        <div
          class="w-12 h-12 rounded-avatar bg-success/15 dark:bg-success/25 flex items-center justify-center shrink-0"
          aria-hidden="true"
        >
          <CheckCircleIcon class="w-7 h-7 text-success high-contrast:text-yellow-300" />
        </div>
        <div class="min-w-0 flex-1">
          <h2 :id="tituloSecaoId" class="text-base font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300">
            Obrigado pela sua avaliação!
          </h2>
          <p class="text-sm text-gray-600 dark:text-gray-400 high-contrast:text-white mt-1">
            Sua opinião ajuda a melhorar o atendimento municipal.
          </p>
        </div>
      </div>

      <p class="text-sm font-semibold text-gray-800 dark:text-gray-200 high-contrast:text-white mb-2">
        Sua nota
      </p>
      <div
        class="flex items-center justify-center gap-1 py-2"
        role="img"
        :aria-label="`Avaliação registrada: ${avaliacaoExistente.nota} de 5 estrelas`"
      >
        <span
          v-for="estrela in 5"
          :key="`read-${estrela}`"
          class="inline-flex items-center justify-center w-11 h-11"
          aria-hidden="true"
        >
          <StarIconSolid
            v-if="estrela <= avaliacaoExistente.nota"
            class="w-9 h-9 text-amber-400"
          />
          <StarIconOutline
            v-else
            class="w-9 h-9 text-gray-300 dark:text-gray-600"
          />
        </span>
      </div>

      <p
        v-if="dataAvaliacaoFormatada"
        class="text-xs text-center text-gray-500 dark:text-gray-400 high-contrast:text-gray-300 mt-1"
      >
        Avaliado em
        <time :datetime="avaliacaoExistente.criadaEm || undefined">{{ dataAvaliacaoFormatada }}</time>
      </p>

      <blockquote
        v-if="avaliacaoExistente.comentario"
        class="mt-4 p-3 rounded-card bg-gray-50 dark:bg-gray-800/60 border border-gray-200 dark:border-gray-700 text-sm text-gray-700 dark:text-gray-300 high-contrast:text-white"
      >
        <p class="text-xs font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 mb-1">
          Seu comentário
        </p>
        {{ avaliacaoExistente.comentario }}
      </blockquote>
    </template>

    <!-- Modo formulário -->
    <template v-else-if="podeAvaliar">
      <div class="flex items-start gap-3 mb-4">
        <div
          class="w-12 h-12 rounded-avatar bg-primary-100 dark:bg-primary-900/40 flex items-center justify-center shrink-0"
          aria-hidden="true"
        >
          <StarIconSolid class="w-7 h-7 text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300" />
        </div>
        <div class="min-w-0 flex-1">
          <h2 :id="tituloSecaoId" class="text-base font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300">
            Avalie o atendimento
          </h2>
          <p class="text-sm text-gray-600 dark:text-gray-400 high-contrast:text-white mt-1">
            Como você avalia a resolução desta solicitação?
          </p>
        </div>
      </div>

      <div
        role="radiogroup"
        aria-required="true"
        :aria-labelledby="tituloSecaoId"
        :aria-describedby="erro ? erroAnuncioId : undefined"
        class="mb-4"
        @keydown="onRadiogroupKeydown"
      >
        <span :id="labelEstrelasId" class="sr-only">Selecione de 1 a 5 estrelas</span>
        <div class="flex items-center justify-center gap-1 py-2">
          <button
            v-for="estrela in 5"
            :key="`rate-${estrela}`"
            type="button"
            role="radio"
            :aria-checked="nota === estrela"
            :aria-label="`${estrela} de 5 estrelas`"
            :tabindex="nota === 0 ? (estrela === 1 ? 0 : -1) : nota === estrela ? 0 : -1"
            class="inline-flex items-center justify-center min-w-[44px] min-h-[44px] rounded-full transition-transform motion-reduce:transition-none hover:scale-105 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500 high-contrast:focus-visible:ring-yellow-300 disabled:opacity-50"
            :disabled="enviando"
            @click="selecionarNota(estrela)"
          >
            <StarIconSolid
              v-if="estrela <= nota"
              class="w-9 h-9 text-amber-400"
              aria-hidden="true"
            />
            <StarIconOutline
              v-else
              class="w-9 h-9 text-gray-300 dark:text-gray-600 high-contrast:text-gray-500"
              aria-hidden="true"
            />
          </button>
        </div>
        <p
          v-if="nota > 0"
          class="text-center text-sm font-medium text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300"
          aria-live="polite"
        >
          {{ rotuloNota(nota) }}
        </p>
      </div>

      <div class="mb-4">
        <label :for="comentarioId" class="block text-sm font-semibold text-gray-800 dark:text-gray-200 high-contrast:text-white mb-2">
          Comentário (opcional)
        </label>
        <textarea
          :id="comentarioId"
          v-model="comentario"
          rows="3"
          maxlength="500"
          class="input resize-none w-full"
          placeholder="Conte como foi sua experiência..."
          :disabled="enviando"
          :aria-describedby="contadorId"
        />
        <p :id="contadorId" class="text-xs text-gray-500 dark:text-gray-400 mt-1 text-right">
          {{ comentario.length }}/500
        </p>
      </div>

      <p :id="erroAnuncioId" v-if="erro" class="text-sm text-red-600 dark:text-red-400 mb-3" role="alert">
        {{ erro }}
      </p>

      <button
        type="button"
        class="btn-primary w-full min-h-[44px] disabled:opacity-50 disabled:cursor-not-allowed"
        :disabled="nota === 0 || enviando"
        @click="submeter"
      >
        <span
          v-if="enviando"
          class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin motion-reduce:animate-none mr-2 align-middle"
          aria-hidden="true"
        />
        {{ enviando ? 'Enviando...' : 'Enviar avaliação' }}
      </button>

      <div class="sr-only" aria-live="polite" aria-atomic="true">{{ anuncioLive }}</div>
    </template>
  </section>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { StarIcon as StarIconOutline } from '@heroicons/vue/24/outline'
import { StarIcon as StarIconSolid, CheckCircleIcon } from '@heroicons/vue/24/solid'
import { protocolosService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'

const props = defineProps({
  protocoloId: {
    type: String,
    required: true
  },
  podeAvaliar: {
    type: Boolean,
    default: false
  },
  avaliacao: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['avaliado'])

const uid = Math.random().toString(36).slice(2, 9)
const tituloSecaoId = `csat-titulo-${uid}`
const comentarioId = `csat-comentario-${uid}`
const contadorId = `csat-contador-${uid}`
const erroAnuncioId = `csat-erro-${uid}`
const labelEstrelasId = `csat-label-estrelas-${uid}`

const nota = ref(0)
const comentario = ref('')
const enviando = ref(false)
const erro = ref('')
const anuncioLive = ref('')
const avaliacaoLocal = ref(props.avaliacao)

watch(
  () => props.avaliacao,
  (v) => {
    avaliacaoLocal.value = v
  }
)

const avaliacaoExistente = computed(() => {
  if (!avaliacaoLocal.value) return null
  const criadaEm = avaliacaoLocal.value.criadaEm ?? avaliacaoLocal.value.criada_em
  return {
    nota: Number(avaliacaoLocal.value.nota) || 0,
    comentario: (avaliacaoLocal.value.comentario || '').trim(),
    criadaEm: criadaEm || null
  }
})

const dataAvaliacaoFormatada = computed(() => {
  if (!avaliacaoExistente.value?.criadaEm) return ''
  const data = new Date(avaliacaoExistente.value.criadaEm)
  if (Number.isNaN(data.getTime())) return ''
  return data.toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
})

function rotuloNota(n) {
  const labels = {
    1: 'Muito insatisfeito',
    2: 'Insatisfeito',
    3: 'Neutro',
    4: 'Satisfeito',
    5: 'Muito satisfeito'
  }
  return labels[n] || ''
}

function selecionarNota(estrela) {
  nota.value = estrela
  erro.value = ''
}

function onRadiogroupKeydown(event) {
  const alvo = event.target
  if (!alvo?.getAttribute || alvo.getAttribute('role') !== 'radio') return
  let proxima = nota.value || 1
  if (event.key === 'ArrowRight' || event.key === 'ArrowUp') {
    event.preventDefault()
    proxima = Math.min(5, (nota.value || 0) + 1 || 1)
  } else if (event.key === 'ArrowLeft' || event.key === 'ArrowDown') {
    event.preventDefault()
    proxima = Math.max(1, (nota.value || 2) - 1)
  } else {
    return
  }
  selecionarNota(proxima)
  const botoes = event.currentTarget?.querySelectorAll?.('[role="radio"]')
  botoes?.[proxima - 1]?.focus?.()
}

async function submeter() {
  if (nota.value < 1 || nota.value > 5 || enviando.value) return
  enviando.value = true
  erro.value = ''
  anuncioLive.value = ''

  try {
    const resposta = await protocolosService.avaliar(props.protocoloId, {
      nota: nota.value,
      comentario: comentario.value.trim()
    })
    avaliacaoLocal.value = {
      nota: resposta.nota,
      comentario: resposta.comentario || '',
      criadaEm: resposta.criada_em ?? resposta.criadaEm ?? new Date().toISOString()
    }
    anuncioLive.value = 'Avaliação enviada com sucesso. Obrigado!'
    emit('avaliado', avaliacaoLocal.value)
  } catch (err) {
    erro.value = getApiErrorMessage(err, 'Não foi possível enviar sua avaliação. Tente novamente.')
    anuncioLive.value = erro.value
  } finally {
    enviando.value = false
  }
}
</script>