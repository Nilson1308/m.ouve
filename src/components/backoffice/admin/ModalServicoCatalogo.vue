<template>
  <Transition
    enter-active-class="transition-opacity duration-300"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-300"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto"
      @click.self="$emit('fechar')"
    >
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-4xl my-8 overflow-hidden">
          <div class="bg-gradient-to-r from-cyan-600 to-primary-600 px-6 py-5 flex items-start justify-between gap-4">
            <div>
              <h2 class="text-xl font-bold text-white">
                {{ servico ? 'Editar Serviço' : 'Novo Serviço no Catálogo' }}
              </h2>
              <p class="text-cyan-100 text-sm mt-0.5">Form Builder — sem JSON manual</p>
            </div>
            <button type="button" class="p-2 hover:bg-white/20 rounded-lg" @click="$emit('fechar')">
              <XMarkIcon class="w-6 h-6 text-white" />
            </button>
          </div>

          <!-- Abas internas -->
          <div class="border-b border-gray-200 dark:border-gray-700 px-6 pt-4 flex gap-6">
            <button
              v-for="tab in abasInternas"
              :key="tab.id"
              type="button"
              :class="[
                'pb-3 text-sm font-semibold border-b-2 transition-colors',
                abaInterna === tab.id
                  ? 'border-primary-500 text-primary-600 dark:text-primary-400'
                  : 'border-transparent text-gray-500 hover:text-gray-700 dark:text-gray-400'
              ]"
              @click="abaInterna = tab.id"
            >
              {{ tab.label }}
            </button>
          </div>

          <form class="p-6 max-h-[70vh] overflow-y-auto space-y-6" @submit.prevent="salvar">
            <!-- Dados básicos -->
            <div v-show="abaInterna === 'dados'" class="space-y-4">
              <div>
                <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Nome *</label>
                <input v-model="form.nome" type="text" required class="input" placeholder="Ex.: Tapa Buraco" />
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Descrição</label>
                <textarea
                  v-model="form.descricao"
                  rows="3"
                  class="input resize-none"
                  placeholder="Texto exibido ao cidadão"
                />
              </div>
              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Ícone (app)</label>
                  <input v-model="form.icone" type="text" class="input font-mono text-sm" placeholder="ex.: wrench ou URL" />
                </div>
                <div>
                  <SlaUnidadeInput v-model="form.sla_padrao_horas" label="SLA padrão *" />
                </div>
              </div>
              <div>
                <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Unidade responsável</label>
                <select v-model="form.unidade_responsavel_id" class="input">
                  <option value="">Selecione a secretaria padrão...</option>
                  <option v-for="u in unidades" :key="u.id" :value="u.id">
                    {{ u.sigla ? `${u.sigla} — ` : '' }}{{ u.nome }}
                  </option>
                </select>
              </div>
              <label class="flex items-center gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 cursor-pointer">
                <input v-model="form.ativo" type="checkbox" class="w-4 h-4 rounded text-primary-600" />
                <span class="text-sm font-semibold text-gray-900 dark:text-white">Serviço ativo no catálogo</span>
              </label>
            </div>

            <!-- Form builder -->
            <div v-show="abaInterna === 'formulario'" class="space-y-4">
              <div class="flex items-center justify-between gap-4">
                <p class="text-sm text-gray-600 dark:text-gray-400">
                  Monte os campos que o cidadão preencherá no aplicativo.
                  <span class="hidden sm:inline text-gray-500">Arraste pelo ícone ≡ para reordenar.</span>
                </p>
                <button
                  type="button"
                  class="inline-flex items-center gap-2 px-3 py-2 bg-primary-600 hover:bg-primary-700 text-white text-sm font-medium rounded-lg shadow-button"
                  @click="adicionarCampo"
                >
                  <PlusCircleIcon class="w-5 h-5" />
                  Adicionar Campo
                </button>
              </div>

              <div v-if="campos.length === 0" class="card p-8 text-center border-2 border-dashed border-gray-200 dark:border-gray-600">
                <QueueListIcon class="w-10 h-10 mx-auto text-gray-400 mb-2" />
                <p class="text-sm text-gray-500">Nenhum campo. Clique em &quot;Adicionar Campo&quot;.</p>
              </div>

              <div
                v-for="(campo, index) in campos"
                :key="campo._id"
                class="relative rounded-xl border-2 bg-gradient-to-br from-gray-50 to-white dark:from-gray-800 dark:to-gray-800/80 p-4 shadow-sm hover:shadow-md transition-all"
                :class="[
                  dragFromIndex === index ? 'opacity-60 scale-[0.99]' : '',
                  dragOverIndex === index && dragFromIndex !== index
                    ? 'border-primary-400 ring-2 ring-primary-400/40'
                    : 'border-gray-200 dark:border-gray-600'
                ]"
                @dragover.prevent="onDragOver(index)"
                @dragleave="onDragLeave(index)"
                @drop.prevent="onDrop(index)"
              >
                <button
                  type="button"
                  class="absolute left-2 top-2 p-1.5 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-200/80 dark:hover:bg-gray-700 cursor-grab active:cursor-grabbing touch-none hidden sm:flex"
                  title="Arrastar para reordenar"
                  draggable="true"
                  aria-label="Arrastar para reordenar campo"
                  @dragstart="onDragStart(index, $event)"
                  @dragend="onDragEnd"
                >
                  <Bars3Icon class="w-5 h-5 pointer-events-none" aria-hidden="true" />
                </button>

                <div class="grid grid-cols-1 md:grid-cols-12 gap-4 pl-0 sm:pl-8">
                  <div class="md:col-span-5">
                    <label class="text-xs font-semibold text-gray-500 uppercase">Rótulo (Label)</label>
                    <input
                      v-model="campo.label"
                      type="text"
                      class="input mt-1"
                      placeholder="Ex.: Foto do Buraco"
                      @input="sugerirName(campo, index)"
                    />
                  </div>
                  <div class="md:col-span-3">
                    <label class="text-xs font-semibold text-gray-500 uppercase">Nome (name)</label>
                    <input
                      v-model="campo.name"
                      type="text"
                      class="input mt-1 font-mono text-sm"
                      @input="campo.nameManual = true"
                    />
                  </div>
                  <div class="md:col-span-3">
                    <label class="text-xs font-semibold text-gray-500 uppercase">Tipo</label>
                    <select v-model="campo.type" class="input mt-1">
                      <option v-for="t in TIPOS_CAMPO_UI" :key="t.value" :value="t.value">
                        {{ t.label }}
                      </option>
                    </select>
                  </div>
                  <div class="md:col-span-1 flex items-end justify-end pb-1">
                    <button
                      type="button"
                      class="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
                      title="Remover campo"
                      @click="removerCampo(index)"
                    >
                      <TrashIcon class="w-5 h-5" />
                    </button>
                  </div>
                </div>

                <div v-if="campo.type === 'select'" class="mt-3 pl-0 sm:pl-8">
                  <label class="text-xs font-semibold text-gray-500 uppercase">Opções (separadas por vírgula)</label>
                  <input
                    v-model="campo.optionsText"
                    type="text"
                    class="input mt-1"
                    placeholder="Baixa, Média, Alta"
                  />
                </div>

                <div class="mt-3 pl-0 sm:pl-8 flex items-center gap-2">
                  <button
                    type="button"
                    role="switch"
                    :aria-checked="campo.required"
                    :class="[
                      'relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors',
                      campo.required ? 'bg-primary-600' : 'bg-gray-300 dark:bg-gray-600'
                    ]"
                    @click="campo.required = !campo.required"
                  >
                    <span
                      :class="[
                        'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow transition',
                        campo.required ? 'translate-x-5' : 'translate-x-0'
                      ]"
                    />
                  </button>
                  <span class="text-sm text-gray-700 dark:text-gray-300">Obrigatório</span>
                </div>
              </div>
            </div>

            <div class="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button type="button" class="btn-secondary" @click="$emit('fechar')">Cancelar</button>
              <button type="submit" class="btn-primary" :disabled="salvando || !formValido">
                {{ salvando ? 'Salvando...' : 'Salvar Serviço' }}
              </button>
            </div>
          </form>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  XMarkIcon,
  PlusCircleIcon,
  TrashIcon,
  QueueListIcon,
  Bars3Icon
} from '@heroicons/vue/24/outline'
import { TIPOS_CAMPO_UI, labelParaName, schemaParaCamposUi } from '@/utils/catalogoMappers'
import SlaUnidadeInput from '@/components/backoffice/catalogo/SlaUnidadeInput.vue'

