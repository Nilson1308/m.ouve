<template>
  <div class="max-w-7xl">
    <!-- Header com Ações -->
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
      <div>
        <h2 class="text-lg font-bold text-gray-900 dark:text-white">
          Usuários e Controle de Acesso
        </h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Gestão de servidores, perfis e permissões (RBAC)
        </p>
      </div>

      <button
        @click="abrirModalCriacao"
        class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium text-sm transition-colors shadow-button"
      >
        <PlusIcon class="w-5 h-5" />
        Novo Usuário
      </button>
    </div>

    <!-- Filtros Rápidos -->
    <div class="flex flex-wrap items-center gap-3 mb-6">
      <button
        v-for="perfil in perfisDisponiveis"
        :key="perfil.id"
        @click="filtrarPorPerfil(perfil.id)"
        :class="[
          'inline-flex items-center gap-2 px-3 py-1.5 rounded-lg text-sm font-medium transition-colors',
          filtroAtivo === perfil.id
            ? 'bg-purple-100 text-purple-700 dark:bg-purple-900/30 dark:text-purple-300 ring-2 ring-purple-500'
            : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
        ]"
      >
        <span class="w-2 h-2 rounded-full bg-purple-500"></span>
        {{ perfil.nome }}
        <span
          v-if="contarPorPerfil(perfil.id) > 0"
          :class="[
            'px-1.5 py-0.5 rounded-full text-xs font-bold',
            filtroAtivo === perfil.id
              ? 'bg-white/50'
              : 'bg-gray-200 dark:bg-gray-600'
          ]"
        >
          {{ contarPorPerfil(perfil.id) }}
        </span>
      </button>

      <button
        v-if="filtroAtivo"
        @click="limparFiltro"
        class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200"
      >
        <XMarkIcon class="w-4 h-4" />
        Limpar filtro
      </button>
    </div>

    <!-- Loading State -->
    <div v-if="loading" class="card p-12 flex flex-col items-center justify-center">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      <p class="text-gray-600 dark:text-gray-400 text-sm mt-4">Carregando usuários...</p>
    </div>

    <!-- Tabela de Usuários -->
    <div v-else class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Usuário
              </th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Perfil (Role)
              </th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Unidade Vinculada
              </th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Status
              </th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Último Acesso
              </th>
              <th class="px-6 py-3 text-right text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase tracking-wider">
                Ações
              </th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="usuario in usuariosFiltrados"
              :key="usuario.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
            >
              <!-- Nome e E-mail -->
              <td class="px-6 py-4">
                <div class="flex items-center gap-3">
                  <div class="w-10 h-10 rounded-full bg-gradient-to-br from-primary-500 to-purple-600 flex items-center justify-center text-white font-bold text-sm">
                    {{ getIniciais(usuario.nome) }}
                  </div>
                  <div class="min-w-0">
                    <p class="text-sm font-semibold text-gray-900 dark:text-white">
                      {{ usuario.nome }}
                    </p>
                    <p class="text-xs text-gray-600 dark:text-gray-400">
                      {{ usuario.email }}
                    </p>
                  </div>
                </div>
              </td>

              <!-- Perfil -->
              <td class="px-6 py-4">
                <span
                  :class="[
                    'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-badge text-xs font-semibold',
                    getCorPerfil(usuario.perfil)
                  ]"
                >
                  <ShieldCheckIcon class="w-3.5 h-3.5" />
                  {{ getNomePerfil(usuario.perfil) }}
                </span>
              </td>

              <!-- Unidade -->
              <td class="px-6 py-4">
                <div v-if="usuario.unidade_nome" class="flex items-center gap-2">
                  <BuildingOfficeIcon class="w-4 h-4 text-gray-400" />
                  <span class="text-sm text-gray-700 dark:text-gray-300">
                    {{ usuario.unidade_nome }}
                  </span>
                </div>
                <span v-else class="text-sm text-gray-500 dark:text-gray-400 italic">
                  Sem vínculo
                </span>
              </td>

              <!-- Status -->
              <td class="px-6 py-4">
                <span
                  :class="[
                    'inline-flex items-center gap-1.5 px-2.5 py-1 rounded-badge text-xs font-semibold',
                    usuario.ativo
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                  ]"
                >
                  <span
                    :class="[
                      'w-1.5 h-1.5 rounded-full',
                      usuario.ativo ? 'bg-green-500' : 'bg-gray-400'
                    ]"
                  ></span>
                  {{ usuario.ativo ? 'Ativo' : 'Inativo' }}
                </span>
              </td>

              <!-- Último Acesso -->
              <td class="px-6 py-4">
                <span class="text-sm text-gray-600 dark:text-gray-400">
                  {{ formatarUltimoAcesso(usuario.ultimo_acesso) }}
                </span>
              </td>

              <!-- Ações -->
              <td class="px-6 py-4">
                <div class="flex items-center justify-end gap-2">
                  <button
                    @click="abrirModalEdicao(usuario)"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-primary-600 hover:text-primary-700 dark:text-primary-400 dark:hover:text-primary-300 hover:bg-primary-50 dark:hover:bg-primary-900/20 rounded-lg transition-colors"
                    title="Editar usuário"
                  >
                    <PencilSquareIcon class="w-4 h-4" />
                    Editar
                  </button>
                  <button
                    @click="resetarSenha(usuario)"
                    class="inline-flex items-center gap-1.5 px-3 py-1.5 text-sm font-medium text-orange-600 hover:text-orange-700 dark:text-orange-400 dark:hover:text-orange-300 hover:bg-orange-50 dark:hover:bg-orange-900/20 rounded-lg transition-colors"
                    title="Gerar nova senha temporária"
                  >
                    <KeyIcon class="w-4 h-4" />
                  </button>
                </div>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <!-- Empty State -->
      <div v-if="usuariosFiltrados.length === 0" class="p-12 text-center">
        <UserGroupIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
        <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-2">
          {{ filtroAtivo ? 'Nenhum usuário encontrado' : 'Nenhum usuário cadastrado' }}
        </h3>
        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
          {{ filtroAtivo ? 'Tente limpar os filtros ou criar um novo usuário' : 'Comece criando o primeiro usuário do sistema' }}
        </p>
        <button
          v-if="!filtroAtivo"
          @click="abrirModalCriacao"
          class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium text-sm transition-colors"
        >
          <PlusIcon class="w-5 h-5" />
          Novo Usuário
        </button>
      </div>
    </div>

    <!-- Modal de Criação/Edição -->
    <ModalUsuario
      v-if="modalAberto"
      :usuario="usuarioSelecionado"
      @fechar="fecharModal"
      @salvar="salvarUsuario"
    />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { storeToRefs } from 'pinia'
