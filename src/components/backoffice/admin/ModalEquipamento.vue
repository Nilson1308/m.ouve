<template>
  <Teleport to="body">
    <div
      class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      @click.self="$emit('fechar')"
    >
      <div
        class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90dvh] flex flex-col overflow-hidden border border-gray-200/80 dark:border-gray-700"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="tituloId"
      >
        <div
          class="shrink-0 px-6 py-5 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-cyan-50 to-primary-50 dark:from-cyan-950/40 dark:to-primary-950/30"
        >
          <div class="flex items-start justify-between gap-3">
            <div class="flex items-center gap-3 min-w-0">
              <div class="p-2 bg-cyan-100 dark:bg-cyan-900/40 rounded-lg shrink-0">
                <BuildingStorefrontIcon class="w-6 h-6 text-cyan-700 dark:text-cyan-300" />
              </div>
              <div class="min-w-0">
                <h2 :id="tituloId" class="text-xl font-bold text-gray-900 dark:text-white">
                  {{ equipamento ? 'Editar equipamento' : 'Novo equipamento público' }}
                </h2>
                <p class="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                  UBS, escolas, CRAS e demais locais vinculados a uma secretaria
                </p>
              </div>
            </div>
            <button
              type="button"
              class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
              aria-label="Fechar"
              @click="$emit('fechar')"
            >
              <XMarkIcon class="w-5 h-5 text-gray-500" />
            </button>
          </div>
        </div>

        <form class="flex-1 overflow-y-auto p-6 space-y-5" @submit.prevent="salvar">
          <p v-if="erroForm" class="text-sm text-red-700 dark:text-red-300 bg-red-50 dark:bg-red-950/40 border border-red-200 dark:border-red-800 rounded-lg px-3 py-2" role="alert">
            {{ erroForm }}
          </p>

          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Nome *</label>
            <input v-model="formulario.nome" type="text" class="input" required placeholder="Ex.: UBS Vila Esperança" />
          </div>

          <div class="grid sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Tipo *</label>
              <select v-model="formulario.tipo" class="input" required>
                <option v-for="t in TIPOS_EQUIPAMENTO_PUBLICO" :key="t.value" :value="t.value">
                  {{ t.label }}
                </option>
              </select>
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Secretaria responsável *</label>
              <select v-model="formulario.unidadeResponsavelId" class="input" required>
                <option value="" disabled>Selecione...</option>
                <option v-for="u in unidadesAtivas" :key="u.id" :value="u.id">
                  {{ u.nome }}{{ u.sigla ? ` (${u.sigla})` : '' }}
                </option>
              </select>
            </div>
          </div>

          <div class="grid sm:grid-cols-2 gap-4">
            <div>
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Bairro</label>
              <input v-model="formulario.bairro" type="text" class="input" placeholder="Centro, Vila Nova..." />
            </div>
            <div>
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Endereço</label>
              <input v-model="formulario.endereco" type="text" class="input" placeholder="Rua, número..." />
            </div>
          </div>

          <section
            class="rounded-xl border border-cyan-200/80 dark:border-cyan-800/60 bg-cyan-50/40 dark:bg-cyan-950/20 p-4 space-y-3"
            aria-labelledby="equipamento-mapa-titulo"
          >
            <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-2">
              <div>
                <h3 id="equipamento-mapa-titulo" class="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  <MapPinIcon class="w-5 h-5 text-cyan-600 dark:text-cyan-400" />
                  Localização no mapa
                </h3>
                <p class="text-xs text-gray-600 dark:text-gray-400 mt-0.5">
                  Opcional — melhora mapas operacionais e localização automática em protocolos sobre o equipamento.
                </p>
              </div>
              <button
                type="button"
                class="btn-secondary text-xs py-1.5 px-3 shrink-0"
                :disabled="geocodificando || (!formulario.endereco?.trim() && !formulario.bairro?.trim())"
                @click="localizarEnderecoNoMapa"
              >
                <span v-if="geocodificando" class="inline-flex items-center gap-1.5">
                  <span class="w-3 h-3 border-2 border-primary-500 border-t-transparent rounded-full animate-spin" />
                  Localizando…
                </span>
                <span v-else>Localizar endereço no mapa</span>
              </button>
            </div>

            <p v-if="erroGeo" class="text-xs text-amber-800 dark:text-amber-200">{{ erroGeo }}</p>

            <ul
              v-if="resultadosGeo.length"
              class="max-h-36 overflow-y-auto rounded-lg border border-gray-200 dark:border-gray-600 divide-y divide-gray-100 dark:divide-gray-700"
            >
              <li v-for="(item, idx) in resultadosGeo" :key="idx">
                <button
                  type="button"
                  class="w-full text-left px-3 py-2.5 text-xs hover:bg-gray-50 dark:hover:bg-gray-700/80 min-h-[44px]"
                  @click="selecionarResultadoGeo(item)"
                >
                  {{ item.endereco_completo }}
                </button>
              </li>
            </ul>

            <div class="flex flex-wrap items-end gap-2">
              <div class="flex-1 min-w-[8.5rem]">
                <label class="block text-[11px] font-semibold text-gray-600 dark:text-gray-400 mb-1">Latitude</label>
                <input
                  v-model="latitudeInput"
                  type="text"
                  inputmode="decimal"
                  class="input text-sm font-mono"
                  placeholder="-23.522200"
                  @change="aplicarCoordenadasDosInputs"
                />
              </div>
              <div class="flex-1 min-w-[8.5rem]">
                <label class="block text-[11px] font-semibold text-gray-600 dark:text-gray-400 mb-1">Longitude</label>
                <input
                  v-model="longitudeInput"
                  type="text"
                  inputmode="decimal"
                  class="input text-sm font-mono"
                  placeholder="-46.188300"
                  @change="aplicarCoordenadasDosInputs"
                />
              </div>
              <button
                type="button"
                class="text-xs font-medium text-gray-600 dark:text-gray-300 hover:text-red-600 dark:hover:text-red-400 px-2 py-2 underline"
                @click="limparPonto"
              >
                Limpar ponto
              </button>
            </div>

            <LocationMap
              ref="mapaRef"
              :latitude="formulario.latitude"
              :longitude="formulario.longitude"
              :draggable="temPonto"
              pick-on-click
              height="14rem"
              @move="aoMoverMarcador"
            />
            <p class="text-[11px] text-gray-500 dark:text-gray-400">
              {{
                temPonto
                  ? 'Arraste o pino ou clique no mapa para ajustar a entrada do equipamento.'
                  : 'Clique no mapa para posicionar o pino ou use “Localizar endereço no mapa”.'
              }}
            </p>
          </section>

          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
              Apelidos (sinônimos para a IA)
            </label>
            <p class="text-xs text-gray-500 dark:text-gray-400 mb-2 leading-relaxed">
              Nomes populares usados pelos cidadãos (ex.: Postinho do Centro). Ajudam o chat a identificar o local
              automaticamente.
            </p>
            <div class="flex flex-wrap gap-2 mb-2" v-if="formulario.apelidos.length">
              <span
                v-for="(tag, i) in formulario.apelidos"
                :key="`${tag}-${i}`"
                class="inline-flex items-center gap-1 px-2.5 py-1 rounded-full text-xs font-medium bg-gray-100 dark:bg-gray-700 text-gray-800 dark:text-gray-200"
              >
                {{ tag }}
                <button type="button" class="p-0.5 rounded hover:bg-gray-200 dark:hover:bg-gray-600" :aria-label="`Remover ${tag}`" @click="removerApelido(i)">
                  <XMarkIcon class="w-3.5 h-3.5" />
                </button>
              </span>
            </div>
            <input
              v-model="entradaApelido"
              type="text"
              class="input"
              placeholder="Digite e pressione Enter ou vírgula"
              @keydown.enter.prevent="adicionarApelido"
              @keydown="onApelidoKeydown"
              @blur="adicionarApelido"
            />
          </div>

          <div
            class="flex items-start gap-3 p-4 bg-gray-50 dark:bg-gray-700/40 rounded-lg border border-gray-200 dark:border-gray-600"
          >
            <button
              type="button"
              role="switch"
              :aria-checked="formulario.ativo"
              :class="[
                'relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors mt-0.5',
                formulario.ativo ? 'bg-green-600' : 'bg-gray-300 dark:bg-gray-600'
              ]"
              @click="formulario.ativo = !formulario.ativo"
            >
              <span
                :class="[
                  'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow transition',
                  formulario.ativo ? 'translate-x-5' : 'translate-x-0'
                ]"
              />
            </button>
            <div>
              <p class="text-sm font-semibold text-gray-900 dark:text-white">Equipamento ativo</p>
              <p class="text-xs text-gray-600 dark:text-gray-400 mt-0.5">Inativos não aparecem no lookup do PWA.</p>
            </div>
          </div>
        </form>

        <div class="shrink-0 px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50 flex flex-col-reverse sm:flex-row gap-2 sm:justify-end">
          <button type="button" class="btn-secondary" :disabled="salvando" @click="$emit('fechar')">Cancelar</button>
          <button type="button" class="btn-primary" :disabled="salvando" @click="salvar">
            {{ salvando ? 'Salvando…' : 'Salvar equipamento' }}
          </button>
        </div>
      </div>
    </div>
  </Teleport>
