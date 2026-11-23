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
import { reactive, ref, watch } from 'vue'
import { BuildingStorefrontIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { useAdminStore } from '@/stores/admin'
import { TIPOS_EQUIPAMENTO_PUBLICO } from '@/constants/equipamentosPublicos'
import { getApiErrorMessage } from '@/utils/apiError'

const props = defineProps({
  equipamento: { type: Object, default: null },
  unidadesAtivas: { type: Array, default: () => [] }
})

const emit = defineEmits(['fechar', 'salvo'])

const adminStore = useAdminStore()
const tituloId = `modal-equipamento-${Math.random().toString(36).slice(2, 8)}`
const entradaApelido = ref('')
const salvando = ref(false)
const erroForm = ref('')

const formulario = reactive({
  nome: '',
  tipo: 'ubs',
  unidadeResponsavelId: '',
  bairro: '',
  endereco: '',
  apelidos: [],
  ativo: true
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
      formulario.ativo = true
      return
    }
    formulario.nome = eq.nome || ''
    formulario.tipo = eq.tipo || 'ubs'
    formulario.unidadeResponsavelId = eq.unidadeResponsavelId || ''
    formulario.bairro = eq.bairro || ''
    formulario.endereco = eq.endereco || ''
    formulario.apelidos = [...(eq.apelidos || [])]
    formulario.ativo = eq.ativo !== false
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
  salvando.value = true
  try {
    const payload = { ...formulario }
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