const props = defineProps({
  servico: { type: Object, default: null },
  unidades: { type: Array, default: () => [] }
})

const emit = defineEmits(['fechar', 'salvar'])

const abasInternas = [
  { id: 'dados', label: 'Dados Básicos' },
  { id: 'formulario', label: 'Campos do Formulário' }
]
const abaInterna = ref('dados')
const salvando = ref(false)

const form = ref({
  nome: '',
  descricao: '',
  icone: '',
  sla_padrao_horas: 72,
  unidade_responsavel_id: '',
  ativo: true
})

const campos = ref([])
const dragFromIndex = ref(null)
const dragOverIndex = ref(null)

const formValido = computed(() => {
  return Boolean(form.value.nome?.trim()) && form.value.sla_padrao_horas > 0
})

function novoCampo() {
  return {
    _id: `campo-${Date.now()}-${Math.random().toString(36).slice(2, 7)}`,
    label: '',
    name: '',
    nameManual: false,
    type: 'text',
    required: false,
    optionsText: '',
    placeholder: ''
  }
}

function adicionarCampo() {
  campos.value.push(novoCampo())
}

function removerCampo(index) {
  campos.value.splice(index, 1)
}

function limparDrag() {
  dragFromIndex.value = null
  dragOverIndex.value = null
}

