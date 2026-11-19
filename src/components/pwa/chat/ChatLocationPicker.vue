<template>
  <div class="card bg-white dark:bg-gray-800 high-contrast:bg-gray-900 high-contrast:border-2 high-contrast:border-yellow-300 p-4 space-y-4 max-w-md animate-scale-in">
    <div class="flex items-center gap-2 mb-3">
      <MapPinIcon class="w-5 h-5 text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300" aria-hidden="true" />
      <h3 class="text-sm font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300">
        Compartilhar Localização
      </h3>
    </div>

    <div class="relative">
      <label for="chat-location-search" class="block text-xs font-semibold text-gray-700 dark:text-gray-300 high-contrast:text-white mb-2">
        Buscar endereço
      </label>
      <div class="relative">
        <input
          id="chat-location-search"
          v-model="enderecoTexto"
          type="search"
          autocomplete="street-address"
          placeholder="Digite o endereço ou nome do local..."
          class="input pr-12"
          aria-describedby="chat-location-search-hint"
          @keydown.enter="buscarEndereco"
          :disabled="carregando"
        />
        <span id="chat-location-search-hint" class="sr-only">Pressione Enter ou use o botão buscar para pesquisar</span>
        <button
          type="button"
          @click="buscarEndereco"
          :disabled="carregando || !enderecoTexto.trim()"
          class="absolute right-1 top-1/2 -translate-y-1/2 min-w-[44px] min-h-[44px] p-2 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-50 focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-primary-500"
          aria-label="Buscar endereço digitado"
        >
          <MagnifyingGlassIcon class="w-5 h-5 text-gray-600 dark:text-gray-400 high-contrast:text-yellow-300" aria-hidden="true" />
        </button>
      </div>

      <ul
        v-if="resultadosBusca.length"
        class="mt-2 max-h-40 overflow-y-auto rounded-card border border-gray-200 dark:border-gray-600 high-contrast:border-yellow-300 divide-y divide-gray-100 dark:divide-gray-700"
      >
        <li v-for="(item, idx) in resultadosBusca" :key="idx">
          <button
            type="button"
            class="w-full text-left px-3 py-2 text-xs hover:bg-gray-50 dark:hover:bg-gray-700/80 high-contrast:hover:bg-gray-800"
            @click="selecionarResultado(item)"
          >
            {{ item.endereco_completo }}
          </button>
        </li>
      </ul>
    </div>

    <div class="relative py-2">
      <div class="absolute inset-0 flex items-center">
        <div class="w-full border-t border-gray-200 dark:border-gray-700 high-contrast:border-yellow-300"></div>
      </div>
      <div class="relative flex justify-center">
        <span class="px-3 text-xs font-semibold text-gray-500 dark:text-gray-400 high-contrast:text-white bg-white dark:bg-gray-800 high-contrast:bg-gray-900">
          OU
        </span>
      </div>
    </div>

    <button
      v-if="temEnderecoCadastrado"
      type="button"
      @click="usarEnderecoCadastrado"
      :disabled="carregando"
      class="w-full btn-secondary flex items-center justify-center gap-2 disabled:opacity-50"
    >
      <HomeIcon class="w-5 h-5" aria-hidden="true" />
      Usar meu endereço cadastrado
    </button>

    <button
      type="button"
      @click="usarLocalizacaoAtual"
      :disabled="carregando"
      class="w-full btn-secondary flex items-center justify-center gap-2 min-h-[44px] disabled:opacity-50"
      aria-label="Usar minha localização atual pelo GPS"
    >
      <span v-if="carregando" class="w-4 h-4 border-2 border-primary-600 border-t-transparent rounded-full animate-spin motion-reduce:animate-none" aria-hidden="true"></span>
      <MapPinIcon v-else class="w-5 h-5" aria-hidden="true" />
      {{ carregando ? 'Obtendo localização...' : 'Usar minha localização atual (GPS)' }}
    </button>

    <div class="sr-only" aria-live="assertive" aria-atomic="true">
      <span v-if="carregando">Obtendo localização pelo GPS, aguarde.</span>
      <span v-else-if="erro">{{ erro }}</span>
    </div>

    <div v-if="coordenadas.latitude != null && coordenadas.longitude != null" class="space-y-2">
      <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300 high-contrast:text-white">
        Localização no mapa
      </label>
      <LocationMap
        :latitude="coordenadas.latitude"
        :longitude="coordenadas.longitude"
        draggable
        height="12rem"
        @move="aoMoverMarcador"
      />
      <p v-if="enderecoFormatado" class="p-3 bg-gray-50 dark:bg-gray-700/50 high-contrast:bg-gray-800 rounded-card text-xs text-gray-700 dark:text-gray-300 high-contrast:text-white flex items-start gap-2">
        <MapPinIcon class="w-4 h-4 flex-shrink-0 mt-0.5 text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300" />
        <span>{{ enderecoFormatado }}</span>
      </p>
    </div>

    <div v-if="erro" class="p-3 bg-red-50 dark:bg-red-900/20 high-contrast:bg-transparent border border-red-200 dark:border-red-800 high-contrast:border-red-500 rounded-card">
      <div class="flex items-start gap-2">
        <ExclamationCircleIcon class="w-5 h-5 text-red-600 dark:text-red-400 flex-shrink-0" aria-hidden="true" />
        <p class="text-xs text-red-800 dark:text-red-200 high-contrast:text-white high-contrast:font-bold">
          {{ erro }}
        </p>
      </div>
    </div>

    <div class="flex gap-2 pt-2">
      <button type="button" @click="$emit('cancelar')" class="btn-secondary flex-1" :disabled="carregando">
        Cancelar
      </button>
      <button
        type="button"
        @click="confirmarLocalizacao"
        :disabled="coordenadas.latitude == null || carregando"
        class="btn-primary flex-1 disabled:opacity-50 disabled:cursor-not-allowed"
      >
        <CheckIcon class="w-5 h-5 inline-block mr-1" aria-hidden="true" />
        Confirmar Local
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import {
  MapPinIcon,
  MagnifyingGlassIcon,
  CheckIcon,
  ExclamationCircleIcon,
  HomeIcon
} from '@heroicons/vue/24/outline'
import LocationMap from '@/components/pwa/LocationMap.vue'
import { atendimentosService } from '@/services/api'
import { useGeolocation } from '@/composables/useGeolocation'
import { useAuthStore } from '@/stores/auth'
import { useCepLookup } from '@/composables/useCepLookup'

