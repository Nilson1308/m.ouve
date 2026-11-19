<template>
  <div class="h-full flex flex-col bg-gradient-to-br from-slate-50 to-blue-50 dark:from-gray-900 dark:to-blue-950">
    <!-- Header do Widget -->
    <div class="p-6 border-b border-gray-200 dark:border-gray-700 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
      <div class="flex items-start gap-3">
        <!-- Ícone IA com Gradiente -->
        <div class="relative">
          <div class="absolute inset-0 bg-gradient-to-br from-primary-500 to-purple-600 rounded-xl blur-sm opacity-75 animate-pulse"></div>
          <div class="relative p-3 bg-gradient-to-br from-primary-500 to-purple-600 rounded-xl">
            <SparklesIcon class="w-6 h-6 text-white" />
          </div>
        </div>

        <div class="flex-1">
          <h2 class="text-lg font-bold text-gray-900 dark:text-white mb-1">
            Inteligência Artificial
          </h2>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            Sugestões de agrupamento inteligente
          </p>
        </div>

        <button
          @click="$emit('refresh')"
          :disabled="loading"
          class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
          title="Atualizar sugestões"
        >
          <ArrowPathIcon
            :class="[
              'w-5 h-5 text-gray-600 dark:text-gray-400',
              loading && 'animate-spin'
            ]"
          />
        </button>
      </div>

      <!-- Estatísticas -->
      <div v-if="!loading && totalSugestoes > 0" class="mt-4 grid grid-cols-2 gap-3">
        <div class="bg-gradient-to-br from-primary-50 to-blue-50 dark:from-primary-900/20 dark:to-blue-900/20 rounded-lg p-3 border border-primary-200 dark:border-primary-800">
          <p class="text-xs text-primary-700 dark:text-primary-300 font-medium mb-1">
            Agrupamentos
          </p>
          <p class="text-2xl font-bold text-primary-900 dark:text-primary-100">
            {{ totalSugestoes }}
          </p>
        </div>
        
        <div class="bg-gradient-to-br from-purple-50 to-pink-50 dark:from-purple-900/20 dark:to-pink-900/20 rounded-lg p-3 border border-purple-200 dark:border-purple-800">
          <p class="text-xs text-purple-700 dark:text-purple-300 font-medium mb-1">
            Protocolos
          </p>
          <p class="text-2xl font-bold text-purple-900 dark:text-purple-100">
            {{ totalProtocolosAgrupáveis }}
          </p>
        </div>
      </div>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="flex-1 flex items-center justify-center p-6">
      <div class="text-center">
        <div class="relative w-16 h-16 mx-auto mb-4">
          <div class="absolute inset-0 bg-gradient-to-br from-primary-500 to-purple-600 rounded-full blur-md opacity-50 animate-pulse"></div>
          <div class="relative w-16 h-16 border-4 border-primary-200 dark:border-primary-800 border-t-primary-600 dark:border-t-primary-400 rounded-full animate-spin"></div>
        </div>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          Analisando protocolos...
        </p>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else-if="totalSugestoes === 0" class="flex-1 flex items-center justify-center p-6">
      <div class="text-center max-w-xs">
        <div class="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-gray-100 to-gray-200 dark:from-gray-800 dark:to-gray-700 rounded-full flex items-center justify-center">
          <CheckCircleIcon class="w-8 h-8 text-gray-400 dark:text-gray-500" />
        </div>
        <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-2">
          Nenhum agrupamento identificado
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400">
          A IA está analisando continuamente. Novas sugestões aparecerão aqui.
        </p>
      </div>
    </div>

    <!-- Lista de Sugestões -->
    <div v-else class="flex-1 overflow-y-auto p-4 space-y-3">
      <div
        v-for="sugestao in sugestoes"
        :key="sugestao.id"
        class="group relative"
      >
        <!-- Brilho de fundo (efeito hi-tech) -->
        <div class="absolute -inset-0.5 bg-gradient-to-r from-primary-500 via-purple-500 to-pink-500 rounded-xl opacity-0 group-hover:opacity-20 blur transition-all duration-300"></div>
        
        <!-- Card da Sugestão -->
        <div class="relative bg-white dark:bg-gray-800 rounded-xl border-2 border-gray-200 dark:border-gray-700 group-hover:border-primary-300 dark:group-hover:border-primary-600 transition-all duration-300 overflow-hidden">
          <div class="absolute top-3 right-3 z-10 flex flex-col items-end gap-1">
            <span
              v-if="sugestao.tipo_acao === 'anexar'"
              class="px-2 py-0.5 rounded-full text-[10px] font-bold uppercase tracking-wide bg-purple-100 text-purple-800 dark:bg-purple-900/40 dark:text-purple-200 border border-purple-200 dark:border-purple-700"
            >
              Anexar
            </span>
            <div
              :class="[
                'px-2 py-1 rounded-full text-xs font-bold flex items-center gap-1',
                sugestao.confianca_ia >= 0.9
                  ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                  : sugestao.confianca_ia >= 0.8
                  ? 'bg-blue-100 text-blue-800 dark:bg-blue-900/30 dark:text-blue-300'
                  : 'bg-yellow-100 text-yellow-800 dark:bg-yellow-900/30 dark:text-yellow-300'
              ]"
            >
              <SparklesIcon class="w-3 h-3" />
              {{ Math.round(sugestao.confianca_ia * 100) }}%
            </div>
          </div>

          <div class="p-4">
            <!-- Título e Região -->
            <div class="mb-3 pr-16">
              <h3 class="text-sm font-bold text-gray-900 dark:text-white mb-1">
                {{ sugestao.titulo_resumo }}
              </h3>
              <p
                v-if="sugestao.tipo_acao === 'anexar' && sugestao.super_os_codigo"
                class="text-xs font-medium text-purple-700 dark:text-purple-300 mb-0.5"
              >
                Destino: {{ sugestao.super_os_codigo }}
              </p>
              <div class="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
                <MapPinIcon class="w-3.5 h-3.5" />
                {{ sugestao.regiao }} · Raio: {{ sugestao.raio_km }} km
              </div>
            </div>

            <!-- Grid de Fotos -->
            <div class="grid grid-cols-3 gap-2 mb-3">
              <div
                v-for="(protocolo, idx) in sugestao.protocolos.slice(0, 3)"
                :key="protocolo.id"
                class="relative aspect-square rounded-lg overflow-hidden bg-gray-100 dark:bg-gray-700"
              >
                <img
                  v-if="protocolo.foto_url"
                  :src="protocolo.foto_url"
                  :alt="`Foto ${idx + 1}`"
                  class="w-full h-full object-cover"
                />
                <div
                  v-else
                  class="w-full h-full flex items-center justify-center bg-gradient-to-br from-gray-200 to-gray-300 dark:from-gray-600 dark:to-gray-700"
                >
                  <MapPinIcon class="w-6 h-6 text-gray-500 dark:text-gray-400" />
                </div>
                <div class="absolute inset-0 bg-black/30 flex items-center justify-center">
                  <span class="text-xs font-bold text-white">
                    {{ protocolo.codigo.split('-').pop() }}
                  </span>
                </div>
              </div>
            </div>

            <!-- Economia Estimada -->
            <div class="bg-gradient-to-r from-green-50 to-emerald-50 dark:from-green-900/20 dark:to-emerald-900/20 rounded-lg p-3 mb-3 border border-green-200 dark:border-green-800">
              <div class="flex items-center gap-2 mb-2">
                <div class="p-1 bg-green-100 dark:bg-green-900/40 rounded">
                  <BanknotesIcon class="w-4 h-4 text-green-600 dark:text-green-400" />
                </div>
                <span class="text-xs font-semibold text-green-900 dark:text-green-100">
                  Economia Estimada
                </span>
              </div>
              <div class="grid grid-cols-3 gap-2 text-xs">
                <div>
                  <p class="text-green-700 dark:text-green-300 font-medium">
                    {{ sugestao.economia_estimada.equipes }}
                  </p>
                  <p class="text-green-600 dark:text-green-400">equipes</p>
                </div>
                <div>
                  <p class="text-green-700 dark:text-green-300 font-medium">
                    {{ sugestao.economia_estimada.tempo_horas }}h
                  </p>
                  <p class="text-green-600 dark:text-green-400">tempo</p>
                </div>
                <div>
                  <p class="text-green-700 dark:text-green-300 font-medium">
                    R$ {{ sugestao.economia_estimada.custo_reais }}
                  </p>
                  <p class="text-green-600 dark:text-green-400">custo</p>
                </div>
              </div>
            </div>

            <!-- Botões de Ação -->
            <div class="flex gap-2">
              <button
                @click="$emit('visualizar-no-mapa', sugestao)"
                class="flex-1 px-3 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium transition-colors flex items-center justify-center gap-2"
              >
                <MapIcon class="w-4 h-4" />
                Ver no Mapa
              </button>
              <button
                @click="aprovar(sugestao)"
                :disabled="aprovando === sugestao.id"
                class="flex-1 px-3 py-2 bg-gradient-to-r from-primary-600 to-purple-600 hover:from-primary-700 hover:to-purple-700 text-white rounded-lg text-sm font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg shadow-primary-500/50"
              >
                <CheckIcon v-if="aprovando !== sugestao.id" class="w-4 h-4" />
                <div v-else class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                {{
                  aprovando === sugestao.id
                    ? sugestao.tipo_acao === 'anexar'
                      ? 'Anexando...'
                      : sugestao.tipo_acao === 'criar_retroativa'
                        ? 'Agrupando...'
                        : 'Criando...'
                    : sugestao.tipo_acao === 'anexar'
                      ? 'Anexar à OS Existente'
                      : sugestao.tipo_acao === 'criar_retroativa'
                        ? 'Unir à âncora'
                        : 'Aprovar'
                }}
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer com Info -->
    <div v-if="!loading && totalSugestoes > 0" class="p-4 border-t border-gray-200 dark:border-gray-700 bg-white/50 dark:bg-gray-800/50 backdrop-blur-sm">
      <div class="flex items-center gap-2 text-xs text-gray-600 dark:text-gray-400">
        <ClockIcon class="w-4 h-4" />
        <span>
          Última atualização: {{ formatarDataHora(ultimaAtualizacao) }}
        </span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import { useSuperOSStore } from '@/stores/super_os'
