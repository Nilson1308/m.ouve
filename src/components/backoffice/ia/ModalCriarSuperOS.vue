<template>
  <!-- Backdrop -->
  <Transition
    enter-active-class="transition-opacity duration-300"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-300"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      class="fixed inset-0 bg-black/50 backdrop-blur-sm z-[2000] flex items-center justify-center p-4"
      @click.self="$emit('fechar')"
    >
      <!-- Modal -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-2xl overflow-hidden">
          <!-- Header com Gradiente -->
          <div class="relative bg-gradient-to-r from-primary-600 via-purple-600 to-pink-600 p-6">
            <div class="absolute inset-0 bg-gradient-to-r from-primary-400 via-purple-400 to-pink-400 opacity-30 animate-pulse"></div>
            
            <div class="relative flex items-start justify-between">
              <div>
                <h2 class="text-2xl font-bold text-white mb-2 flex items-center gap-3">
                  <SparklesIcon class="w-8 h-8" />
                  Criar Super OS Manual
                </h2>
                <p class="text-primary-100">
                  Agrupe {{ protocolos.length }} protocolos selecionados
                </p>
              </div>

              <button
                @click="$emit('fechar')"
                class="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <XMarkIcon class="w-6 h-6 text-white" />
              </button>
            </div>
          </div>

          <!-- Conteúdo -->
          <div class="p-6 space-y-6">
            <!-- Título da Super OS -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Título da Super OS *
              </label>
              <input
                v-model="formulario.titulo"
                type="text"
                placeholder="Ex: Tapa-buracos na região central"
                class="input"
                @keyup.enter="confirmar"
              />
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                Descreva brevemente o que será executado
              </p>
            </div>

            <!-- Lista de Protocolos Selecionados -->
            <div>
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-3">
                Protocolos que serão agrupados ({{ protocolos.length }})
              </label>
              
              <div class="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4 max-h-64 overflow-y-auto space-y-2">
                <div
                  v-for="protocolo in protocolos"
                  :key="protocolo.id"
                  class="flex items-start gap-3 p-3 bg-white dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-600"
                >
                  <!-- Foto do Protocolo -->
                  <div class="w-16 h-16 rounded-lg overflow-hidden flex-shrink-0 bg-gray-100 dark:bg-gray-700">
                    <img
                      v-if="protocolo.foto_url"
                      :src="protocolo.foto_url"
                      :alt="protocolo.codigo"
                      class="w-full h-full object-cover"
                    />
                    <div v-else class="w-full h-full flex items-center justify-center">
                      <PhotoIcon class="w-8 h-8 text-gray-400" />
                    </div>
                  </div>

                  <!-- Info do Protocolo -->
                  <div class="flex-1 min-w-0">
                    <div class="flex items-start justify-between gap-2 mb-1">
                      <p class="text-sm font-semibold text-gray-900 dark:text-white">
                        {{ protocolo.codigo }}
                      </p>
                      <span
                        :class="[
                          'px-2 py-0.5 rounded-full text-xs font-semibold',
                          protocolo.urgencia === 'urgente'
                            ? 'bg-red-100 text-red-800 dark:bg-red-900/30 dark:text-red-300'
                            : protocolo.urgencia === 'alta'
                            ? 'bg-orange-100 text-orange-800 dark:bg-orange-900/30 dark:text-orange-300'
                            : 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                        ]"
                      >
                        {{ protocolo.urgencia?.toUpperCase() }}
                      </span>
                    </div>
                    <p class="text-xs text-gray-600 dark:text-gray-400 mb-1">
                      {{ protocolo.servico }}
                    </p>
                    <p class="text-xs text-gray-500 dark:text-gray-500 flex items-center gap-1">
                      <MapPinIcon class="w-3 h-3" />
                      {{ protocolo.endereco }}
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Informações da Super OS -->
            <div class="bg-gradient-to-r from-blue-50 to-purple-50 dark:from-blue-900/20 dark:to-purple-900/20 rounded-lg p-4 border border-blue-200 dark:border-blue-800">
              <div class="flex items-start gap-3">
                <div class="p-2 bg-blue-100 dark:bg-blue-900/40 rounded-lg">
                  <InformationCircleIcon class="w-5 h-5 text-blue-600 dark:text-blue-400" />
                </div>
                <div class="flex-1">
                  <h4 class="text-sm font-semibold text-blue-900 dark:text-blue-100 mb-2">
                    O que acontecerá:
                  </h4>
                  <ul class="text-sm text-blue-800 dark:text-blue-200 space-y-1">
                    <li class="flex items-start gap-2">
                      <CheckCircleIcon class="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <span>Os {{ protocolos.length }} protocolos serão agrupados em uma única Ordem de Serviço</span>
                    </li>
                    <li class="flex items-start gap-2">
                      <CheckCircleIcon class="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <span>Uma equipe poderá resolver todos de uma vez</span>
                    </li>
                    <li class="flex items-start gap-2">
                      <CheckCircleIcon class="w-4 h-4 mt-0.5 flex-shrink-0" />
                      <span>Economia de tempo e recursos operacionais</span>
                    </li>
                  </ul>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer -->
          <div class="p-6 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-600 flex items-center justify-between">
            <p class="text-sm text-gray-600 dark:text-gray-400">
              {{ protocolos.length }} protocolo(s) selecionado(s)
            </p>

            <div class="flex items-center gap-3">
              <button
                @click="$emit('fechar')"
                class="px-4 py-2 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-200 rounded-lg font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                @click="confirmar"
                :disabled="!formularioValido || criando"
                class="px-6 py-2 bg-gradient-to-r from-primary-600 to-purple-600 hover:from-primary-700 hover:to-purple-700 text-white rounded-lg font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2 shadow-lg shadow-primary-500/50"
              >
                <div v-if="criando" class="w-5 h-5 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <SparklesIcon v-else class="w-5 h-5" />
                {{ criando ? 'Criando...' : 'Criar Super OS' }}
              </button>
            </div>
          </div>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  SparklesIcon,
  XMarkIcon,
  PhotoIcon,
  MapPinIcon,
  InformationCircleIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  protocolos: {
    type: Array,
    required: true
  }
})

const emit = defineEmits(['fechar', 'confirmar'])

// Estado
const formulario = ref({
  titulo: ''
})
const criando = ref(false)

// Computeds
const formularioValido = computed(() => {
  return formulario.value.titulo.trim().length >= 5
})

// Funções
async function confirmar() {
  if (!formularioValido.value) return

  criando.value = true

  try {
    emit('confirmar', {
      titulo: formulario.value.titulo.trim(),
      protocolos: props.protocolos
    })
  } finally {
    criando.value = false
  }
}
</script>
