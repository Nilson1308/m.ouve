<template>
  <!-- Backdrop -->
  <Transition
    enter-active-class="transition-opacity duration-300"
    enter-from-class="opacity-0"
    enter-to-class="opacity-100"
    leave-active-class="transition-opacity duration-300"
    leave-from-class="opacity-100"
    leave-to-class="opacity-0"
  >
    <div
      class="fixed inset-0 bg-black/50 backdrop-blur-sm z-50 flex items-center justify-center p-4"
      @click.self="$emit('fechar')"
    >
      <!-- Modal -->
      <Transition
        enter-active-class="transition-all duration-300 ease-out"
        enter-from-class="opacity-0 scale-95"
        enter-to-class="opacity-100 scale-100"
        leave-active-class="transition-all duration-200 ease-in"
        leave-from-class="opacity-100 scale-100"
        leave-to-class="opacity-0 scale-95"
      >
        <div
          class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-3xl max-h-[90vh] flex flex-col overflow-hidden"
        >
          <!-- Header -->
          <div class="shrink-0 px-6 py-3 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-purple-50 to-blue-50 dark:from-purple-900/20 dark:to-blue-900/20">
            <div class="flex items-start justify-between gap-3">
              <div class="flex items-center gap-3 min-w-0">
                <div class="p-1.5 bg-purple-100 dark:bg-purple-900/40 rounded-lg shrink-0">
                  <UserCircleIcon class="w-5 h-5 text-purple-600 dark:text-purple-400" />
                </div>
                <div>
                  <h2 class="text-lg font-bold text-gray-900 dark:text-white">
                    {{ usuario ? 'Editar Usuário' : 'Novo Usuário do Sistema' }}
                  </h2>
                  <p class="text-xs text-gray-600 dark:text-gray-400 mt-0.5 line-clamp-2">
                    {{ usuario ? 'Altere os dados e permissões do servidor' : 'Cadastre um novo servidor com controle de acesso' }}
                  </p>
                </div>
              </div>

              <button
                @click="$emit('fechar')"
                class="p-2 hover:bg-gray-100 dark:hover:bg-gray-700 rounded-lg transition-colors"
              >
                <XMarkIcon class="w-5 h-5 text-gray-500 dark:text-gray-400" />
              </button>
            </div>
          </div>

          <!-- Formulário -->
          <form @submit.prevent="salvar" class="flex flex-col flex-1 min-h-0">
            <div class="flex-1 overflow-y-auto p-6 space-y-6">
            <!-- Seção: Dados Pessoais -->
            <div>
              <h3 class="text-sm font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <IdentificationIcon class="w-5 h-5 text-gray-600 dark:text-gray-400" />
                Dados Pessoais
              </h3>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Nome -->
                <div class="md:col-span-2">
                  <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Nome Completo *
                  </label>
                  <input
                    v-model="formulario.nome"
                    type="text"
                    placeholder="Ex: Maria da Silva Santos"
                    required
                    class="input"
                  />
                </div>

                <!-- E-mail -->
                <div>
                  <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    E-mail Corporativo *
                  </label>
                  <input
                    v-model="formulario.email"
                    type="email"
                    placeholder="usuario@prefeitura.gov.br"
                    required
                    class="input"
                  />
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Será usado para login e notificações
                  </p>
                </div>

                <!-- CPF -->
                <div>
                  <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    CPF *
                  </label>
                  <input
                    v-model="formulario.cpf"
                    type="text"
                    placeholder="000.000.000-00"
                    required
                    maxlength="14"
                    class="input font-mono"
                    @input="formatarCPF"
                  />
                </div>
              </div>
            </div>

            <!-- Seção: Controle de Acesso (RBAC) -->
            <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
              <h3 class="text-sm font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <ShieldCheckIcon class="w-5 h-5 text-gray-600 dark:text-gray-400" />
                Controle de Acesso (RBAC)
              </h3>

              <div class="space-y-5">
                <!-- Perfil (Role) -->
                <div>
                  <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Perfil de Acesso *
                  </label>
                  <select
                    v-model="formulario.perfil"
                    required
                    class="input"
                    @change="onPerfilChange"
                  >
                    <option value="">Selecione um perfil...</option>
                    <option
                      v-for="perfil in perfisDisponiveis"
                      :key="perfil.id"
                      :value="perfil.id"
                    >
                      {{ perfil.nome }} — {{ perfil.descricao }}
                    </option>
                  </select>

                  <!-- Info Box do Perfil Selecionado -->
                  <div
                    v-if="perfilSelecionado"
                    class="mt-3 p-3 rounded-lg border flex items-start gap-3 bg-purple-50 border-purple-200 dark:bg-purple-900/20 dark:border-purple-800"
                  >
                    <InformationCircleIcon class="w-5 h-5 text-purple-600 dark:text-purple-400 shrink-0 mt-0.5" />
                    <div>
                      <p class="text-sm font-semibold text-purple-900 dark:text-purple-100 mb-1">
                        {{ perfilSelecionado.nome }}
                      </p>
                      <p class="text-xs text-purple-700 dark:text-purple-300">
                        {{ perfilSelecionado.descricao || 'Perfil customizado' }}
                      </p>
                    </div>
                  </div>
                </div>

                <!-- Vínculo de Unidade (condicional) -->
                <div v-if="perfilSelecionado?.requer_vinculo">
                  <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Unidade Administrativa *
                  </label>
                  <select
                    v-model="formulario.unidade_id"
                    required
                    class="input"
                  >
                    <option value="">Selecione uma unidade...</option>
                    <option
                      v-for="unidade in unidadesAtivas"
                      :key="unidade.id"
                      :value="unidade.id"
                    >
                      {{ unidade.sigla }} — {{ unidade.nome }}
                    </option>
                  </select>
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Usuário terá acesso apenas aos protocolos desta unidade
                  </p>
                </div>

                <!-- Explicação quando NÃO requer vínculo -->
                <div
                  v-else-if="formulario.perfil"
                  class="p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800 flex items-start gap-3"
                >
                  <InformationCircleIcon class="w-5 h-5 text-blue-600 dark:text-blue-400 shrink-0 mt-0.5" />
                  <p class="text-xs text-blue-800 dark:text-blue-200">
                    <strong>Este perfil não requer vínculo a uma unidade.</strong><br />
                    {{ perfilSelecionado?.id === 'super_admin' 
                      ? 'Super Admins têm acesso total ao sistema e todas as unidades.' 
                      : 'Ouvidores têm acesso à Mesa de Trabalho Geral com todos os protocolos.' 
                    }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Status Ativo/Inativo -->
            <div class="border-t border-gray-200 dark:border-gray-700 pt-6">
              <div class="flex items-start gap-3 p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600">
                <input
                  v-model="formulario.ativo"
                  type="checkbox"
                  id="usuario-ativo"
                  class="mt-0.5 w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500 dark:focus:ring-primary-600 dark:ring-offset-gray-800 focus:ring-2 dark:bg-gray-700 dark:border-gray-600"
                />
                <div class="flex-1">
                  <label for="usuario-ativo" class="block text-sm font-semibold text-gray-900 dark:text-white cursor-pointer">
                    Usuário Ativo
                  </label>
                  <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                    Usuários inativos não podem fazer login e não têm acesso ao sistema
                  </p>
                </div>
              </div>
            </div>

            <!-- Informações Adicionais (Se estiver editando) -->
            <div v-if="usuario" class="border-t border-gray-200 dark:border-gray-700 pt-6">
              <div class="p-4 bg-gray-50 dark:bg-gray-700/50 rounded-lg">
                <h4 class="text-sm font-semibold text-gray-900 dark:text-white mb-3">
                  Informações do Cadastro
                </h4>
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3 text-xs text-gray-600 dark:text-gray-400">
                  <div>
                    <strong class="text-gray-900 dark:text-white">ID do Usuário:</strong> {{ usuario.id }}
                  </div>
                  <div>
                    <strong class="text-gray-900 dark:text-white">Último Acesso:</strong> {{ formatarData(usuario.ultimo_acesso) || 'Nunca' }}
                  </div>
                  <div>
                    <strong class="text-gray-900 dark:text-white">Criado em:</strong> {{ formatarData(usuario.criado_em) }}
                  </div>
                  <div v-if="usuario.atualizado_em !== usuario.criado_em">
                    <strong class="text-gray-900 dark:text-white">Última edição:</strong> {{ formatarData(usuario.atualizado_em) }}
                  </div>
                </div>
              </div>
            </div>
            </div>

            <!-- Footer -->
            <div class="shrink-0 px-6 py-4 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-600 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                * Campos obrigatórios
              </p>
              <p v-if="!usuario" class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                O usuário receberá um e-mail para definir sua senha
              </p>
            </div>

            <div class="flex items-center gap-3 w-full sm:w-auto">
              <button
                type="button"
                @click="$emit('fechar')"
                class="flex-1 sm:flex-none px-4 py-2 bg-gray-200 dark:bg-gray-600 hover:bg-gray-300 dark:hover:bg-gray-500 text-gray-700 dark:text-gray-200 rounded-lg font-medium transition-colors"
              >
                Cancelar
              </button>
              <button
                @click="salvar"
                :disabled="!formularioValido || salvando"
                class="flex-1 sm:flex-none px-6 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
              >
                <div v-if="salvando" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <CheckIcon v-else class="w-5 h-5" />
                {{ salvando ? 'Salvando...' : usuario ? 'Salvar Alterações' : 'Criar Usuário' }}
              </button>
            </div>
            </div>
          </form>
        </div>
      </Transition>
    </div>
  </Transition>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { storeToRefs } from 'pinia'
import {
  UserCircleIcon,
  IdentificationIcon,
  ShieldCheckIcon,
  XMarkIcon,
  CheckIcon,
  InformationCircleIcon
} from '@heroicons/vue/24/outline'
import { useAdminStore } from '@/stores/admin'

const props = defineProps({
  usuario: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['fechar', 'salvar'])

const adminStore = useAdminStore()
const { perfisAcesso, unidadesAtivas } = storeToRefs(adminStore)

// Perfis disponíveis (filtrar apenas ativos)
const perfisDisponiveis = computed(() => {
  return perfisAcesso.value.filter(p => p.ativo)
})

// Formulário
const formulario = ref({
  nome: '',
  email: '',
  cpf: '',
  perfil: '',
  unidade_id: '',
  ativo: true
})

const salvando = ref(false)

// Perfil selecionado (para exibir info box)
const perfilSelecionado = computed(() => {
  if (!formulario.value.perfil) return null
  return perfisAcesso.value.find(p => p.id === formulario.value.perfil || p.slug === formulario.value.perfil)
})

// Preencher formulário se estiver editando
watch(() => props.usuario, (usuario) => {
  if (usuario) {
    formulario.value = {
      nome: usuario.nome || '',
      email: usuario.email || '',
      cpf: usuario.cpf || '',
      perfil: usuario.perfil_acesso_id || usuario.perfil || '',
      unidade_id: usuario.unidade_id || '',
      ativo: usuario.ativo !== false
    }
  } else {
    formulario.value = {
      nome: '',
      email: '',
      cpf: '',
      perfil: '',
      unidade_id: '',
      ativo: true
    }
  }
}, { immediate: true })

// Validação
const formularioValido = computed(() => {
  const { nome, email, cpf, perfil, unidade_id } = formulario.value
  
  // Validações básicas
  if (!nome.trim() || nome.length < 3) return false
  if (!email.trim() || !email.includes('@')) return false
  if (!cpf.trim() || cpf.replace(/\D/g, '').length !== 11) return false
  if (!perfil) return false
  
  // Se o perfil requer vínculo, validar unidade
  const perfilObj = perfilSelecionado.value
  if (perfilObj?.requer_vinculo && !unidade_id) return false
  
  return true
})

// Funções
function onPerfilChange() {
  // Limpar unidade_id se o novo perfil não requer vínculo
  const perfil = perfilSelecionado.value
  if (!perfil?.requer_vinculo) {
    formulario.value.unidade_id = ''
  }
}

function formatarCPF() {
  let cpf = formulario.value.cpf.replace(/\D/g, '')
  
  if (cpf.length > 11) cpf = cpf.substring(0, 11)
  
  if (cpf.length > 9) {
    cpf = cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4')
  } else if (cpf.length > 6) {
    cpf = cpf.replace(/(\d{3})(\d{3})(\d{1,3})/, '$1.$2.$3')
  } else if (cpf.length > 3) {
    cpf = cpf.replace(/(\d{3})(\d{1,3})/, '$1.$2')
  }
  
  formulario.value.cpf = cpf
}

async function salvar() {
  if (!formularioValido.value) return

  salvando.value = true

  try {
    // Preparar dados (sem unidade_id se não requer vínculo)
    const dados = { ...formulario.value }
    if (!perfilSelecionado.value?.requer_vinculo) {
      dados.unidade_id = null
    }
    
    emit('salvar', dados)
  } finally {
    salvando.value = false
  }
}

function formatarData(data) {
  if (!data) return null
  const d = new Date(data)
  return d.toLocaleDateString('pt-BR', {
    day: '2-digit',
    month: '2-digit',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}
</script>
