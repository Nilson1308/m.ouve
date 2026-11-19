<template>
  <div class="max-w-7xl">
    <!-- Header com Ações -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
      <div>
        <h2 class="text-lg font-bold text-gray-900 dark:text-white">
          Perfis de Acesso (RBAC)
        </h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Gestão granular de permissões por módulo
        </p>
      </div>

      <button
        @click="abrirModalCriacao"
        class="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-medium text-sm transition-colors shadow-lg shadow-purple-500/50"
      >
        <PlusCircleIcon class="w-5 h-5" />
        Novo Perfil
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loadingPerfis" class="card p-12 flex flex-col items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-purple-500 border-t-transparent" />
      <p class="text-gray-600 dark:text-gray-400 text-sm mt-4">Carregando perfis...</p>
    </div>

    <!-- Grid de Perfis -->
    <div v-else-if="perfisAcesso.length > 0" class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
      <div
        v-for="perfil in perfisAcesso"
        :key="perfil.id"
        class="group card hover:shadow-card-hover transition-all duration-300 border-2 border-transparent hover:border-purple-200 dark:hover:border-purple-800"
      >
        <div class="flex items-start justify-between mb-4">
          <div class="flex items-center gap-3">
            <div class="p-3 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/40 dark:to-pink-900/40 rounded-lg">
              <ShieldCheckIcon class="w-6 h-6 text-purple-600 dark:text-purple-400" />
            </div>
            <div>
              <h3 class="text-base font-bold text-gray-900 dark:text-white">
                {{ perfil.nome }}
              </h3>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                ID: {{ perfil.id }}
              </p>
            </div>
          </div>

          <!-- Badge Ativo/Inativo -->
          <span
            :class="[
              'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-badge text-xs font-semibold',
              perfil.ativo
                ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
            ]"
          >
            <span
              :class="[
                'w-1.5 h-1.5 rounded-full',
                perfil.ativo ? 'bg-green-500' : 'bg-gray-400'
              ]"
            ></span>
            {{ perfil.ativo ? 'Ativo' : 'Inativo' }}
          </span>
        </div>

        <!-- Descrição -->
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
          {{ perfil.descricao || 'Sem descrição' }}
        </p>

        <!-- Resumo de Permissões -->
        <div class="mb-4 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
          <div class="flex items-center justify-between text-xs text-gray-600 dark:text-gray-400">
            <span class="font-semibold">Módulos com acesso:</span>
            <span class="px-2 py-0.5 bg-purple-100 dark:bg-purple-900/40 text-purple-700 dark:text-purple-300 rounded-full font-bold">
              {{ contarModulosAtivos(perfil.permissoes) }}
            </span>
          </div>
        </div>

        <!-- Estatísticas -->
        <div class="flex items-center gap-4 mb-4 text-xs text-gray-600 dark:text-gray-400">
          <div class="flex items-center gap-1.5">
            <UserGroupIcon class="w-4 h-4" />
            <span>{{ perfil.usuarios_count || 0 }} usuário(s)</span>
          </div>
          <div v-if="perfil.requer_vinculo" class="flex items-center gap-1.5">
            <BuildingOfficeIcon class="w-4 h-4" />
            <span>Req. vínculo</span>
          </div>
        </div>

        <!-- Ações -->
        <div class="flex items-center gap-2 pt-4 border-t border-gray-200 dark:border-gray-700">
          <button
            @click="abrirModalEdicao(perfil)"
            class="flex-1 inline-flex items-center justify-center gap-2 px-3 py-2 bg-gray-100 dark:bg-gray-700 hover:bg-gray-200 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 rounded-lg text-sm font-medium transition-colors"
          >
            <PencilSquareIcon class="w-4 h-4" />
            Editar
          </button>
          <button
            v-if="!perfil.sistema && (perfil.usuarios_count || 0) === 0"
            @click="confirmarExclusao(perfil)"
            class="inline-flex items-center justify-center gap-2 px-3 py-2 bg-red-100 dark:bg-red-900/30 hover:bg-red-200 dark:hover:bg-red-900/50 text-red-700 dark:text-red-300 rounded-lg text-sm font-medium transition-colors"
            title="Excluir perfil"
          >
            <TrashIcon class="w-4 h-4" />
          </button>
        </div>
      </div>
    </div>

    <!-- Empty State -->
    <div v-else class="card p-12 text-center">
      <div class="w-16 h-16 mx-auto mb-4 bg-gradient-to-br from-purple-100 to-pink-100 dark:from-purple-900/40 dark:to-pink-900/40 rounded-full flex items-center justify-center">
        <ShieldCheckIcon class="w-8 h-8 text-purple-600 dark:text-purple-400" />
      </div>
      <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-2">
        Nenhum perfil cadastrado
      </h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Crie o primeiro perfil de acesso com permissões granulares
      </p>
      <button
        @click="abrirModalCriacao"
        class="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-medium text-sm transition-colors shadow-lg shadow-purple-500/50"
      >
        <PlusCircleIcon class="w-5 h-5" />
        Novo Perfil
      </button>
    </div>

    <!-- Modal de Criação/Edição (A MATRIZ!) -->
    <ModalPerfil
      v-if="modalAberto"
      ref="modalPerfilRef"
      :perfil="perfilSelecionado"
      @fechar="fecharModal"
      @salvar="salvarPerfil"
    />
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { storeToRefs } from 'pinia'
import {
  ShieldCheckIcon,
  PlusCircleIcon,
  UserGroupIcon,
  BuildingOfficeIcon,
  PencilSquareIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'
import ModalPerfil from './ModalPerfil.vue'
import { useAdminStore } from '@/stores/admin'
import { useAdminToast } from '@/composables/useAdminToast'

const { mostrarToast } = useAdminToast()

const adminStore = useAdminStore()
const { perfisAcesso, loadingPerfis } = storeToRefs(adminStore)

const modalAberto = ref(false)
const modalPerfilRef = ref(null)
const perfilSelecionado = ref(null)

function contarModulosAtivos(permissoes) {
  if (!permissoes || typeof permissoes !== 'object') return 0
  return Object.keys(permissoes).filter((modulo) => {
    if (modulo === 'regras') return false
    const perms = permissoes[modulo]
    return perms && Object.values(perms).some(v => v === true)
  }).length
}

function abrirModalCriacao() {
  perfilSelecionado.value = null
  modalAberto.value = true
}

function abrirModalEdicao(perfil) {
  perfilSelecionado.value = { ...perfil }
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
  perfilSelecionado.value = null
}

async function salvarPerfil(dados) {
  try {
    if (perfilSelecionado.value?.id) {
      // Editar
      await adminStore.atualizarPerfilAcesso(perfilSelecionado.value.id, dados)
      mostrarToast('Perfil atualizado com sucesso.')
    } else {
      // Criar
      await adminStore.criarPerfilAcesso(dados)
      mostrarToast('Perfil criado com sucesso.')
    }
    fecharModal()
  } catch (error) {
    console.error('Erro ao salvar perfil:', error)
    mostrarToast(adminStore.erro || 'Erro ao salvar perfil. Tente novamente.', true)
    modalPerfilRef.value?.resetSalvando?.()
  }
}

async function confirmarExclusao(perfil) {
  const confirmar = confirm(
    `Deseja realmente excluir o perfil "${perfil.nome}"?\n\n` +
    `Esta ação não pode ser desfeita.`
  )
  
  if (!confirmar) return

  try {
    await adminStore.excluirPerfilAcesso(perfil.id)
    mostrarToast('Perfil excluído com sucesso.')
  } catch (error) {
    console.error('Erro ao excluir perfil:', error)
    mostrarToast(adminStore.erro || 'Erro ao excluir perfil. Tente novamente.', true)
  }
}
</script>