import { getApiErrorMessage } from '@/utils/apiError'
import {
  SparklesIcon,
  ArrowPathIcon,
  CheckCircleIcon,
  MapPinIcon,
  BanknotesIcon,
  MapIcon,
  CheckIcon,
  ClockIcon
} from '@heroicons/vue/24/outline'

const emit = defineEmits([
  'refresh',
  'visualizar-no-mapa',
  'sugestao-aprovada',
  'sugestao-erro'
])

// Store
const superOSStore = useSuperOSStore()
const { sugestoes, loading, ultimaAtualizacao } = storeToRefs(superOSStore)

const totalSugestoes = computed(() => superOSStore.totalSugestoes)
const totalProtocolosAgrupáveis = computed(() => superOSStore.totalProtocolosAgrupáveis)

// Estado local
const aprovando = ref(null)

// Funções
async function aprovar(sugestao) {
  try {
    aprovando.value = sugestao.id
    const resultado = await superOSStore.executarSugestao(sugestao)
    const qtd =
      sugestao.quantidade ||
      sugestao.protocolo_ids?.length ||
      sugestao.protocolos?.length ||
      0
    emit('sugestao-aprovada', {
      sugestao_id: sugestao.id,
      tipo_acao: sugestao.tipo_acao || 'criar',
      titulo: sugestao.titulo_resumo,
      protocolos: qtd,
      codigo: resultado?.super_os?.codigo,
      super_os: resultado?.super_os
    })
  } catch (error) {
    emit('sugestao-erro', getApiErrorMessage(error, 'Erro ao criar Super OS.'))
  } finally {
    aprovando.value = null
  }
}

