<template>
  <div class="max-w-7xl">
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
      <div>
        <h2 class="text-lg font-bold text-gray-900 dark:text-white">
          Catálogo de Serviços
        </h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Form Builder dinâmico — define o que o cidadão preenche no app
        </p>
      </div>

      <button
        type="button"
        class="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-primary-600 to-cyan-600 hover:from-primary-700 hover:to-cyan-700 text-white rounded-lg font-medium text-sm transition-colors shadow-button"
        @click="abrirModalCriacao"
      >
        <PlusIcon class="w-5 h-5" />
        Novo Serviço
      </button>
    </div>

    <div v-if="loadingServicos" class="card p-12 flex flex-col items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      <p class="text-gray-600 dark:text-gray-400 text-sm mt-4">Carregando catálogo...</p>
    </div>

    <div v-else class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Nome
              </th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                SLA Padrão
              </th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Unidade Responsável
              </th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-right text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Ações
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="servico in servicos"
              :key="servico.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
            >
              <td class="px-6 py-4">
                <div class="flex items-center gap-3 min-w-0">
                  <div class="p-2 bg-cyan-100 dark:bg-cyan-900/40 rounded-lg shrink-0">
                    <WrenchScrewdriverIcon class="w-5 h-5 text-cyan-600 dark:text-cyan-400" />
                  </div>
                  <div class="min-w-0">
                    <p class="text-sm font-semibold text-gray-900 dark:text-white truncate">
                      {{ servico.nome }}
                    </p>
                    <p v-if="servico.descricao" class="text-xs text-gray-500 dark:text-gray-400 truncate max-w-md">
                      {{ servico.descricao }}
                    </p>
                  </div>
                </div>
              </td>
              <td class="px-6 py-4">
                <span class="text-sm font-mono text-gray-800 dark:text-gray-200">
                  {{ servico.sla_padrao_horas }}h
                </span>
              </td>
              <td class="px-6 py-4">
                <span class="text-sm text-gray-700 dark:text-gray-300">
                  {{ servico.unidade_responsavel_nome || '—' }}
                </span>
              </td>
              <td class="px-6 py-4">
                <span
                  :class="[
                    'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-badge text-xs font-semibold',
                    servico.ativo
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                  ]"
                >
                  <span
                    :class="['w-1.5 h-1.5 rounded-full', servico.ativo ? 'bg-green-500' : 'bg-gray-400']"
                  />
                  {{ servico.ativo ? 'Ativo' : 'Inativo' }}
                </span>
              </td>
              <td class="px-6 py-4 text-right space-x-2">
                <button
                  type="button"
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-colors"
                  @click="abrirModalEdicao(servico)"
                >
                  <PencilSquareIcon class="w-4 h-4" />
                  Editar
                </button>
                <button
                  type="button"
                  class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20 rounded-lg transition-colors"
                  title="Excluir ou desativar"
                  @click="confirmarExclusao(servico)"
                >
                  <TrashIcon class="w-4 h-4" />
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="servicos.length === 0" class="p-12 text-center">
        <p class="text-gray-600 dark:text-gray-400 text-sm">Nenhum serviço cadastrado.</p>
      </div>
    </div>

    <ModalServicoCatalogo
      v-if="modalAberto"
      :servico="servicoSelecionado"
      :unidades="unidadesAtivas"
      @fechar="fecharModal"
      @salvar="salvarServico"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import {
  PlusIcon,
  PencilSquareIcon,
  TrashIcon,
  WrenchScrewdriverIcon
} from '@heroicons/vue/24/outline'
import ModalServicoCatalogo from './ModalServicoCatalogo.vue'
import { useCatalogoStore } from '@/stores/catalogo'
import { useAdminStore } from '@/stores/admin'
import { useAdminToast } from '@/composables/useAdminToast'

const catalogoStore = useCatalogoStore()
const adminStore = useAdminStore()
const { servicos, loadingServicos } = storeToRefs(catalogoStore)
const { unidadesAtivas } = storeToRefs(adminStore)
const { mostrarToast } = useAdminToast()

const modalAberto = ref(false)
const servicoSelecionado = ref(null)

function abrirModalCriacao() {
  servicoSelecionado.value = null
  modalAberto.value = true
}

function abrirModalEdicao(servico) {
  servicoSelecionado.value = { ...servico }
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
  servicoSelecionado.value = null
}

async function salvarServico({ form, campos }) {
  try {
    if (servicoSelecionado.value?.id) {
      await catalogoStore.atualizarServicoCatalogo(servicoSelecionado.value.id, form, campos)
      mostrarToast('Serviço atualizado com sucesso.')
    } else {
      await catalogoStore.criarServicoCatalogo(form, campos)
      mostrarToast('Serviço criado com sucesso.')
    }
    fecharModal()
  } catch {
    mostrarToast(catalogoStore.erro || 'Erro ao salvar serviço.', true)
  }
}

async function confirmarExclusao(servico) {
  const ok = confirm(
    `Remover o serviço "${servico.nome}"?\n\n` +
      'Se existirem protocolos vinculados, o sistema apenas DESATIVARÁ o serviço (soft delete), ' +
      'preservando o histórico. Caso contrário, o registro será excluído.'
  )
  if (!ok) return
  try {
    await catalogoStore.excluirServicoCatalogo(servico.id)
    mostrarToast('Operação concluída. Verifique o status na tabela (ativo/inativo).')
  } catch {
    mostrarToast(catalogoStore.erro || 'Erro ao excluir serviço.', true)
  }
}

onMounted(() => {
  catalogoStore.carregarServicosCatalogo().catch(() => {})
  if (!unidadesAtivas.value.length) {
    adminStore.carregarUnidades().catch(() => {})
  }
})
</script>