<template>
  <section class="card">
    <!-- Header -->
    <button
      @click="expandido = !expandido"
      class="w-full flex items-center justify-between mb-4 hover:bg-gray-50 dark:hover:bg-gray-750 -m-2 p-2 rounded-lg transition-colors"
    >
      <div class="flex items-center gap-3">
        <div class="w-10 h-10 rounded-lg bg-purple-100 dark:bg-purple-900 flex items-center justify-center">
          <ChatBubbleLeftRightIcon class="w-6 h-6 text-purple-600 dark:text-purple-400" />
        </div>
        <div class="text-left">
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
            Histórico de Atendimento
          </h2>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            {{ historico.length }} mensagens · Auditoria de conversação IA
          </p>
        </div>
      </div>
      <ChevronDownIcon 
        :class="['w-5 h-5 text-gray-400 transition-transform', { 'rotate-180': expandido }]"
      />
    </button>

    <!-- Conteúdo Expansível -->
    <Transition name="expand">
      <div v-if="expandido" class="space-y-3">
        <!-- Timeline de Mensagens -->
        <div class="relative border-l-2 border-gray-200 dark:border-gray-700 ml-5 pl-6 py-2 space-y-4">
          <div
            v-for="mensagem in historico"
            :key="mensagem.id"
            class="relative"
          >
            <!-- Indicador de Timeline -->
            <div 
              :class="[
                'absolute -left-8 w-4 h-4 rounded-full border-2 border-white dark:border-gray-800',
                mensagem.tipo === 'bot' ? 'bg-primary-500' : 'bg-success-500'
              ]"
            ></div>

            <!-- Mensagem -->
            <div :class="[
              'p-3 rounded-lg',
              mensagem.tipo === 'bot'
                ? 'bg-gray-50 dark:bg-gray-750 border border-gray-200 dark:border-gray-700'
                : 'bg-primary-50 dark:bg-primary-900/20 border border-primary-200 dark:border-primary-800'
            ]">
              <!-- Cabeçalho -->
              <div class="flex items-center justify-between mb-2">
                <div class="flex items-center gap-2">
                  <component 
                    :is="mensagem.tipo === 'bot' ? CpuChipIcon : UserCircleIcon"
                    class="w-4 h-4"
                    :class="mensagem.tipo === 'bot' ? 'text-primary-600 dark:text-primary-400' : 'text-success-600 dark:text-success-400'"
                  />
                  <span class="text-xs font-semibold" :class="mensagem.tipo === 'bot' ? 'text-gray-700 dark:text-gray-300' : 'text-gray-900 dark:text-white'">
                    {{ mensagem.tipo === 'bot' ? 'Assistente IA' : 'Cidadão' }}
                  </span>
                </div>
                <span class="text-xs text-gray-500 dark:text-gray-400">
                  {{ formatarHora(mensagem.timestamp) }}
                </span>
              </div>

              <!-- Conteúdo -->
              <p class="text-sm text-gray-700 dark:text-gray-300 whitespace-pre-wrap">
                {{ mensagem.mensagem }}
              </p>

              <!-- Anexo (se houver) -->
              <div v-if="mensagem.anexo" class="mt-3 pt-3 border-t border-gray-200 dark:border-gray-600">
                <div v-if="mensagem.anexo.tipo === 'imagem'" class="relative group">
                  <img 
                    :src="mensagem.anexo.url" 
                    alt="Anexo"
                    class="w-full max-w-xs rounded-lg border border-gray-300 dark:border-gray-600 cursor-pointer hover:opacity-90 transition-opacity"
                    @click="abrirImagem(mensagem.anexo.url)"
                  />
                  <div class="absolute inset-0 flex items-center justify-center opacity-0 group-hover:opacity-100 transition-opacity">
                    <div class="bg-black/50 px-4 py-2 rounded-lg">
                      <MagnifyingGlassPlusIcon class="w-6 h-6 text-white" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Rodapé com Estatísticas -->
        <div class="pt-4 border-t border-gray-200 dark:border-gray-700 grid grid-cols-3 gap-4">
          <div class="text-center">
            <p class="text-2xl font-bold text-gray-900 dark:text-white">
              {{ estatisticas.totalMensagens }}
            </p>
            <p class="text-xs text-gray-600 dark:text-gray-400">Mensagens</p>
          </div>
          <div class="text-center">
            <p class="text-2xl font-bold text-primary-600 dark:text-primary-400">
              {{ estatisticas.mensagensBot }}
            </p>
            <p class="text-xs text-gray-600 dark:text-gray-400">IA</p>
          </div>
          <div class="text-center">
            <p class="text-2xl font-bold text-success-600 dark:text-success-400">
              {{ estatisticas.mensagensCidadao }}
            </p>
            <p class="text-xs text-gray-600 dark:text-gray-400">Cidadão</p>
          </div>
        </div>
      </div>
    </Transition>
  </section>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  ChatBubbleLeftRightIcon,
  ChevronDownIcon,
  CpuChipIcon,
  UserCircleIcon,
  MagnifyingGlassPlusIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  historico: {
    type: Array,
    required: true
  }
})

const expandido = ref(false)

const estatisticas = computed(() => ({
  totalMensagens: props.historico.length,
  mensagensBot: props.historico.filter(m => m.tipo === 'bot').length,
  mensagensCidadao: props.historico.filter(m => m.tipo === 'cidadao').length
}))

function formatarHora(timestamp) {
  const date = new Date(timestamp)
  return date.toLocaleTimeString('pt-BR', {
    hour: '2-digit',
    minute: '2-digit'
  })
}

function abrirImagem(url) {
  window.open(url, '_blank')
}
</script>

<style scoped>
/* Animação de expansão */
.expand-enter-active,
.expand-leave-active {
  transition: all 0.3s ease;
  max-height: 2000px;
  overflow: hidden;
}

.expand-enter-from,
.expand-leave-to {
  max-height: 0;
  opacity: 0;
}
</style>