</template>

<script setup>
import { computed, nextTick, onMounted, reactive, ref, watch } from 'vue'
import { BuildingStorefrontIcon, MapPinIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import LocationMap from '@/components/pwa/LocationMap.vue'
import { atendimentosService } from '@/services/api'
import { useCepLookup } from '@/composables/useCepLookup'
import { useAdminStore } from '@/stores/admin'
import { TIPOS_EQUIPAMENTO_PUBLICO } from '@/constants/equipamentosPublicos'
import { getApiErrorMessage } from '@/utils/apiError'
import { resolverCoordenadasPorEndereco } from '@/utils/geocodificarEnderecoTexto'

const props = defineProps({
  equipamento: { type: Object, default: null },
  unidadesAtivas: { type: Array, default: () => [] }
})

const emit = defineEmits(['fechar', 'salvo'])

const adminStore = useAdminStore()
const { buscarCepComGeocoding } = useCepLookup()
const tituloId = `modal-equipamento-${Math.random().toString(36).slice(2, 8)}`
const entradaApelido = ref('')
const salvando = ref(false)
const erroForm = ref('')
const erroGeo = ref('')
const geocodificando = ref(false)
const mapaRef = ref(null)
const latitudeInput = ref('')
const longitudeInput = ref('')
const limparGeorreferencia = ref(false)
const resultadosGeo = ref([])

const formulario = reactive({
  nome: '',
  tipo: 'ubs',
  unidadeResponsavelId: '',
  bairro: '',
  endereco: '',
  apelidos: [],
  latitude: null,
  longitude: null,
  ativo: true
})

const temPonto = computed(
  () => formulario.latitude != null && formulario.longitude != null
)

function formatarCoord(n) {
  if (n == null || !Number.isFinite(n)) return ''
  return Number(n).toFixed(6)
}

function sincronizarInputsCoordenadas() {
  latitudeInput.value = formatarCoord(formulario.latitude)
  longitudeInput.value = formatarCoord(formulario.longitude)
}

function validarFaixa(lat, lng) {
  if (!Number.isFinite(lat) || !Number.isFinite(lng)) return false
  if (lat < -90 || lat > 90 || lng < -180 || lng > 180) return false
  return true
}

function definirCoordenadas(lat, lng) {
  limparGeorreferencia.value = false
  formulario.latitude = lat
  formulario.longitude = lng
  sincronizarInputsCoordenadas()
  nextTick(() => mapaRef.value?.invalidateSize?.())
}

function limparPonto() {
  limparGeorreferencia.value = true
  formulario.latitude = null
  formulario.longitude = null
  latitudeInput.value = ''
  longitudeInput.value = ''
  erroGeo.value = ''
  resultadosGeo.value = []
}

function aplicarCoordenadasDosInputs() {
  const lat = parseFloat(String(latitudeInput.value).replace(',', '.'))
  const lng = parseFloat(String(longitudeInput.value).replace(',', '.'))
  if (!latitudeInput.value.trim() && !longitudeInput.value.trim()) {
    limparPonto()
    return
  }
  if (!validarFaixa(lat, lng)) {
    erroGeo.value = 'Informe latitude (-90…90) e longitude (-180…180) válidas.'
    return
  }
  erroGeo.value = ''
  definirCoordenadas(lat, lng)
}

async function aoMoverMarcador({ latitude: lat, longitude: lng }) {
  definirCoordenadas(lat, lng)
  if (!formulario.endereco?.trim() || !formulario.bairro?.trim()) {
    try {
      const data = await atendimentosService.geocodeReverso(lat, lng)
      const rua = data.rua || data.logradouro
      if (!formulario.endereco?.trim() && rua) {
        const linha = [rua, data.numero].filter(Boolean).join(', ')
        if (linha) formulario.endereco = linha
      }
      if (!formulario.bairro?.trim() && data.bairro) {
        formulario.bairro = data.bairro
      }
    } catch {
      /* reverso opcional */
    }
  }
}

function selecionarResultadoGeo(item) {
  resultadosGeo.value = []
  definirCoordenadas(item.latitude, item.longitude)
  erroGeo.value = ''
}

async function localizarEnderecoNoMapa() {
  const endereco = formulario.endereco?.trim()
  const bairro = formulario.bairro?.trim()
  if (!endereco && !bairro) {
    erroGeo.value = 'Informe endereço ou bairro antes de localizar no mapa.'
    return
  }
  geocodificando.value = true
  erroGeo.value = ''
  resultadosGeo.value = []
  try {
    const resolvido = await resolverCoordenadasPorEndereco(
      { endereco: endereco || bairro, bairro },
      {
        buscarEndereco: (q) => atendimentosService.buscarEndereco(q),
        buscarCepComGeocoding
      }
    )
    if (!resolvido) {
      erroGeo.value =
        'Não encontramos esse endereço. Confira CEP e cidade, ou marque o ponto manualmente no mapa.'
      return
    }
    if (resolvido.multiplos?.length) {
      resultadosGeo.value = resolvido.multiplos
      erroGeo.value = 'Encontramos mais de um local. Escolha o correto na lista abaixo.'
      return
    }
    definirCoordenadas(resolvido.latitude, resolvido.longitude)
    if (resolvido.enderecoCompleto && !formulario.bairro?.trim()) {
      const partes = resolvido.enderecoCompleto.split(',')
      if (partes.length > 2) formulario.bairro = partes[1]?.trim() || formulario.bairro
    }
  } catch {
    erroGeo.value = 'Não foi possível localizar. Tente marcar o ponto no mapa.'
  } finally {
    geocodificando.value = false
  }
}

onMounted(() => {
  setTimeout(() => mapaRef.value?.invalidateSize?.(), 120)
  setTimeout(() => mapaRef.value?.invalidateSize?.(), 400)
})

watch(
  () => props.equipamento,
  (eq) => {
    erroForm.value = ''
    if (!eq) {
      formulario.nome = ''
      formulario.tipo = 'ubs'
      formulario.unidadeResponsavelId = ''
      formulario.bairro = ''
      formulario.endereco = ''
      formulario.apelidos = []
      formulario.latitude = null
      formulario.longitude = null
      formulario.ativo = true
      limparGeorreferencia.value = false
      sincronizarInputsCoordenadas()
      nextTick(() => mapaRef.value?.invalidateSize?.())
      return
    }
    formulario.nome = eq.nome || ''
    formulario.tipo = eq.tipo || 'ubs'
    formulario.unidadeResponsavelId = eq.unidadeResponsavelId || ''
    formulario.bairro = eq.bairro || ''
    formulario.endereco = eq.endereco || ''
    formulario.apelidos = [...(eq.apelidos || [])]
    formulario.latitude = eq.latitude ?? null
    formulario.longitude = eq.longitude ?? null
    formulario.ativo = eq.ativo !== false
    limparGeorreferencia.value = false
    sincronizarInputsCoordenadas()
    nextTick(() => {
      setTimeout(() => mapaRef.value?.invalidateSize?.(), 150)
    })
  },
  { immediate: true }
)

function onApelidoKeydown(e) {
  if (e.key === ',') {
    e.preventDefault()
    adicionarApelido()
  }
}

function adicionarApelido() {
  const texto = entradaApelido.value.trim().replace(/,$/, '')
  if (!texto) return
  if (!formulario.apelidos.includes(texto)) {
    formulario.apelidos.push(texto)
  }
  entradaApelido.value = ''
}

function removerApelido(index) {
  formulario.apelidos.splice(index, 1)
}

async function salvar() {
  erroForm.value = ''
  if (!formulario.nome.trim() || !formulario.unidadeResponsavelId) {
    erroForm.value = 'Preencha nome e secretaria responsável.'
    return
  }
  if (
    (formulario.latitude != null && formulario.longitude == null) ||
    (formulario.latitude == null && formulario.longitude != null)
  ) {
    erroForm.value = 'Informe latitude e longitude juntos, ou limpe o ponto.'
    return
  }

  salvando.value = true
  try {
    const payload = { ...formulario, limparGeorreferencia: limparGeorreferencia.value }
    if (props.equipamento?.id) {
      await adminStore.atualizarEquipamento(props.equipamento.id, payload)
    } else {
      await adminStore.criarEquipamento(payload)
    }
    emit('salvo')
    emit('fechar')
  } catch (err) {
    erroForm.value = getApiErrorMessage(err, 'Não foi possível salvar. Verifique os dados.')
  } finally {
    salvando.value = false
  }
}
</script>