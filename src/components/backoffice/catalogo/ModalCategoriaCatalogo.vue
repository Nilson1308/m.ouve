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
      class="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm overflow-hidden"
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
        <div
          class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-2xl max-h-[90dvh] flex flex-col overflow-hidden"
        >
          <header
            class="shrink-0 px-6 py-5 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-primary-50 to-cyan-50 dark:from-primary-900/20 dark:to-cyan-900/20"
          >
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-center gap-3 min-w-0">
                <div class="p-2 bg-primary-100 dark:bg-primary-900/40 rounded-lg shrink-0">
                  <FolderIcon class="w-6 h-6 text-primary-600 dark:text-primary-400" />
                </div>
                <div class="min-w-0">
                  <h2 class="text-xl font-bold text-gray-900 dark:text-white">
                    {{ categoria ? 'Editar categoria' : 'Nova categoria' }}
                  </h2>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mt-0.5">
                    Agrupa serviços na tela inicial do PWA (Nova Solicitação)
                  </p>
                </div>
              </div>
              <button
                type="button"
                class="p-2 shrink-0 hover:bg-gray-100 active:bg-gray-200 dark:hover:bg-gray-700 dark:active:bg-gray-600 rounded-lg transition-colors"
                aria-label="Fechar"
                @click="$emit('fechar')"
              >
                <XMarkIcon class="w-5 h-5 text-gray-500 dark:text-gray-400" />
              </button>
            </div>
          </header>

          <form class="flex flex-col flex-1 min-h-0 overflow-hidden" @submit.prevent="salvar">
            <div class="flex-1 min-h-0 overflow-y-auto overscroll-contain p-6 space-y-5">
            <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
              <div class="md:col-span-2">
                <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Nome *
                </label>
                <input v-model="formulario.nome" type="text" required class="input" placeholder="Ex.: Zeladoria Urbana" />
              </div>

              <div>
                <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Slug
                </label>
                <input
                  v-model="formulario.slug"
                  type="text"
                  class="input font-mono text-sm"
                  placeholder="zeladoria_urbana (auto)"
                />
              </div>

              <div>
                <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Ordem de exibição
                </label>
                <input v-model.number="formulario.ordem" type="number" min="0" class="input" />
              </div>

              <div class="md:col-span-2">
                <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Descrição
                </label>
                <textarea
                  v-model="formulario.descricao"
                  rows="2"
                  class="input resize-none min-h-[88px]"
                  placeholder="Texto exibido ao cidadão ao escolher a categoria..."
                />
              </div>

              <div class="md:col-span-2">
                <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Ícone da categoria
                </label>
                <SeletorIcone v-model="formulario.icone" />
              </div>

              <div>
                <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                  Tipo legado (API)
                </label>
                <select v-model="formulario.tipo_legado" class="input text-sm">
                  <option value="">— Nenhum —</option>
                  <option value="ouvidoria">Ouvidoria</option>
                  <option value="zeladoria">Zeladoria</option>
                </select>
              </div>
            </div>

            <div
              class="flex items-start gap-3 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600"
            >
              <input
                id="categoria-ativa"
                v-model="formulario.ativo"
                type="checkbox"
                class="mt-0.5 w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
              />
              <div class="flex-1">
                <label for="categoria-ativa" class="block text-sm font-semibold text-gray-900 dark:text-white cursor-pointer">
                  Categoria ativa
                </label>
                <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                  Inativas não aparecem no PWA nem como opção para novos serviços.
                </p>
              </div>
            </div>
            </div>

            <footer
              class="shrink-0 flex flex-col sm:flex-row sm:items-center justify-end gap-3 p-4 sm:p-6 border-t border-gray-200 dark:border-gray-700 bg-gray-50 dark:bg-gray-900/50"
            >
              <button
                type="button"
                class="min-h-[44px] px-4 py-2 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 active:bg-gray-400 dark:hover:bg-gray-500 dark:active:bg-gray-400 text-gray-700 dark:text-gray-200 rounded-lg font-medium transition-colors"
                @click="$emit('fechar')"
              >
                Cancelar
              </button>
              <button
                type="submit"
                class="btn-primary min-h-[44px] !py-2 !px-6"
                :disabled="salvando || !formularioValido"
              >
                {{ salvando ? 'Salvando…' : categoria ? 'Salvar alterações' : 'Criar categoria' }}
              </button>
            </footer>
          </form>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useCatalogoStore } from '@/stores/catalogo'
import { FolderIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import SeletorIcone from './SeletorIcone.vue'

const props = defineProps({
  categoria: { type: Object, default: null }
})

const emit = defineEmits(['fechar', 'sucesso'])

const catalogoStore = useCatalogoStore()
const salvando = ref(false)

const formulario = ref({
  nome: '',
  slug: '',
  descricao: '',
  icone: '',
  ordem: 0,
  tipo_legado: '',
  ativo: true
})

const formularioValido = computed(() => String(formulario.value.nome || '').trim().length >= 2)

watch(
  () => props.categoria,
  (cat) => {
    if (cat) {
      formulario.value = {
        nome: cat.nome || '',
        slug: cat.slug || '',
        descricao: cat.descricao || '',
        icone: cat.icone || '',
        ordem: cat.ordem ?? 0,
        tipo_legado: cat.tipo_legado || '',
        ativo: cat.ativo !== false
      }
    } else {
      formulario.value = {
        nome: '',
        slug: '',
        descricao: '',
        icone: '',
        ordem: 0,
        tipo_legado: '',
        ativo: true
      }
    }
  },
  { immediate: true }
)

async function salvar() {
  if (!formularioValido.value) return
  salvando.value = true
  try {
    if (props.categoria?.id) {
      await catalogoStore.atualizarCategoriaCatalogo(props.categoria.id, formulario.value)
    } else {
      await catalogoStore.criarCategoriaCatalogo(formulario.value)
    }
    emit('sucesso')
  } catch (err) {
    console.error(err)
  } finally {
    salvando.value = false
  }
}
</script>