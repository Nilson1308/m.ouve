<template>
  <div class="bg-gradient-to-r from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 border-2 border-primary-200 dark:border-primary-800 rounded-card p-6">
    <div class="flex items-start gap-4">
      <div class="p-3 bg-primary-100 dark:bg-primary-900/40 rounded-lg">
        <LinkIcon class="w-6 h-6 text-primary-600 dark:text-primary-400" />
      </div>

      <div class="flex-1">
        <h4 class="text-base font-bold text-primary-900 dark:text-primary-100 mb-2">
          🔗 Link Mágico para Equipe de Campo
        </h4>
        <p class="text-sm text-primary-800 dark:text-primary-200 mb-4">
          Copie e envie este link para a equipe de campo. Permite envio de fotos sem necessidade de login ou cadastro.
        </p>

        <div v-if="!ordem.magic_link" class="space-y-3">
          <button
            type="button"
            @click="emit('gerar-link')"
            :disabled="gerando"
            class="btn-primary w-full sm:w-auto"
          >
            <SparklesIcon v-if="!gerando" class="w-5 h-5" />
            <div v-else class="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
            {{ gerando ? 'Gerando...' : 'Gerar Link Mágico' }}
          </button>
        </div>

        <div v-else class="space-y-4">
          <div>
            <label class="block text-xs font-semibold text-primary-700 dark:text-primary-300 mb-2">
              URL do Link Mágico
            </label>
            <div class="flex items-center gap-2">
              <input
                :value="ordem.magic_link.url"
                readonly
                class="input flex-1 font-mono text-sm bg-white dark:bg-gray-800"
              />
              <button
                type="button"
                @click="copiarLink"
                class="btn-primary flex items-center gap-2 whitespace-nowrap"
              >
                <ClipboardIcon v-if="!copiado" class="w-5 h-5" />
                <CheckIcon v-else class="w-5 h-5" />
                {{ copiado ? 'Copiado!' : 'Copiar' }}
              </button>
            </div>
          </div>

          <div class="grid grid-cols-3 gap-3">
            <div class="bg-white/50 dark:bg-gray-800/50 rounded-lg p-3">
              <p class="text-xs text-gray-600 dark:text-gray-400 mb-1">Token</p>
              <p class="text-xs font-mono font-semibold text-gray-900 dark:text-white truncate">
                {{ ordem.magic_link.token }}
              </p>
            </div>
            <div class="bg-white/50 dark:bg-gray-800/50 rounded-lg p-3">
              <p class="text-xs text-gray-600 dark:text-gray-400 mb-1">Acessos</p>
              <p class="text-sm font-bold text-primary-600 dark:text-primary-400">
                {{ ordem.magic_link.acessos || 0 }}
              </p>
            </div>
            <div class="bg-white/50 dark:bg-gray-800/50 rounded-lg p-3">
              <p class="text-xs text-gray-600 dark:text-gray-400 mb-1">Validade</p>
              <p class="text-xs font-semibold text-gray-900 dark:text-white">
                {{ calcularTempoRestante(ordem.magic_link.expira_em) }}
              </p>
            </div>
          </div>

          <div class="flex items-center gap-2 text-sm flex-wrap">
            <button
              type="button"
              @click="emit('gerar-link')"
              :disabled="gerando"
              class="text-primary-600 dark:text-primary-400 hover:text-primary-700 dark:hover:text-primary-300 font-medium flex items-center gap-1"
            >
              <ArrowPathIcon :class="['w-4 h-4', gerando && 'animate-spin']" />
              Renovar Link
            </button>
            <span class="text-gray-300 dark:text-gray-600">·</span>
            <button
              type="button"
              @click="compartilharWhatsApp"
              class="text-green-600 dark:text-green-400 font-medium flex items-center gap-1"
            >
              <ChatBubbleBottomCenterTextIcon class="w-4 h-4" />
              WhatsApp
            </button>
            <span class="text-gray-300 dark:text-gray-600">·</span>
            <button
              type="button"
              @click="compartilharEmail"
              class="text-blue-600 dark:text-blue-400 font-medium flex items-center gap-1"
            >
              <EnvelopeIcon class="w-4 h-4" />
              E-mail
            </button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import {
  LinkIcon,
  SparklesIcon,
  ClipboardIcon,
  CheckIcon,
  ArrowPathIcon,
  ChatBubbleBottomCenterTextIcon,
  EnvelopeIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  ordem: {
    type: Object,
    required: true
  },
  gerando: {
    type: Boolean,
    default: false
  }
})

const emit = defineEmits(['gerar-link'])

const copiado = ref(false)

async function copiarLink() {
  if (props.ordem.magic_link?.url) {
    await navigator.clipboard.writeText(props.ordem.magic_link.url)
    copiado.value = true
    setTimeout(() => {
      copiado.value = false
    }, 2000)
  }
}

function compartilharWhatsApp() {
  if (!props.ordem.magic_link) return
  const mensagem = `🔗 Link para envio de evidências — OS ${props.ordem.protocolo_id}:\n\n${props.ordem.magic_link.url}\n\nServiço: ${props.ordem.servico}\nLocal: ${props.ordem.endereco}`
  window.open(`https://wa.me/?text=${encodeURIComponent(mensagem)}`, '_blank')
}

function compartilharEmail() {
  if (!props.ordem.magic_link) return
  const assunto = `Link evidências — ${props.ordem.protocolo_id}`
  const corpo = `Link: ${props.ordem.magic_link.url}\n\nServiço: ${props.ordem.servico}\nLocal: ${props.ordem.endereco}`
  window.location.href = `mailto:?subject=${encodeURIComponent(assunto)}&body=${encodeURIComponent(corpo)}`
}

function calcularTempoRestante(expiraEm) {
  if (!expiraEm) return '—'
  const diff = new Date(expiraEm) - new Date()
  if (diff <= 0) return 'Expirado'
  const dias = Math.floor(diff / (1000 * 60 * 60 * 24))
  const horas = Math.floor((diff % (1000 * 60 * 60 * 24)) / (1000 * 60 * 60))
  if (dias > 0) return `${dias}d ${horas}h`
  return `${horas}h`
}
</script>