const emit = defineEmits(['confirmar', 'cancelar'])

const authStore = useAuthStore()
const { getCurrentPosition } = useGeolocation()
const { buscarCepComGeocoding } = useCepLookup()

const enderecoCadastrado = computed(() => authStore.user?.endereco)
const temEnderecoCadastrado = computed(() => {
  const e = enderecoCadastrado.value
  return Boolean(e && (e.logradouro || e.cidade))
})

const enderecoTexto = ref('')
const coordenadas = ref({
  latitude: null,
  longitude: null
})
const enderecoFormatado = ref('')
const resultadosBusca = ref([])
const carregando = ref(false)
const erro = ref(null)

async function atualizarEnderecoPorCoords(lat, lng) {
  try {
    const data = await atendimentosService.geocodeReverso(lat, lng)
    enderecoFormatado.value =
      data.endereco_completo ||
      data.mensagem ||
      `Lat ${lat.toFixed(5)}, Lng ${lng.toFixed(5)}`
  } catch {
    enderecoFormatado.value = `Lat ${lat.toFixed(5)}, Lng ${lng.toFixed(5)}`
  }
}

function definirCoordenadas(lat, lng, endereco = '') {
  coordenadas.value = { latitude: lat, longitude: lng }
  if (endereco) {
    enderecoFormatado.value = endereco
  } else {
    atualizarEnderecoPorCoords(lat, lng)
  }
}

function selecionarResultado(item) {
  resultadosBusca.value = []
  enderecoTexto.value = item.endereco_completo
  definirCoordenadas(item.latitude, item.longitude, item.endereco_completo)
}

async function buscarEndereco() {
  const query = enderecoTexto.value.trim()
  if (!query) return

  carregando.value = true
  erro.value = null
  resultadosBusca.value = []

  try {
    const data = await atendimentosService.buscarEndereco(query)
    const lista = data.resultados || []

    if (!lista.length) {
      erro.value = data.mensagem || 'Nenhum endereço encontrado. Tente outro termo ou use o GPS.'
      return
    }

    if (lista.length === 1) {
      selecionarResultado(lista[0])
    } else {
      resultadosBusca.value = lista
    }
  } catch {
    erro.value = 'Não foi possível buscar o endereço. Tente novamente ou use o GPS.'
  } finally {
    carregando.value = false
  }
}

function montarTextoEndereco(e) {
  const partes = [
    e.logradouro,
    e.numero,
    e.complemento,
    e.bairro,
    e.cidade && e.estado ? `${e.cidade}/${e.estado}` : e.cidade || e.estado
  ].filter((p) => p && String(p).trim())
  return partes.join(', ')
}

async function usarEnderecoCadastrado() {
  const e = enderecoCadastrado.value
  if (!e) {
    erro.value = 'Nenhum endereço no seu cadastro. Use busca ou GPS.'
    return
  }

  carregando.value = true
  erro.value = null
  resultadosBusca.value = []

  const texto = montarTextoEndereco(e)
  enderecoTexto.value = texto

  let lat = e.coordenadas?.latitude ?? e.latitude
  let lng = e.coordenadas?.longitude ?? e.longitude

  if (lat == null || lng == null) {
    try {
      const geo = await buscarCepComGeocoding(e.cep, e.numero || '')
      lat = geo?.coordenadas?.latitude
      lng = geo?.coordenadas?.longitude
    } catch {
      erro.value = 'Não foi possível localizar seu endereço cadastrado. Tente buscar ou GPS.'
      carregando.value = false
      return
    }
  }

  if (lat != null && lng != null) {
    definirCoordenadas(lat, lng, texto)
  } else {
    erro.value = 'Coordenadas do endereço não encontradas. Use busca ou GPS.'
  }
  carregando.value = false
}

async function usarLocalizacaoAtual() {
  carregando.value = true
  erro.value = null
  resultadosBusca.value = []

  const resultado = await getCurrentPosition()
  carregando.value = false

  if (!resultado.success) {
    erro.value = resultado.error || 'Erro ao obter localização.'
    return
  }

  const { latitude, longitude } = resultado.coords
  definirCoordenadas(latitude, longitude)
}

function aoMoverMarcador({ latitude, longitude }) {
  coordenadas.value = { latitude, longitude }
  atualizarEnderecoPorCoords(latitude, longitude)
}

function confirmarLocalizacao() {
  if (coordenadas.value.latitude == null) return

  emit('confirmar', {
    latitude: coordenadas.value.latitude,
    longitude: coordenadas.value.longitude,
    endereco_texto:
      enderecoFormatado.value || enderecoTexto.value.trim() || 'Localização informada'
  })
}
</script>