function onDragStart(index, event) {
  dragFromIndex.value = index
  event.dataTransfer.effectAllowed = 'move'
  event.dataTransfer.setData('text/plain', String(index))
}

function onDragOver(index) {
  if (dragFromIndex.value === null) return
  dragOverIndex.value = index
}

function onDragLeave(index) {
  if (dragOverIndex.value === index) {
    dragOverIndex.value = null
  }
}

function onDrop(index) {
  const from = dragFromIndex.value
  if (from === null || from === index) {
    limparDrag()
    return
  }
  const lista = [...campos.value]
  const [item] = lista.splice(from, 1)
  lista.splice(index, 0, item)
  campos.value = lista
  limparDrag()
}

function onDragEnd() {
  limparDrag()
}

function sugerirName(campo, index) {
  if (campo.nameManual) return
  const usados = new Set(
    campos.value.filter((_, i) => i !== index).map((c) => c.name).filter(Boolean)
  )
  campo.name = labelParaName(campo.label, usados)
}

watch(
  () => props.servico,
  (servico) => {
    if (servico) {
      form.value = {
        nome: servico.nome || '',
        descricao: servico.descricao || '',
        icone: servico.icone || '',
        sla_padrao_horas: servico.sla_padrao_horas ?? 72,
        unidade_responsavel_id: servico.unidade_responsavel_id || '',
        ativo: servico.ativo !== false
      }
      campos.value = schemaParaCamposUi(servico.formulario_schema)
    } else {
      form.value = {
        nome: '',
        descricao: '',
        icone: '',
        sla_padrao_horas: 72,
        unidade_responsavel_id: '',
        ativo: true
      }
      campos.value = []
    }
    abaInterna.value = 'dados'
  },
  { immediate: true }
)

async function salvar() {
  if (!formValido.value) return
  salvando.value = true
  try {
    emit('salvar', { form: { ...form.value }, campos: campos.value })
  } finally {
    salvando.value = false
  }
}
</script>