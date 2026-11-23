<!--
  ⚠️ ARQUIVO ARQUIVADO (Nov 2026)
  Esta view foi substituída pela interface conversacional ChatSolicitacaoView.vue
  Mantida apenas para referência histórica do paradigma de "formulário tradicional"
-->
<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-950 dark:to-gray-900 high-contrast:from-black high-contrast:to-black pb-32">
    <!-- Header -->
    <header class="sticky top-0 z-20 backdrop-blur-xl bg-white/80 dark:bg-gray-900/80 high-contrast:bg-black border-b border-gray-200/50 dark:border-gray-800/50 high-contrast:border-yellow-300 shadow-soft">
      <div class="px-6 py-4 safe-area-inset flex items-center gap-4">
        <button @click="voltar" class="btn-icon">
          <ChevronLeftIcon class="w-6 h-6" />
        </button>
        <div class="flex-1">
          <h1 class="text-lg font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300">
            {{ servico?.nome || 'Carregando...' }}
          </h1>
          <p class="text-xs text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold">
            {{ categoriaLabel }}
          </p>
        </div>
        
        <!-- Badge SLA -->
        <span v-if="servico" class="inline-flex items-center gap-1 px-3 py-1.5 rounded-badge text-xs font-semibold bg-blue-50 dark:bg-blue-900/20 high-contrast:bg-transparent text-blue-700 dark:text-blue-300 high-contrast:text-yellow-300 border border-blue-200 dark:border-blue-800 high-contrast:border-yellow-300">
          <ClockIcon class="w-4 h-4" />
          {{ formatarSLA(servico.sla_horas) }}
        </span>
      </div>
    </header>

    <!-- Main Content -->
    <main class="px-6 py-8 space-y-6 animate-fade-in">
      <!-- Loading State -->
      <div v-if="carregandoFormulario || !servico" class="flex flex-col items-center justify-center py-20">
        <div class="animate-spin rounded-full h-16 w-16 border-4 border-primary-500 border-t-transparent mb-4"></div>
        <p class="text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold">
          Carregando formulário...
        </p>
      </div>

      <!-- Formulário Dinâmico -->
      <form v-else @submit.prevent="enviarSolicitacao" class="space-y-6">
        <!-- Info do Serviço -->
        <div class="card bg-gradient-to-br from-blue-50 to-blue-100 dark:from-blue-900/20 dark:to-blue-800/10 high-contrast:bg-transparent border-blue-200 dark:border-blue-800 high-contrast:border-yellow-300">
          <div class="flex items-start gap-3">
            <InformationCircleIcon class="w-6 h-6 flex-shrink-0 text-blue-600 dark:text-blue-400 high-contrast:text-yellow-300" />
            <div class="flex-1">
              <h3 class="font-bold text-blue-900 dark:text-blue-100 high-contrast:text-yellow-300 mb-1">
                Sobre este serviço
              </h3>
              <p class="text-sm text-blue-800 dark:text-blue-200 high-contrast:text-white high-contrast:font-bold">
                {{ servico.descricao }}
              </p>
            </div>
          </div>
        </div>

        <!-- Campos Dinâmicos do JSON Schema -->
        <div 
          v-for="(propConfig, propName) in schemaProperties" 
          :key="propName"
          class="card"
        >
          <label :for="propName" class="block text-base font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 mb-3">
            {{ propConfig.title || propName }}
            <span v-if="isRequired(propName)" class="text-red-500">*</span>
          </label>

          <!-- Lookup: unidades administrativas -->
          <PwaFieldLookupUnidades
            v-if="isLookupUnidades(propConfig)"
            v-model="dadosDinamicos[propName]"
            :required="isRequired(propName)"
            :label="null"
            :input-id="String(propName)"
          />

          <PwaFieldLookupEquipamentos
            v-else-if="isLookupEquipamentos(propConfig)"
            v-model="dadosDinamicos[propName]"
            :required="isRequired(propName)"
            :label="null"
            :input-id="String(propName)"
            :filtro-datasource="propConfig['x-ouvia-datasource-filter'] || {}"
          />

          <!-- Input type="text" -->
          <input 
            v-else-if="propConfig.type === 'string' && !propConfig.format && !propConfig.enum"
            :id="propName"
            v-model="dadosDinamicos[propName]"
            type="text"
            :required="isRequired(propName)"
            :pattern="propConfig.pattern"
            class="input"
            :placeholder="propConfig.title || ''"
          />

          <!-- Textarea -->
          <div v-else-if="propConfig.type === 'string' && propConfig.format === 'textarea'" class="relative">
            <textarea 
              :id="propName"
              v-model="dadosDinamicos[propName]"
              rows="5"
              :required="isRequired(propName)"
              :minlength="propConfig.minLength"
              class="input resize-none pr-14"
              :placeholder="propConfig.title || ''"
            ></textarea>
            
            <!-- Botão de Áudio -->
            <button 
              type="button"
              @click="toggleGravacao(propName)"
              :class="[
                'absolute right-3 bottom-3 w-10 h-10 rounded-full flex items-center justify-center transition-all shadow-button',
                gravandoCampo === propName
                  ? 'bg-red-500 text-white animate-pulse' 
                  : 'bg-primary-600 dark:bg-primary-500 high-contrast:bg-yellow-300 text-white high-contrast:text-black hover:bg-primary-700 dark:hover:bg-primary-600 hover:scale-110'
              ]"
            >
              <MicrophoneIcon v-if="gravandoCampo !== propName" class="w-5 h-5" />
              <StopIcon v-else class="w-5 h-5" />
            </button>
            
            <p v-if="gravandoCampo === propName" class="text-sm text-red-600 dark:text-red-400 high-contrast:text-red-500 high-contrast:font-bold mt-2 flex items-center gap-2 animate-pulse">
              <span class="w-2 h-2 bg-red-600 rounded-full"></span>
              Gravando áudio...
            </p>
            
            <!-- Contador de caracteres -->
            <div v-if="propConfig.minLength" class="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold mt-2">
              <span>{{ (dadosDinamicos[propName] || '').length }} / {{ propConfig.minLength }} caracteres mínimos</span>
            </div>
          </div>

          <!-- Select (enum) -->
          <select 
            v-else-if="propConfig.enum"
            :id="propName"
            v-model="dadosDinamicos[propName]"
            :required="isRequired(propName)"
            class="input"
          >
            <option value="">Selecione uma opção</option>
            <option 
              v-for="(enumValue, index) in propConfig.enum" 
              :key="enumValue"
              :value="enumValue"
            >
              {{ propConfig.enumNames?.[index] || enumValue }}
            </option>
          </select>

          <!-- Checkbox (boolean) -->
          <div v-else-if="propConfig.type === 'boolean'" class="flex items-start gap-3 p-4 rounded-button bg-gray-50 dark:bg-gray-800 high-contrast:bg-transparent high-contrast:border-2 high-contrast:border-gray-600">
            <input 
              :id="propName"
              v-model="dadosDinamicos[propName]"
              type="checkbox"
              class="w-5 h-5 rounded border-2 border-gray-300 dark:border-gray-600 text-primary-600 focus:ring-4 focus:ring-primary-200 dark:focus:ring-primary-800 high-contrast:border-yellow-300"
            />
            <label :for="propName" class="flex-1 text-sm text-gray-700 dark:text-gray-300 high-contrast:text-white high-contrast:font-bold cursor-pointer">
              {{ propConfig.title || propName }}
            </label>
          </div>

          <!-- Number/Integer -->
          <input 
            v-else-if="propConfig.type === 'integer' || propConfig.type === 'number'"
            :id="propName"
            v-model.number="dadosDinamicos[propName]"
            :type="propConfig.type === 'integer' ? 'number' : 'number'"
            :required="isRequired(propName)"
            :min="propConfig.minimum"
            :max="propConfig.maximum"
            :step="propConfig.type === 'integer' ? 1 : 'any'"
            class="input"
            :placeholder="propConfig.title || ''"
          />
        </div>

        <!-- Campos Universais: Localização (se exigido) -->
        <div v-if="exigeLocalizacao" class="card">
          <div class="flex items-center justify-between mb-3">
            <label class="text-base font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 flex items-center gap-2">
              <MapPinIcon class="w-5 h-5" />
              Localização do Problema *
            </label>
            <button 
              type="button"
              @click="capturarLocalizacao"
              :disabled="capturandoGPS"
              class="text-sm text-primary-600 dark:text-primary-400 high-contrast:text-yellow-300 hover:text-primary-700 font-semibold flex items-center gap-1 disabled:opacity-50 transition-all hover:scale-105"
            >
              <MapPinIcon class="w-4 h-4" />
              {{ capturandoGPS ? 'Localizando...' : 'Usar GPS' }}
            </button>
          </div>

          <input 
            v-model="enderecoTexto"
            type="text"
            required
            class="input"
            placeholder="Digite o endereço ou use o GPS"
          />

          <!-- Mapa -->
          <div v-if="localizacao" class="mt-4 relative h-48 bg-gray-200 dark:bg-gray-700 high-contrast:bg-gray-900 high-contrast:border-2 high-contrast:border-yellow-300 rounded-card overflow-hidden shadow-inner-soft">
            <div class="absolute inset-0 flex items-center justify-center">
              <div class="text-center">
                <div class="w-12 h-12 bg-red-500 high-contrast:bg-yellow-300 rounded-full mx-auto mb-2 flex items-center justify-center shadow-button animate-bounce">
                  <MapPinIcon class="w-6 h-6 text-white high-contrast:text-black" />
                </div>
                <p class="text-sm font-semibold text-gray-900 dark:text-white high-contrast:text-yellow-300 px-4">
                  {{ enderecoTexto }}
                </p>
                <p class="text-xs text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold mt-1">
                  {{ localizacao.latitude.toFixed(6) }}, {{ localizacao.longitude.toFixed(6) }}
                </p>
              </div>
            </div>
          </div>
        </div>

        <!-- Campos Universais: Upload de Fotos -->
        <div class="card">
          <label class="text-base font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 mb-3 block flex items-center gap-2">
            <CameraIcon class="w-5 h-5" />
            Fotos {{ exigeLocalizacao ? '(Opcional)' : '' }}
          </label>

          <!-- Preview -->
          <div v-if="imagensPreviews.length > 0" class="grid grid-cols-3 gap-3 mb-4">
            <div 
              v-for="(preview, index) in imagensPreviews" 
              :key="index"
              class="relative aspect-square bg-gray-200 dark:bg-gray-700 high-contrast:bg-gray-900 high-contrast:border-2 high-contrast:border-yellow-300 rounded-card overflow-hidden group"
            >
              <img :src="preview" alt="Preview" class="w-full h-full object-cover" />
              <button 
                type="button"
                @click="removerImagem(index)"
                class="absolute top-1 right-1 w-7 h-7 bg-red-500 high-contrast:bg-yellow-300 text-white high-contrast:text-black rounded-full opacity-0 group-hover:opacity-100 transition-all flex items-center justify-center font-bold hover:scale-110 shadow-button"
              >
                ×
              </button>
            </div>
          </div>

          <!-- Botões -->
          <div class="grid grid-cols-2 gap-3">
            <label class="btn-secondary cursor-pointer text-center group">
              <CameraIcon class="w-5 h-5 group-hover:scale-110 transition-transform" />
              Tirar Foto
              <input type="file" accept="image/*" capture="environment" @change="handleImageCapture" class="hidden" />
            </label>

            <label class="btn-secondary cursor-pointer text-center group">
              <PhotoIcon class="w-5 h-5 group-hover:scale-110 transition-transform" />
              Galeria
              <input type="file" accept="image/*" multiple @change="handleImageUpload" class="hidden" />
            </label>
          </div>
        </div>
      </form>
    </main>

    <!-- Bottom Bar Fixo -->
    <div class="fixed bottom-0 left-0 right-0 bg-white/80 dark:bg-gray-900/80 high-contrast:bg-black backdrop-blur-xl border-t border-gray-200 dark:border-gray-800 high-contrast:border-yellow-300 p-6 safe-area-inset-bottom z-30 shadow-float-dark">
      <button 
        @click="enviarSolicitacao"
        :disabled="!podeEnviar || protocolosStore.loading"
        class="w-full btn-success shadow-glow-green group"
      >
        <PaperAirplaneIcon class="w-5 h-5 group-hover:translate-x-1 transition-transform" />
        <span class="font-bold">{{ protocolosStore.loading ? 'Enviando...' : 'Enviar Solicitação' }}</span>
      </button>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { useCatalogoStore } from '@/stores/catalogo'