function formatarDataHora(data) {
  if (!data) return 'Nunca'
  
  const d = new Date(data)
  const agora = new Date()
  const diff = agora - d
  
  // Menos de 1 minuto
  if (diff < 60000) return 'Agora'
  
  // Menos de 1 hora
  if (diff < 3600000) {
    const minutos = Math.floor(diff / 60000)
    return `há ${minutos} ${minutos === 1 ? 'minuto' : 'minutos'}`
  }
  
  // Menos de 1 dia
  if (diff < 86400000) {
    const horas = Math.floor(diff / 3600000)
    return `há ${horas} ${horas === 1 ? 'hora' : 'horas'}`
  }
  
  // Formato padrão
  const dia = d.getDate().toString().padStart(2, '0')
  const mes = (d.getMonth() + 1).toString().padStart(2, '0')
  const hora = d.getHours().toString().padStart(2, '0')
  const min = d.getMinutes().toString().padStart(2, '0')
  return `${dia}/${mes} ${hora}:${min}`
}
</script>

<style scoped>
/* Animação sutil de brilho */
@keyframes shimmer {
  0% {
    background-position: -1000px 0;
  }
  100% {
    background-position: 1000px 0;
  }
}

.group:hover .shimmer {
  animation: shimmer 2s infinite linear;
  background: linear-gradient(
    to right,
    transparent 0%,
    rgba(255, 255, 255, 0.1) 50%,
    transparent 100%
  );
  background-size: 1000px 100%;
}
</style>
