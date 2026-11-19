<template>
  <div class="space-y-6">
    <!-- Dados Coletados pela IA -->
    <section class="card">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-lg bg-primary-100 dark:bg-primary-900 flex items-center justify-center">
          <CpuChipIcon class="w-6 h-6 text-primary-600 dark:text-primary-400" />
        </div>
        <div>
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
            Dados Coletados pela IA
          </h2>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            Informações extraídas do atendimento conversacional
          </p>
        </div>
      </div>

      <div
        v-if="!temDadosColetados"
        class="text-sm text-gray-500 dark:text-gray-400 py-4 text-center border border-dashed border-gray-300 dark:border-gray-600 rounded-lg"
      >
        Nenhum dado estruturado foi registrado neste protocolo.
      </div>

      <div
        v-else
        class="overflow-hidden border border-gray-200 dark:border-gray-700 rounded-lg"
      >
        <table class="w-full divide-y divide-gray-200 dark:divide-gray-700">
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700 bg-white dark:bg-gray-800">
            <tr
              v-for="(valor, campo) in protocolo.dados_coletados"
              :key="campo"
              class="hover:bg-gray-50 dark:hover:bg-gray-750 transition-colors"
            >
              <td class="px-4 py-3 text-sm font-medium text-gray-700 dark:text-gray-300 bg-gray-50 dark:bg-gray-900 w-1/3">
                {{ campo }}
              </td>
              <td class="px-4 py-3 text-sm text-gray-900 dark:text-white">
                {{ valor }}
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </section>

    <!-- Localização -->
    <section class="card">
      <div class="flex items-center gap-3 mb-4">
        <div class="w-10 h-10 rounded-lg bg-success-100 dark:bg-success-900 flex items-center justify-center">
          <MapPinIcon class="w-6 h-6 text-success-600 dark:text-success-400" />
        </div>
        <div>
          <h2 class="text-lg font-semibold text-gray-900 dark:text-white">
            Localização
          </h2>
          <p class="text-sm text-gray-600 dark:text-gray-400">
            Endereço e coordenadas geográficas
          </p>
        </div>
      </div>

      <div class="mb-4 p-4 bg-gray-50 dark:bg-gray-750 rounded-lg border border-gray-200 dark:border-gray-700">
        <div class="space-y-2">
          <div class="flex items-start gap-3">
            <BuildingOffice2Icon class="w-5 h-5 text-gray-400 mt-0.5 flex-shrink-0" />
            <div class="flex-1">
              <p class="text-sm font-medium text-gray-900 dark:text-white">
                {{ enderecoLinha }}
              </p>
              <p
                v-if="protocolo.localizacao.complemento"
                class="text-sm text-gray-600 dark:text-gray-400"
              >
                {{ protocolo.localizacao.complemento }}
              </p>
              <p
                v-if="linhaBairroCidade"
                class="text-sm text-gray-600 dark:text-gray-400"
              >
                {{ linhaBairroCidade }}
              </p>
              <p
                v-if="protocolo.localizacao.cep"
                class="text-sm text-gray-500 dark:text-gray-500"
              >
                CEP: {{ protocolo.localizacao.cep }}
              </p>
            </div>
          </div>

          <div
            v-if="protocolo.localizacao.pontos_referencia"
            class="flex items-start gap-3 pt-2 border-t border-gray-200 dark:border-gray-600"
          >
            <InformationCircleIcon class="w-5 h-5 text-blue-500 mt-0.5 flex-shrink-0" />
            <div>
              <p class="text-xs font-medium text-gray-700 dark:text-gray-300">
                Ponto de Referência:
              </p>
              <p class="text-sm text-gray-600 dark:text-gray-400">
                {{ protocolo.localizacao.pontos_referencia }}
              </p>
            </div>
          </div>
        </div>
      </div>

      <LocationMap
        v-if="temCoordenadas"
        :latitude="coordenadas.latitude"
        :longitude="coordenadas.longitude"
        :draggable="false"
        :zoom="16"
        height="16rem"
      />
      <div
        v-else
        class="relative h-48 flex items-center justify-center bg-gray-100 dark:bg-gray-750 rounded-lg border border-gray-300 dark:border-gray-600"
      >
        <div class="text-center px-4">
          <MapIcon class="w-10 h-10 text-gray-400 mx-auto mb-2" />
          <p class="text-sm text-gray-600 dark:text-gray-400">
            Coordenadas não disponíveis para exibir o mapa.
          </p>
        </div>
      </div>

      <p
        v-if="temCoordenadas"
        class="mt-2 text-xs text-gray-500 dark:text-gray-400 text-right"
      >
        {{ coordenadasFormatadas }}
      </p>
    </section>

    <ChatAuditoria :historico="protocolo.historico_chat" />
  </div>
</template>

<script setup>
import { computed } from 'vue'
import {
  CpuChipIcon,
  MapPinIcon,
  BuildingOffice2Icon,
  InformationCircleIcon,
  MapIcon
} from '@heroicons/vue/24/outline'
import ChatAuditoria from './ChatAuditoria.vue'
import LocationMap from '@/components/pwa/LocationMap.vue'

const props = defineProps({
  protocolo: {
    type: Object,
    required: true
  }
})

const temDadosColetados = computed(() => {
  const dados = props.protocolo?.dados_coletados
  return dados && Object.keys(dados).length > 0
})

const coordenadas = computed(() => {
  const loc = props.protocolo?.localizacao || {}
  const lat = Number(loc.latitude)
  const lng = Number(loc.longitude)
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) {
    return { latitude: null, longitude: null }
  }
  return { latitude: lat, longitude: lng }
})

const temCoordenadas = computed(
  () => coordenadas.value.latitude != null && coordenadas.value.longitude != null
)

const enderecoLinha = computed(() => {
  const loc = props.protocolo?.localizacao || {}
  const partes = [loc.endereco, loc.numero].filter(Boolean)
  if (partes.length) return partes.join(', ')
  return props.protocolo?.endereco || 'Endereço não informado'
})

const linhaBairroCidade = computed(() => {
  const loc = props.protocolo?.localizacao || {}
  const bairro = loc.bairro || props.protocolo?.bairro || ''
  const cidade = loc.cidade || ''
  const estado = loc.estado || ''
  if (!bairro && !cidade && !estado) return ''
  if (cidade && estado) {
    return bairro ? `${bairro} — ${cidade}/${estado}` : `${cidade}/${estado}`
  }
  return [bairro, cidade, estado].filter(Boolean).join(' — ')
})

const coordenadasFormatadas = computed(() => {
  if (!temCoordenadas.value) return ''
  const { latitude, longitude } = coordenadas.value
  return `Lat ${latitude.toFixed(5)}, Long ${longitude.toFixed(5)} · OpenStreetMap`
})
</script>

<style scoped>
tbody tr {
  transition: background-color 0.15s ease;
}
</style>
