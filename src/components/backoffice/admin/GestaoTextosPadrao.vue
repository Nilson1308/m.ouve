<template>
  <div class="max-w-7xl">
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
      <div>
        <h2 class="text-lg font-bold text-gray-900 dark:text-white">Textos padrão de despacho</h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Modelos por secretaria para formalização e assinatura de ordens de serviço
          <span v-if="unidadeContextoLabel" class="text-gray-500"> · {{ unidadeContextoLabel }}</span>
        </p>
      </div>

      <button
        type="button"
        class="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-primary-600 to-indigo-600 hover:from-primary-700 hover:to-indigo-700 text-white rounded-lg font-medium text-sm transition-colors shadow-button"
        :disabled="store.semPermissaoUnidade || store.loading"
        @click="abrirCriar"
      >
        <PlusIcon class="w-5 h-5" />
        Novo texto
      </button>
    </div>

    <div
      v-if="store.semPermissaoUnidade"
      class="card p-6 border-2 border-amber-200 dark:border-amber-800 bg-amber-50 dark:bg-amber-900/20 mb-6"
    >
      <p class="font-semibold text-amber-900 dark:text-amber-100">Acesso restrito</p>
      <p class="text-sm text-amber-800 dark:text-amber-200 mt-1">{{ store.erro }}</p>
    </div>

    <template v-else>
      <div class="flex flex-col lg:flex-row gap-3 mb-4">
        <div class="relative flex-1">
          <MagnifyingGlassIcon class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
          <input
            v-model="busca"
            type="search"
            class="input pl-10"
            placeholder="Buscar por título ou conteúdo…"
          />
        </div>
        <select
          v-if="mostrarFiltroUnidade"
          v-model="filtroUnidadeId"
          class="input lg:max-w-xs"
        >
          <option value="">Todas as unidades</option>
          <option v-for="u in unidadesNasListagem" :key="u.id" :value="u.id">
            {{ u.sigla ? `${u.sigla} — ` : '' }}{{ u.nome }}
          </option>
        </select>
        <select v-model="filtroAtivo" class="input lg:max-w-[11rem]">
          <option value="">Todos os status</option>
          <option value="ativo">Somente ativos</option>
          <option value="inativo">Somente inativos</option>
        </select>
      </div>

      <div v-if="store.loading && !store.itens.length" class="card p-12 flex flex-col items-center justify-center">
        <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
        <p class="text-gray-600 dark:text-gray-400 text-sm mt-4">Carregando textos…</p>
      </div>

      <div v-else class="card overflow-hidden">
        <div class="overflow-x-auto">
          <table class="w-full">
            <thead class="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
              <tr>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">
                  Título
                </th>
                <th
                  v-if="mostrarFiltroUnidade"
                  class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase"
                >
                  Unidade
                </th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">
                  Status
                </th>
                <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">
                  Atualizado
                </th>
                <th class="px-6 py-3 text-right text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">
                  Ações
                </th>
              </tr>
            </thead>
            <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
              <tr
                v-for="item in itensFiltrados"
                :key="item.id"
                class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                :class="{ 'opacity-75': !item.ativo }"
              >
                <td class="px-6 py-4 min-w-[12rem]">
                  <div class="flex items-start gap-3">
                    <div class="p-2 bg-primary-100 dark:bg-primary-900/40 rounded-lg shrink-0">
                      <DocumentTextIcon class="w-5 h-5 text-primary-600 dark:text-primary-400" />
                    </div>
                    <div class="min-w-0">
                      <p class="text-sm font-semibold text-gray-900 dark:text-white">{{ item.titulo }}</p>
                      <p class="text-xs text-gray-500 dark:text-gray-400 mt-1 line-clamp-2 whitespace-pre-wrap">
                        {{ item.texto }}
                      </p>
                    </div>
                  </div>
                </td>
                <td v-if="mostrarFiltroUnidade" class="px-6 py-4 text-sm text-gray-700 dark:text-gray-300">
                  {{ item.unidadeSigla || item.unidadeNome || '—' }}
                </td>
                <td class="px-6 py-4">
                  <span
                    :class="[
                      'inline-flex px-2.5 py-1 rounded-badge text-xs font-semibold',
                      item.ativo
                        ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300'
                        : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'
                    ]"
                  >
                    {{ item.ativo ? 'Ativo' : 'Inativo' }}
                  </span>
                </td>
                <td class="px-6 py-4 text-sm text-gray-600 dark:text-gray-400 whitespace-nowrap">
                  {{ formatarData(item.atualizadoEm || item.criadoEm) }}
                </td>
                <td class="px-6 py-4 text-right">
                  <div class="inline-flex items-center gap-1">
                    <button
                      type="button"
                      class="p-2 text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg"
                      title="Editar"
                      @click="abrirEditar(item)"
                    >
                      <PencilSquareIcon class="w-5 h-5" />
                    </button>
                    <button
                      type="button"
                      class="p-2 text-amber-600 hover:bg-amber-50 dark:hover:bg-amber-900/20 rounded-lg"
                      title="Ativar/inativar"
                      :disabled="store.saving"
                      @click="toggleAtivo(item)"
                    >
                      <EyeIcon v-if="item.ativo" class="w-5 h-5" />
                      <EyeSlashIcon v-else class="w-5 h-5" />
                    </button>
                    <button
                      type="button"
                      class="p-2 text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg"
                      title="Excluir"
                      :disabled="store.saving"
                      @click="confirmarExclusao(item)"
                    >
                      <TrashIcon class="w-5 h-5" />
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="!itensFiltrados.length" class="p-12 text-center text-sm text-gray-500">
          {{ store.itens.length ? 'Nenhum resultado com os filtros atuais.' : 'Nenhum texto cadastrado.' }}
        </div>
      </div>
    </template>

    <ModalTextoPadrao
      :aberto="modalAberto"
      :modo="modalModo"
      :item="itemEdicao"
      :salvando="store.saving"
      :unidade-label="unidadeModalLabel"
      :mostrar-seletor-unidade="precisaSeletorUnidade"
      :unidades="unidadesAtivas"
      @fechar="fecharModal"
      @salvar="salvarModal"
    />
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import {
  PlusIcon,
  DocumentTextIcon,
  MagnifyingGlassIcon,
  PencilSquareIcon,
  TrashIcon,
  EyeIcon,
  EyeSlashIcon
} from '@heroicons/vue/24/outline'
import { useTextosPadraoStore } from '@/stores/textosPadrao'
import { useAdminStore } from '@/stores/admin'
import { useAuthStore } from '@/stores/auth'
import { useAdminToast } from '@/composables/useAdminToast'
import ModalTextoPadrao from './ModalTextoPadrao.vue'