import {
  UserGroupIcon,
  BuildingOfficeIcon,
  ShieldCheckIcon,
  PlusIcon,
  PencilSquareIcon,
  KeyIcon,
  XMarkIcon
} from '@heroicons/vue/24/outline'
import ModalUsuario from './ModalUsuario.vue'
import { useAdminStore } from '@/stores/admin'
import { useAdminToast } from '@/composables/useAdminToast'

const adminStore = useAdminStore()
const { mostrarToast } = useAdminToast()

async function copiarTexto(texto) {
  if (!texto) return false
  try {
    if (navigator.clipboard?.writeText) {
      await navigator.clipboard.writeText(texto)
      return true
    }
  } catch {
    /* fallback abaixo */
  }
  return false
}
const { usuarios, loading, perfisAcesso } = storeToRefs(adminStore)

// Perfis disponíveis para filtro
const perfisDisponiveis = computed(() => perfisAcesso.value)

const modalAberto = ref(false)
const usuarioSelecionado = ref(null)
const filtroAtivo = ref(null)

// Computeds
const usuariosFiltrados = computed(() => {
  if (!filtroAtivo.value) return usuarios.value
  return usuarios.value.filter(
    (u) =>
      u.perfil_acesso_id === filtroAtivo.value ||
      u.perfil === filtroAtivo.value
  )
})

