<template>
  <div class="space-y-6">
    <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
      <div>
        <h3 class="text-lg font-bold text-gray-900 dark:text-white">Categorias do catálogo</h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Agrupamentos exibidos na jornada do cidadão (Nova Solicitação)
        </p>
      </div>
      <button type="button" class="btn-primary !py-2 !px-4 text-sm" @click="abrirCriacao">
        <PlusCircleIcon class="w-5 h-5" />
        Nova categoria
      </button>
    </div>

    <div v-if="catalogoStore.loadingCategorias" class="card p-12 flex flex-col items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      <p class="text-gray-600 dark:text-gray-400 text-sm mt-4">Carregando categorias...</p>
    </div>

    <div v-else class="card overflow-hidden !p-0">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
            <tr>
              <th
                class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider"
              >
                Categoria
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider"
              >
                Slug
              </th>
              <th
                class="px-6 py-3 text-center text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider"
              >
                Ordem
              </th>
              <th
                class="px-6 py-3 text-center text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider"
              >
                Serviços
              </th>
              <th
                class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider"
              >
                Status
              </th>
              <th
                class="px-6 py-3 text-right text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider"
              >
                Ações
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="cat in categorias"
              :key="cat.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
            >
              <td class="px-6 py-4">
                <div class="flex items-start gap-3">
                  <div
                    class="p-2 bg-gradient-to-br from-primary-100 to-cyan-100 dark:from-primary-900/40 dark:to-cyan-900/30 rounded-lg"
                  >
                    <FolderIcon class="w-5 h-5 text-primary-600 dark:text-primary-400" />
                  </div>
                  <div class="min-w-0">
                    <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ cat.nome }}</p>
                    <p class="text-xs text-gray-600 dark:text-gray-400 mt-0.5 line-clamp-2">
                      {{ cat.descricao || 'Sem descrição' }}
                    </p>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <span
                  class="inline-flex px-2.5 py-1 rounded-badge bg-gray-100 dark:bg-gray-700 font-mono text-xs text-gray-700 dark:text-gray-300"
                >
                  {{ cat.slug }}
                </span>
              </td>
              <td class="px-6 py-4 text-center text-sm font-semibold text-gray-700 dark:text-gray-300">
                {{ cat.ordem }}
              </td>
              <td class="px-6 py-4 text-center">
                <span
                  class="inline-flex px-2.5 py-0.5 rounded-full text-xs font-bold bg-primary-100 text-primary-800 dark:bg-primary-900/40 dark:text-primary-300"
                >
                  {{ cat.servicos_count }}
                </span>
              </td>
              <td class="px-6 py-4">
                <span
                  :class="[
                    'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-badge text-xs font-semibold',
                    cat.ativo
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                  ]"
                >
                  <span
                    :class="['w-1.5 h-1.5 rounded-full', cat.ativo ? 'bg-green-500' : 'bg-gray-400']"
                  />
                  {{ cat.ativo ? 'Ativa' : 'Inativa' }}
                </span>
              </td>
              <td class="px-6 py-4 text-right">
                <div class="flex items-center justify-end gap-2">
                  <button
                    type="button"
                    class="p-2 rounded-lg text-primary-600 hover:bg-primary-50 dark:hover:bg-primary-900/30 transition-colors"
                    title="Editar"
                    @click="abrirEdicao(cat)"
                  >
                    <PencilSquareIcon class="w-5 h-5" />
                  </button>
                  <button
                    type="button"
                    class="p-2 rounded-lg text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30 transition-colors"
                    title="Excluir"
                    @click="confirmarExclusao(cat)"
                  >
                    <TrashIcon class="w-5 h-5" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="!categorias.length" class="p-12 text-center">
        <FolderIcon class="w-12 h-12 text-gray-400 mx-auto mb-3" />
        <p class="text-sm text-gray-600 dark:text-gray-400">Nenhuma categoria cadastrada.</p>
      </div>
    </div>

    <Teleport to="body">
      <ModalCategoriaCatalogo
        v-if="modalAberto"
        :categoria="categoriaEmEdicao"
        @fechar="fecharModal"
        @sucesso="aoSucessoModal"
      />
    </Teleport>

  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useCatalogoStore } from '@/stores/catalogo'
import ModalCategoriaCatalogo from './ModalCategoriaCatalogo.vue'
import {
  PlusCircleIcon,
  FolderIcon,
  PencilSquareIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'

const catalogoStore = useCatalogoStore()
const { categoriasCatalogo } = storeToRefs(catalogoStore)

const categorias = computed(() => categoriasCatalogo.value)

const modalAberto = ref(false)
const categoriaEmEdicao = ref(null)
function abrirCriacao() {
  categoriaEmEdicao.value = null
  modalAberto.value = true
}

function abrirEdicao(cat) {
  categoriaEmEdicao.value = cat
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
  categoriaEmEdicao.value = null
}

function aoSucessoModal() {
  fecharModal()
  catalogoStore.carregarCategoriasCatalogo().catch(() => {})
}

async function confirmarExclusao(cat) {
  const msg =
    cat.servicos_count > 0
      ? `A categoria "${cat.nome}" possui ${cat.servicos_count} serviço(s). Ela será desativada em vez de excluída. Continuar?`
      : `Excluir a categoria "${cat.nome}"? Esta ação não pode ser desfeita.`
  if (!window.confirm(msg)) return
  try {
    await catalogoStore.excluirCategoriaCatalogo(cat.id)
  } catch (err) {
    console.error(err)
  }
}

onMounted(() => {
  catalogoStore.carregarCategoriasCatalogo().catch(() => {})
})
</script>