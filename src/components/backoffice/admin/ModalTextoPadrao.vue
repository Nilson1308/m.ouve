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
      v-if="aberto"
      class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto"
      @click.self="fechar"
    >
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-2xl my-8 overflow-hidden">
          <div class="bg-gradient-to-r from-primary-600 to-primary-500 px-6 py-5 flex items-start justify-between gap-4">
            <div class="flex items-center gap-3 min-w-0">
              <DocumentTextIcon class="w-7 h-7 text-white shrink-0" />
              <div>
                <h2 class="text-xl font-bold text-white">
                  {{ modo === 'editar' ? 'Editar texto padrão' : 'Novo texto padrão' }}
                </h2>
                <p class="text-primary-100 text-sm mt-0.5">Despacho técnico · formalização setorial</p>
              </div>
            </div>
            <button type="button" class="p-2 hover:bg-white/20 rounded-lg" aria-label="Fechar" @click="fechar">
              <XMarkIcon class="w-6 h-6 text-white" />
            </button>
          </div>

          <form class="p-6 max-h-[70vh] overflow-y-auto space-y-4" @submit.prevent="salvar">
            <div
              v-if="mostrarSeletorUnidade"
              class="p-4 rounded-xl border border-gray-200 dark:border-gray-600 bg-gray-50 dark:bg-gray-800/50"
            >
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Unidade administrativa *
              </label>
              <select v-model="form.unidade_id" class="input" required>
                <option value="">Selecione a secretaria…</option>
                <option v-for="u in unidades" :key="u.id" :value="u.id">
                  {{ u.sigla ? `${u.sigla} — ` : '' }}{{ u.nome }}
                </option>
              </select>
            </div>

            <div
              v-else-if="unidadeLabel"
              class="p-4 rounded-xl border border-primary-200 dark:border-primary-800 bg-primary-50/50 dark:bg-primary-900/20"
            >
              <p class="text-xs font-semibold text-gray-500 uppercase">Secretaria</p>
              <p class="text-sm font-semibold text-gray-900 dark:text-white mt-1">{{ unidadeLabel }}</p>
            </div>

            <ul class="text-xs text-gray-600 dark:text-gray-400 space-y-1 list-disc list-inside">
              <li>Usado no select <strong>Despacho Técnico Oficial</strong> na formalização de OS.</li>
              <li>O conteúdo integra o fluxo de assinatura eletrônica simples.</li>
            </ul>

            <div>
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Título *</label>
              <input
                v-model="form.titulo"
                type="text"
                class="input"
                maxlength="120"
                required
                placeholder="Ex.: Asfalto frio CBUQ"
              />
            </div>

            <div>
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Texto do despacho *</label>
              <Editor v-model="form.texto" :mostrar-contagem="true" placeholder="Conteúdo gravado na formalização…" />
            </div>

            <label class="flex items-center gap-3 p-3 rounded-lg bg-gray-50 dark:bg-gray-700/50 border border-gray-200 dark:border-gray-600 cursor-pointer">
              <input v-model="form.ativo" type="checkbox" class="w-4 h-4 rounded text-primary-600" />
              <span class="text-sm font-semibold text-gray-900 dark:text-white">Disponível para formalização (ativo)</span>
            </label>

            <div class="flex justify-end gap-3 pt-4 border-t border-gray-200 dark:border-gray-700">
              <button type="button" class="btn-secondary" :disabled="salvando" @click="fechar">Cancelar</button>
              <button type="submit" class="btn-primary" :disabled="salvando || !formValido">
                {{ salvando ? 'Salvando…' : modo === 'editar' ? 'Salvar alterações' : 'Criar texto' }}
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
import { DocumentTextIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import Editor from '@/components/shared/Editor.vue'

const props = defineProps({
  aberto: Boolean,
  modo: { type: String, default: 'criar' },
  item: { type: Object, default: null },
  salvando: Boolean,
  unidadeLabel: { type: String, default: '' },
  mostrarSeletorUnidade: { type: Boolean, default: false },
  unidades: { type: Array, default: () => [] }
})

const emit = defineEmits(['fechar', 'salvar'])

const form = ref({
  titulo: '',
  texto: '',
  ativo: true,
  unidade_id: ''
})

const formValido = computed(() => {
  const base = form.value.titulo.trim() && form.value.texto.trim()
  if (props.mostrarSeletorUnidade && props.modo === 'criar') {
    return Boolean(base && form.value.unidade_id)
  }
  return Boolean(base)
})

watch(
  () => [props.aberto, props.item, props.modo],
  () => {
    if (!props.aberto) return
    if (props.modo === 'editar' && props.item) {
      form.value = {
        titulo: props.item.titulo,
        texto: props.item.texto,
        ativo: props.item.ativo,
        unidade_id: props.item.unidade || ''
      }
    } else {
      form.value = {
        titulo: '',
        texto: '',
        ativo: true,
        unidade_id: ''
      }
    }
  },
  { immediate: true }
)

function fechar() {
  emit('fechar')
}

function salvar() {
  if (!formValido.value) return
  const payload = {
    titulo: form.value.titulo.trim(),
    texto: form.value.texto.trim(),
    ativo: form.value.ativo
  }
  if (props.mostrarSeletorUnidade && form.value.unidade_id) {
    payload.unidade = form.value.unidade_id
  }
  emit('salvar', payload)
}
</script>