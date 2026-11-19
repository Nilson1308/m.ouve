<template>
  <CardSecao
    titulo="Elegibilidade do serviço (vários campos)"
    subtitulo="Condições que cruzam idade, motivo, espécie e demais respostas — avaliadas sobre o protocolo completo"
    :icon="ShieldExclamationIcon"
  >
    <p class="text-xs text-gray-600 dark:text-gray-400 mb-4">
      Use quando a regra depende de mais de uma pergunta. As regras por passo (no roteiro abaixo) continuam
      válidas para bloqueio imediato em um único campo.
    </p>

    <div v-if="!modelValue.length" class="rounded-lg border border-dashed border-gray-300 dark:border-gray-600 p-6 text-center">
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-3">Nenhuma regra de protocolo ainda.</p>
      <button type="button" class="btn-primary !py-2 !px-4 text-sm" @click="adicionar">
        Adicionar regra
      </button>
    </div>

    <div v-else class="space-y-4">
      <div
        v-for="(regra, index) in modelValue"
        :key="regra._id"
        class="rounded-xl border border-amber-200 dark:border-amber-800 bg-amber-50/50 dark:bg-amber-950/20 p-4 space-y-3"
      >
        <div class="flex items-center justify-between gap-2">
          <span class="text-sm font-semibold text-gray-900 dark:text-white">
            Regra {{ index + 1 }}
          </span>
          <button
            type="button"
            class="text-xs text-red-600 hover:text-red-700 dark:text-red-400"
            @click="remover(index)"
          >
            Remover
          </button>
        </div>

        <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400">
          Bloquear o atendimento quando…
        </label>
        <textarea
          :value="regra.condicao"
          rows="3"
          class="input text-sm min-h-[80px]"
          placeholder="Ex.: o animal tiver menos de 12 meses E o cidadão indicar que está doente."
          @input="patch(index, { condicao: $event.target.value })"
        />

        <div class="flex flex-wrap gap-2">
          <button
            type="button"
            class="text-[11px] px-2 py-1 rounded-md bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:border-primary-400"
            @click="aplicarModelo(index, 'idade_doenca')"
          >
            Modelo: idade + doença
          </button>
          <button
            type="button"
            class="text-[11px] px-2 py-1 rounded-md bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:border-primary-400"
            @click="aplicarModelo(index, 'fora_perfil')"
          >
            Modelo: fora do perfil do serviço
          </button>
        </div>

        <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400">
          Mensagem para o cidadão
        </label>
        <textarea
          :value="regra.mensagem"
          rows="3"
          class="input text-sm min-h-[72px]"
          placeholder="Orientação humanizada quando o protocolo não puder seguir neste canal…"
          @input="patch(index, { mensagem: $event.target.value })"
        />
      </div>

      <button
        type="button"
        class="w-full py-2 text-sm font-medium text-primary-700 dark:text-primary-300 border border-primary-200 dark:border-primary-800 rounded-lg hover:bg-primary-50 dark:hover:bg-primary-950/30"
        @click="adicionar"
      >
        + Outra regra de protocolo
      </button>
    </div>
  </CardSecao>
</template>

<script setup>
import CardSecao from './FormBuilderCardSecao.vue'
import { ShieldExclamationIcon } from '@heroicons/vue/24/outline'
import { novoRegraProtocoloUi } from '@/utils/catalogoMappers'

const props = defineProps({
  modelValue: { type: Array, default: () => [] }
})

const emit = defineEmits(['update:modelValue'])

const MODELOS = {
  idade_doenca:
    'Bloquear se, considerando idade e estado de saúde informados, o animal for filhote com menos de 12 meses OU tiver mais de 9 anos E estiver doente, com sintomas ou necessidade de atendimento veterinário urgente.',
  fora_perfil:
    'Bloquear se o conjunto das respostas indicar que a demanda não é deste serviço (ex.: emergência que exige SAMU/180, crime, ou outro órgão), mesmo que cada resposta isolada pareça aceitável.'
}

function emitir(lista) {
  emit('update:modelValue', lista)
}

function patch(index, partial) {
  const copia = props.modelValue.map((item, i) => (i === index ? { ...item, ...partial } : item))
  emitir(copia)
}

function adicionar() {
  emitir([...props.modelValue, novoRegraProtocoloUi()])
}

function remover(index) {
  emitir(props.modelValue.filter((_, i) => i !== index))
}

function aplicarModelo(index, chave) {
  const texto = MODELOS[chave]
  if (!texto) return
  patch(index, { condicao: texto, ativa: true })
}
</script>