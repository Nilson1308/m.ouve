<template>
  <div class="max-w-7xl">
    <!-- Header com Ações -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
      <div>
        <h2 class="text-lg font-bold text-gray-900 dark:text-white">
          Unidades Administrativas
        </h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Secretarias e órgãos executivos da prefeitura
        </p>
      </div>

      <button
        @click="abrirModalCriacao"
        class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium text-sm transition-colors shadow-button"
      >
        <PlusIcon class="w-5 h-5" />
        Nova Unidade
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="card p-12 flex flex-col items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      <p class="text-gray-600 dark:text-gray-400 text-sm mt-4">Carregando unidades...</p>
    </div>

    <!-- Tabela de Unidades -->
    <div v-else class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Unidade
              </th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Sigla
              </th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Tom da IA
              </th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Usuários
              </th>
              <th class="px-6 py-3 text-right text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Ações
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="unidade in unidades"
              :key="unidade.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
            >
              <!-- Nome e Descrição -->
              <td class="px-6 py-4">
                <div class="flex items-start gap-3">
                  <div class="p-2 bg-primary-100 dark:bg-primary-900/40 rounded-lg">
                    <BuildingOfficeIcon class="w-5 h-5 text-primary-600 dark:text-primary-400" />
                  </div>
                  <div class="min-w-0">
                    <p class="text-sm font-semibold text-gray-900 dark:text-white">
                      {{ unidade.nome }}
                    </p>
                    <p class="text-xs text-gray-600 dark:text-gray-400 mt-0.5 line-clamp-2">
                      {{ unidade.descricao }}
                    </p>
                  </div>
                </div>
              </td>

              <!-- Sigla -->
              <td class="px-6 py-4">
                <span class="inline-flex items-center px-3 py-1 rounded-badge bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 text-sm font-mono font-semibold">
                  {{ unidade.sigla }}
                </span>
              </td>

              <!-- Tom da IA -->
              <td class="px-6 py-4">
                <span
                  class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-full text-xs font-medium max-w-[11rem] truncate"
                  :class="badgeClassTomIa(unidade.tom_ia)"
                  :title="labelTomIa(unidade)"
                >
                  <SparklesIcon class="w-3.5 h-3.5 shrink-0 opacity-80" />
                  {{ labelTomIa(unidade) }}
                </span>
              </td>

              <!-- Status -->
              <td class="px-6 py-4">
                <span
                  :class="[
                    'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-badge text-xs font-semibold',
                    unidade.ativo
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                  ]"
                >
                  <span
                    :class="[
                      'w-1.5 h-1.5 rounded-full',
                      unidade.ativo ? 'bg-green-500' : 'bg-gray-400'
                    ]"
                  ></span>
                  {{ unidade.ativo ? 'Ativo' : 'Inativo' }}
                </span>
              </td>

              <!-- Usuários -->
              <td class="px-6 py-4">
                <div class="flex items-center gap-2">
                  <UserGroupIcon class="w-4 h-4 text-gray-400" />
                  <span class="text-sm text-gray-700 dark:text-gray-300">
                    {{ unidade.usuarios_count }}
                  </span>
                </div>
              </td>

              <!-- Ações -->
              <td class="px-6 py-4 text-right">
                <button
                  @click="abrirModalEdicao(unidade)"
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-colors"
                >
                  <PencilSquareIcon class="w-4 h-4" />
                  Editar
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Empty State -->
      <div v-if="unidades.length === 0" class="p-12 text-center">
        <BuildingOfficeIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-2">
          Nenhuma unidade cadastrada
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          Comece criando a primeira unidade administrativa
        </p>
        <button
          @click="abrirModalCriacao"
          class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium text-sm transition-colors"
        >
          <PlusIcon class="w-5 h-5" />
          Nova Unidade
        </button>
      </div>
    </div>

    <!-- Modal de Criação/Edição -->
    <ModalUnidade
      v-if="modalAberto"
      :unidade="unidadeSelecionada"
      @fechar="fecharModal"
      @salvar="salvarUnidade"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import {
  BuildingOfficeIcon,
  UserGroupIcon,
  PlusIcon,
  PencilSquareIcon,
  SparklesIcon
} from '@heroicons/vue/24/outline'
import { badgeClassTomIa, labelTomIa } from '@/utils/tomIaUnidade'
import ModalUnidade from './ModalUnidade.vue'
import { useAdminStore } from '@/stores/admin'
import { useAdminToast } from '@/composables/useAdminToast'

const adminStore = useAdminStore()
const { mostrarToast } = useAdminToast()
const { unidades, loading } = storeToRefs(adminStore)

const modalAberto = ref(false)
const unidadeSelecionada = ref(null)

function abrirModalCriacao() {
  unidadeSelecionada.value = null
  modalAberto.value = true
}

function abrirModalEdicao(unidade) {
  unidadeSelecionada.value = { ...unidade }
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
  unidadeSelecionada.value = null
}

async function salvarUnidade(dados) {
  try {
    if (unidadeSelecionada.value?.id) {
      // Editar
      await adminStore.atualizarUnidade(unidadeSelecionada.value.id, dados)
      mostrarToast('Unidade atualizada com sucesso.')
    } else {
      // Criar
      await adminStore.criarUnidade(dados)
      mostrarToast('Unidade criada com sucesso.')
    }
    fecharModal()
  } catch (error) {
    console.error('Erro ao salvar unidade:', error)
    mostrarToast(adminStore.erro || 'Erro ao salvar unidade. Tente novamente.', true)
  }
}
</script>