import { nomeCategoriaServico } from '@/utils/catalogo'
import { useProtocolosStore } from '@/stores/protocolos'
import { useDialog } from '@/composables/useDialog'
import PwaFieldLookupUnidades from '@/components/pwa/PwaFieldLookupUnidades.vue'
import PwaFieldLookupEquipamentos from '@/components/pwa/PwaFieldLookupEquipamentos.vue'
import { useCatalogoLookup } from '@/composables/useCatalogoLookup'
import {
  ChevronLeftIcon,
  ClockIcon,
  InformationCircleIcon,
  MicrophoneIcon,
  StopIcon,
  MapPinIcon,
  CameraIcon,
  PhotoIcon,
  PaperAirplaneIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const route = useRoute()
const catalogoStore = useCatalogoStore()
const protocolosStore = useProtocolosStore()
const { success, error: showError } = useDialog()
const { isLookupUnidades, isLookupEquipamentos } = useCatalogoLookup()

const servicoId = computed(() => route.params.servicoId)
const carregandoFormulario = ref(true)

const servico = computed(() => {
  const id = servicoId.value
  const encontrado = catalogoStore.getServicoPorId(id)
  if (encontrado) return encontrado

  const selecionado = catalogoStore.servicoSelecionado
  if (selecionado && String(selecionado.id) === String(id)) {
    return selecionado
  }

  return null
})
const categoriaLabel = computed(() => nomeCategoriaServico(servico.value))
const schemaProperties = computed(() => servico.value?.schema_formulario?.properties || {})
const requiredFields = computed(() => servico.value?.schema_formulario?.required || [])
const exigeLocalizacao = computed(() => {
  if (servico.value?.exige_localizacao === true) return true
  const metadata = servico.value?.schema_formulario?.$metadata || {}
  return metadata.exige_localizacao === true
})

const dadosDinamicos = ref({})
const enderecoTexto = ref('')
const localizacao = ref(null)
const imagensPreviews = ref([])
const imagensFiles = ref([])
const gravandoCampo = ref(null)
const capturandoGPS = ref(false)

const podeEnviar = computed(() => {
  if (!servico.value) return false

  const camposObrigatoriosPreenchidos = requiredFields.value.every((field) => {
    const valor = dadosDinamicos.value[field]
    const prop = schemaProperties.value[field]

    if (prop?.type === 'boolean') {
      return typeof valor === 'boolean'
    }

    if (prop?.type === 'integer' || prop?.type === 'number') {
      return valor !== undefined && valor !== null && valor !== ''
    }

    return valor !== undefined && valor !== null && String(valor).trim() !== ''
  })

  const localizacaoOk =
    !exigeLocalizacao.value ||
    (String(enderecoTexto.value).trim() !== '' && localizacao.value)

  return camposObrigatoriosPreenchidos && localizacaoOk
})

function aplicarDefaultsSchema() {
  if (!servico.value) return

  Object.entries(schemaProperties.value).forEach(([key, config]) => {
    if (dadosDinamicos.value[key] !== undefined) return

    if (config.type === 'boolean') {
      dadosDinamicos.value[key] = config.default ?? false
      return
    }

    if (config.default !== undefined) {
      dadosDinamicos.value[key] = config.default
    }
  })
}

watch(servico, (atual) => {
  if (atual) aplicarDefaultsSchema()
})

onMounted(async () => {
  try {
    if (catalogoStore.servicos.length === 0) {
      const { success } = await catalogoStore.carregarCatalogo()
      if (!success) {
        showError(catalogoStore.error || 'Não foi possível carregar o catálogo')
        router.push('/nova-solicitacao')
        return
      }
    }

    if (!servico.value) {
      showError('Serviço não encontrado no catálogo')
      router.push('/nova-solicitacao')
      return
    }

    aplicarDefaultsSchema()
  } finally {
    carregandoFormulario.value = false
  }
})

function voltar() {
  router.back()
}

function isRequired(fieldName) {
  return requiredFields.value.includes(fieldName)
}

function formatarSLA(horas) {
  if (horas < 24) return `${horas}h`
  const dias = Math.floor(horas / 24)
  return `${dias} ${dias === 1 ? 'dia' : 'dias'}`
}

function toggleGravacao(campo) {
  gravandoCampo.value = gravandoCampo.value === campo ? null : campo
  
  if (gravandoCampo.value) {
    setTimeout(() => {
      const transcricao = ' [Áudio transcrito: conteúdo simulado do áudio]'
      dadosDinamicos.value[campo] = (dadosDinamicos.value[campo] || '') + transcricao
      gravandoCampo.value = null
    }, 3000)
  }
}

function capturarLocalizacao() {
  capturandoGPS.value = true
  
  // Simula captura de GPS
  setTimeout(() => {
    localizacao.value = {
      latitude: -23.5505 + (Math.random() - 0.5) * 0.01,
      longitude: -46.6333 + (Math.random() - 0.5) * 0.01
    }
    
    if (!enderecoTexto.value) {
      enderecoTexto.value = 'Rua Exemplo, 100 - Centro'
    }
    
    capturandoGPS.value = false
  }, 1500)
}

function handleImageCapture(event) {
  handleImageFiles(event.target.files)
}

function handleImageUpload(event) {
  handleImageFiles(event.target.files)
}

function handleImageFiles(files) {
  Array.from(files).forEach(file => {
    if (file.type.startsWith('image/')) {
      imagensFiles.value.push(file)
      
      const reader = new FileReader()
      reader.onload = (e) => {
        imagensPreviews.value.push(e.target.result)
      }
      reader.readAsDataURL(file)
    }
  })
}

function removerImagem(index) {
  imagensPreviews.value.splice(index, 1)
  imagensFiles.value.splice(index, 1)
}

async function enviarSolicitacao() {
  if (!podeEnviar.value) {
    showError('Por favor, preencha todos os campos obrigatórios')
    return
  }

  const payload = {
    servico_id: String(servicoId.value),
    dados_dinamicos: dadosDinamicos.value,
    endereco_texto: enderecoTexto.value || null,
    localizacao: localizacao.value ? {
      latitude: localizacao.value.latitude,
      longitude: localizacao.value.longitude
    } : null,
    anexos: imagensFiles.value.map((f, i) => `foto_${i + 1}.jpg`)
  }

  const result = await protocolosStore.criarSolicitacaoDinamica(payload)

  if (result.success) {
    success(`Solicitação enviada! Protocolo: ${result.protocolo.codigo}`)
    router.push('/app/dashboard')
  } else {
    showError(result.error || 'Erro ao enviar solicitação')
  }
}
</script>
