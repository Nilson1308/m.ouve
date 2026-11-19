<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="aberto"
        class="fixed inset-0 bg-black/50 backdrop-blur-sm z-[100] flex items-center justify-center p-4"
        role="dialog"
        aria-modal="true"
        :aria-labelledby="tituloModalId"
        @click.self="fechar"
      >
        <Transition name="slide-up">
          <div
            v-if="aberto"
            class="bg-white dark:bg-gray-900 rounded-modal shadow-float dark:shadow-float-dark w-full max-w-2xl max-h-[90vh] overflow-hidden flex flex-col"
          >
            <!-- Header (padrão Despachar Protocolo) -->
            <div class="px-6 py-5 border-b border-primary-600/30 bg-gradient-to-r from-primary-500 to-primary-600">
              <div class="flex items-start justify-between gap-4">
                <div class="flex items-center gap-3 min-w-0">
                  <div class="w-12 h-12 bg-white/20 backdrop-blur-sm rounded-xl flex items-center justify-center shrink-0">
                    <DocumentTextIcon class="w-6 h-6 text-white" />
                  </div>
                  <div class="min-w-0">
                    <h2 :id="tituloModalId" class="text-xl sm:text-2xl font-bold text-white">
                      {{ modo === 'editar' ? 'Editar texto padrão' : 'Novo texto padrão' }}
                    </h2>
                    <p class="text-primary-100 text-sm mt-0.5">
                      Despacho técnico · Formalização setorial
                    </p>
                  </div>
                </div>
                <button
                  type="button"
                  class="text-white/80 hover:text-white transition-colors p-2 rounded-lg hover:bg-white/10 shrink-0"
                  aria-label="Fechar"
                  @click="fechar"
                >
                  <XMarkIcon class="w-6 h-6" />
                </button>
              </div>
            </div>

            <!-- Body -->
            <form class="flex-1 overflow-y-auto p-6 space-y-5" @submit.prevent="salvar">
              <div
                v-if="unidadeLabel"
                class="card bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900 border-2 border-primary-200 dark:border-primary-800"
              >
                <div class="flex items-center gap-3">
                  <div class="w-12 h-12 rounded-xl bg-primary-500 text-white flex items-center justify-center shrink-0">
                    <BuildingOffice2Icon class="w-6 h-6" />
                  </div>
                  <div>
                    <p class="text-xs font-medium text-gray-500 dark:text-gray-400 uppercase tracking-wide">
                      Secretaria
                    </p>
                    <p class="text-base font-semibold text-gray-900 dark:text-white">
                      {{ unidadeLabel }}
                    </p>
                  </div>
                </div>
              </div>

              <div class="alert-info">
                <InformationCircleIcon class="w-5 h-5 flex-shrink-0" />
                <div>
                  <strong class="font-semibold">Modelos de despacho oficial</strong>
                  <p class="text-sm mt-1">
                    Os textos cadastrados aparecem no select <strong>Despacho Técnico Oficial</strong>
                    ao formalizar ordens de serviço, com validade da assinatura eletrônica simples.
                  </p>
                </div>
              </div>

              <div v-if="modo === 'editar' && item" class="card border-l-4 border-primary-500 p-4">
                <p class="text-xs text-gray-500 dark:text-gray-400 mb-1">Editando</p>
                <p class="font-semibold text-gray-900 dark:text-white">{{ item.titulo }}</p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Título identificador *
                </label>
                <input
                  v-model="form.titulo"
                  type="text"
                  class="input-field"
                  maxlength="120"
                  placeholder="Ex.: Asfalto frio CBUQ"
                  required
                />
                <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                  Nome curto na lista de seleção da formalização
                </p>
              </div>

              <div>
                <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
                  Texto do despacho técnico *
                </label>
                <Editor
                  v-model="form.texto"
                  :mostrar-contagem="true"
                  placeholder="Descreva o despacho que será gravado na formalização da OS..."
                />
              </div>

              <label
                class="flex items-start gap-3 cursor-pointer card p-4 border-2 transition-colors"
                :class="
                  form.ativo
                    ? 'border-green-200 dark:border-green-800 bg-green-50/50 dark:bg-green-900/10'
                    : 'border-gray-200 dark:border-gray-600'
                "
              >
                <input
                  v-model="form.ativo"
                  type="checkbox"
                  class="mt-0.5 w-5 h-5 rounded text-primary-600 focus:ring-primary-500"
                />
                <span class="text-sm text-gray-800 dark:text-gray-200">
                  <strong class="text-gray-900 dark:text-white">Texto ativo</strong>
                  <span class="block text-gray-600 dark:text-gray-400 mt-0.5">
                    Disponível para gestores na formalização de ordens de serviço
                  </span>
                </span>
              </label>
            </form>

            <!-- Footer -->
            <div class="px-6 py-4 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-800">
              <div class="flex flex-col-reverse sm:flex-row sm:items-center sm:justify-between gap-3">
                <button type="button" class="btn-secondary" :disabled="salvando" @click="fechar">
                  Cancelar
                </button>
                <button
                  type="button"
                  class="btn-primary flex items-center justify-center gap-2 w-full sm:w-auto"
                  :class="{ 'opacity-50 cursor-not-allowed': !formValido || salvando }"
                  :disabled="!formValido || salvando"
                  @click="salvar"
                >
                  <CheckCircleIcon class="w-5 h-5" />
                  {{ salvando ? 'Salvando…' : modo === 'editar' ? 'Salvar alterações' : 'Criar texto padrão' }}
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import {
  XMarkIcon,
  DocumentTextIcon,
  BuildingOffice2Icon,
  InformationCircleIcon,
  CheckCircleIcon
} from '@heroicons/vue/24/outline'
import Editor from '@/components/shared/Editor.vue'

const props = defineProps({
  aberto: Boolean,
  modo: {
    type: String,
    default: 'criar'
  },
  item: {
    type: Object,
    default: null
  },
  salvando: Boolean,
  unidadeLabel: {
    type: String,
    default: ''
  }
})

const emit = defineEmits(['fechar', 'salvar'])

const tituloModalId = 'texto-padrao-modal-titulo'

const form = ref({
  titulo: '',
  texto: '',
  ativo: true
})

const formValido = computed(() => {
  return form.value.titulo.trim().length > 0 && form.value.texto.trim().length > 0
})

watch(
  () => [props.aberto, props.item, props.modo],
  () => {
    if (!props.aberto) return
    if (props.modo === 'editar' && props.item) {
      form.value = {
        titulo: props.item.titulo,
        texto: props.item.texto,
        ativo: props.item.ativo
      }
    } else {
      form.value = { titulo: '', texto: '', ativo: true }
    }
  },
  { immediate: true }
)

function fechar() {
  emit('fechar')
}

function salvar() {
  if (!formValido.value) return
  emit('salvar', {
    titulo: form.value.titulo.trim(),
    texto: form.value.texto.trim(),
    ativo: form.value.ativo
  })
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

.slide-up-enter-active,
.slide-up-leave-active {
  transition: all 0.3s ease;
}

.slide-up-enter-from {
  opacity: 0;
  transform: translateY(20px) scale(0.98);
}

.slide-up-leave-to {
  opacity: 0;
  transform: translateY(10px) scale(0.98);
}

.input-field {
  @apply w-full px-3 py-2 border border-gray-300 dark:border-gray-600 rounded-input;
  @apply bg-white dark:bg-gray-700 text-gray-900 dark:text-white;
  @apply placeholder-gray-500 dark:placeholder-gray-400;
  @apply focus:ring-2 focus:ring-primary-500 focus:border-transparent;
  @apply transition-all duration-200;
}
</style>