const store = useTextosPadraoStore()
const adminStore = useAdminStore()
const authStore = useAuthStore()
const { mostrarToast } = useAdminToast()
const { unidadesAtivas } = storeToRefs(adminStore)

const busca = ref('')
const filtroUnidadeId = ref('')
const filtroAtivo = ref('')
const modalAberto = ref(false)
const modalModo = ref('criar')
const itemEdicao = ref(null)

const precisaSeletorUnidade = computed(() => !authStore.user?.unidade_id)

const mostrarFiltroUnidade = computed(() => {
  const ids = new Set(store.itens.map((t) => t.unidade).filter(Boolean))
  return ids.size > 1 || precisaSeletorUnidade.value
})

const unidadesNasListagem = computed(() => {
  const byId = new Map()
  for (const t of store.itens) {
    if (t.unidade) {
      byId.set(t.unidade, {
        id: t.unidade,
        nome: t.unidadeNome,
        sigla: t.unidadeSigla
      })
    }
  }
  return [...byId.values()].sort((a, b) => a.nome.localeCompare(b.nome, 'pt-BR'))
})

const unidadeContextoLabel = computed(() => {
  if (precisaSeletorUnidade.value) return 'Visão administrativa'
  const first = store.itens[0]
  if (!first?.unidadeNome) return ''
  return first.unidadeSigla
    ? `${first.unidadeNome} (${first.unidadeSigla})`
    : first.unidadeNome
})

const unidadeModalLabel = computed(() => {
  if (precisaSeletorUnidade.value && modalModo.value === 'criar') return ''
  const u = store.itens[0]
  if (!u) return unidadeContextoLabel.value
  return u.unidadeSigla ? `${u.unidadeNome} (${u.unidadeSigla})` : u.unidadeNome
})

const itensFiltrados = computed(() => {
  let lista = store.itens
  const q = busca.value.trim().toLowerCase()
  if (q) {
    lista = lista.filter(
      (t) => t.titulo.toLowerCase().includes(q) || t.texto.toLowerCase().includes(q)
    )
  }
  if (filtroUnidadeId.value) {
    lista = lista.filter((t) => t.unidade === filtroUnidadeId.value)
  }
  if (filtroAtivo.value === 'ativo') lista = lista.filter((t) => t.ativo)
  if (filtroAtivo.value === 'inativo') lista = lista.filter((t) => !t.ativo)
  return lista
})

function formatarData(iso) {
  if (!iso) return '—'
  return new Date(iso).toLocaleString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

function abrirCriar() {
  modalModo.value = 'criar'
  itemEdicao.value = null
  modalAberto.value = true
}

function abrirEditar(item) {
  modalModo.value = 'editar'
  itemEdicao.value = item
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
}

async function salvarModal(payload) {
  try {
    if (modalModo.value === 'editar' && itemEdicao.value) {
      await store.atualizar(itemEdicao.value.id, payload)
      mostrarToast('Texto atualizado com sucesso.')
    } else {
      await store.criar(payload)
      mostrarToast('Texto criado com sucesso.')
    }
    fecharModal()
  } catch {
    mostrarToast(store.erro || 'Erro ao salvar texto.', true)
  }
}

async function toggleAtivo(item) {
  try {
    await store.alternarAtivo(item)
    mostrarToast('Status atualizado.')
  } catch {
    mostrarToast(store.erro || 'Erro ao alterar status.', true)
  }
}

function confirmarExclusao(item) {
  if (!window.confirm(`Excluir o texto "${item.titulo}"? Esta ação não pode ser desfeita.`)) return
  store
    .remover(item.id)
    .then(() => mostrarToast('Texto excluído.'))
    .catch(() => mostrarToast(store.erro || 'Erro ao excluir.', true))
}

onMounted(() => {
  store.carregar().catch(() => {})
  if (precisaSeletorUnidade.value && !unidadesAtivas.value.length) {
    adminStore.carregarUnidades({ silencioso: true }).catch(() => {})
  }
})
</script>