// Funções
function abrirModalCriacao() {
  usuarioSelecionado.value = null
  modalAberto.value = true
}

function abrirModalEdicao(usuario) {
  usuarioSelecionado.value = { ...usuario }
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
  usuarioSelecionado.value = null
}

async function salvarUsuario(dados) {
  try {
    if (usuarioSelecionado.value?.id) {
      await adminStore.atualizarUsuario(usuarioSelecionado.value.id, dados)
      mostrarToast('Usuário atualizado com sucesso.')
    } else {
      const criado = await adminStore.criarUsuario(dados)
      if (criado.senha_inicial) {
        const copiou = await copiarTexto(criado.senha_inicial)
        mostrarToast(
          copiou
            ? 'Usuário criado. Senha temporária copiada para a área de transferência.'
            : `Usuário criado. Senha temporária: ${criado.senha_inicial}`,
          false,
          copiou ? 4000 : 8000
        )
      } else {
        mostrarToast('Usuário criado com sucesso.')
      }
    }
    fecharModal()
  } catch (error) {
    console.error('Erro ao salvar usuário:', error)
    mostrarToast(adminStore.erro || 'Erro ao salvar usuário. Tente novamente.', true)
  }
}

async function resetarSenha(usuario) {
  const confirmar = confirm(
    `Gerar nova senha temporária para ${usuario.nome}?\n\n` +
      `E-mail: ${usuario.email}\n\n` +
      'A senha será exibida aqui para você copiar e entregar ao servidor.'
  )

  if (!confirmar) return

  try {
    const resultado = await adminStore.resetarSenhaUsuario(usuario.id)
    const copiou = await copiarTexto(resultado.senha)
    mostrarToast(
      copiou
        ? `${resultado.mensagem || 'Senha redefinida.'} Copiada para a área de transferência.`
        : `${resultado.mensagem || 'Senha redefinida.'} Nova senha: ${resultado.senha}`,
      false,
      copiou ? 5000 : 8000
    )
  } catch (error) {
    console.error('Erro ao resetar senha:', error)
    mostrarToast(adminStore.erro || 'Erro ao resetar senha. Tente novamente.', true)
  }
}

function filtrarPorPerfil(perfilId) {
  filtroAtivo.value = filtroAtivo.value === perfilId ? null : perfilId
}

function limparFiltro() {
  filtroAtivo.value = null
}

function contarPorPerfil(perfilId) {
  return usuarios.value.filter(u => u.perfil === perfilId).length
}

function getNomePerfil(perfilId) {
  const perfil = perfisAcesso.value.find(p => p.id === perfilId || p.slug === perfilId)
  return perfil?.nome || perfilId
}

function getCorPerfil(perfilId) {
  // Usar sempre roxo (purple) para todos os perfis dinâmicos
  return 'bg-purple-100 text-purple-800 dark:bg-purple-900/30 dark:text-purple-300'
}

function getIniciais(nome) {
  const partes = nome.trim().split(' ')
  if (partes.length === 1) return partes[0].substring(0, 2).toUpperCase()
  return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase()
}

function formatarUltimoAcesso(data) {
  if (!data) return 'Nunca'
  
  const d = new Date(data)
  const agora = new Date()
  const diff = agora - d
  
  // Menos de 1 hora
  if (diff < 3600000) {
    const minutos = Math.floor(diff / 60000)
    return `há ${minutos}min`
  }
  
  // Menos de 1 dia
  if (diff < 86400000) {
    const horas = Math.floor(diff / 3600000)
    return `há ${horas}h`
  }
  
  // Formato padrão
  return d.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit'
  })
}
</script>
