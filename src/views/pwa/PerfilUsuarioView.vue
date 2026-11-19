<template>
  <div class="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-950 dark:to-gray-900 high-contrast:from-black high-contrast:to-black pb-24">
    <!-- Header -->
    <header class="sticky top-0 z-20 backdrop-blur-xl bg-white/95 dark:bg-gray-900/95 high-contrast:bg-black border-b border-gray-200/50 dark:border-gray-800/50 high-contrast:border-yellow-300 shadow-soft safe-area-inset-top">
      <div class="px-4 py-3 flex items-center gap-3">
        <button @click="voltar" class="btn-icon flex-shrink-0">
          <ChevronLeftIcon class="w-6 h-6" />
        </button>
        <div class="flex-1">
          <h1 class="text-base font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300">
            Meu Perfil
          </h1>
          <p class="text-xs text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold">
            Gerencie seus dados pessoais
          </p>
        </div>
      </div>
    </header>

    <!-- Main Content -->
    <main class="px-4 py-6 space-y-6 max-w-2xl mx-auto animate-fade-in">
      <!-- Avatar e Info Básica -->
      <div class="card text-center p-6">
        <div class="relative inline-block mb-4">
          <div class="w-24 h-24 rounded-avatar bg-gradient-to-br from-primary-500 to-primary-600 high-contrast:from-yellow-300 high-contrast:to-yellow-400 flex items-center justify-center shadow-button mx-auto">
            <span class="text-3xl font-bold text-white high-contrast:text-black">
              {{ iniciais }}
            </span>
          </div>
          <button class="absolute bottom-0 right-0 w-8 h-8 bg-white dark:bg-gray-800 high-contrast:bg-gray-900 border-2 border-gray-200 dark:border-gray-700 high-contrast:border-yellow-300 rounded-full flex items-center justify-center shadow-soft hover:scale-110 transition-transform">
            <CameraIcon class="w-4 h-4 text-gray-600 dark:text-gray-400 high-contrast:text-yellow-300" />
          </button>
        </div>
        <h2 class="text-xl font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 mb-1">
          {{ authStore.userName }}
        </h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 high-contrast:text-white high-contrast:font-bold">
          CPF: {{ formatarCPF(authStore.userCPF) }}
        </p>
      </div>

      <!-- Navegação por Abas -->
      <div class="card p-1 flex gap-1">
        <button
          v-for="aba in abas"
          :key="aba.id"
          @click="abaAtiva = aba.id"
          class="flex-1 py-2.5 px-4 text-sm font-semibold rounded-button transition-all"
          :class="abaAtiva === aba.id 
            ? 'bg-primary-600 text-white high-contrast:bg-yellow-300 high-contrast:text-black shadow-soft' 
            : 'text-gray-600 dark:text-gray-400 high-contrast:text-white hover:bg-gray-100 dark:hover:bg-gray-700 high-contrast:hover:bg-gray-800'"
        >
          <component :is="aba.icone" class="w-4 h-4 inline-block mr-1" />
          {{ aba.label }}
        </button>
      </div>

      <!-- Aba: Dados Pessoais -->
      <div v-if="abaAtiva === 'pessoais'" class="space-y-4">
        <div class="card p-5">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-base font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300">
              Dados Pessoais
            </h3>
            <button
              v-if="!editandoPessoais"
              @click="editandoPessoais = true"
              class="btn-secondary text-sm"
            >
              <PencilIcon class="w-4 h-4 inline-block mr-1" />
              Editar
            </button>
          </div>

          <form @submit.prevent="salvarDadosPessoais" class="space-y-4">
            <!-- Nome -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-2">
                Nome Completo
              </label>
              <input
                v-model="dadosPessoais.nome"
                type="text"
                class="input"
                :disabled="!editandoPessoais"
                required
              />
            </div>

            <!-- Email -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-2">
                E-mail
              </label>
              <input
                v-model="dadosPessoais.email"
                type="email"
                class="input"
                :disabled="!editandoPessoais"
                required
              />
            </div>

            <!-- Telefone -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-2">
                Telefone
              </label>
              <input
                v-model="dadosPessoais.telefone"
                type="tel"
                class="input"
                placeholder="(00) 00000-0000"
                :disabled="!editandoPessoais"
                required
              />
            </div>

            <!-- Ações -->
            <div v-if="editandoPessoais" class="flex gap-3 pt-2">
              <button
                type="button"
                @click="cancelarEdicaoPessoais"
                class="btn-secondary flex-1"
                :disabled="salvandoPessoais"
              >
                Cancelar
              </button>
              <button
                type="submit"
                class="btn-primary flex-1"
                :disabled="salvandoPessoais"
              >
                <span v-if="salvandoPessoais" class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span>
                {{ salvandoPessoais ? 'Salvando...' : 'Salvar' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Aba: Endereço -->
      <div v-if="abaAtiva === 'endereco'" class="space-y-4">
        <div class="card p-5">
          <div class="flex items-center justify-between mb-4">
            <h3 class="text-base font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300">
              Endereço
            </h3>
            <button
              v-if="!editandoEndereco"
              @click="editandoEndereco = true"
              class="btn-secondary text-sm"
            >
              <PencilIcon class="w-4 h-4 inline-block mr-1" />
              Editar
            </button>
          </div>

          <form @submit.prevent="salvarEndereco" class="space-y-4">
            <!-- CEP -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-2">
                CEP
              </label>
              <div class="flex gap-2">
                <input
                  v-model="endereco.cep"
                  type="text"
                  class="input flex-1"
                  placeholder="00000-000"
                  :disabled="!editandoEndereco || buscandoCep"
                  required
                  @blur="buscarCEP"
                />
                <button
                  v-if="editandoEndereco"
                  type="button"
                  @click="buscarCEP"
                  :disabled="buscandoCep || !endereco.cep"
                  class="btn-secondary px-4"
                >
                  <MagnifyingGlassIcon v-if="!buscandoCep" class="w-5 h-5" />
                  <span v-else class="inline-block w-4 h-4 border-2 border-primary-600 border-t-transparent rounded-full animate-spin"></span>
                </button>
              </div>
            </div>

            <!-- Logradouro e Número -->
            <div class="grid grid-cols-3 gap-3">
              <div class="col-span-2">
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-2">
                  Logradouro
                </label>
                <input
                  v-model="endereco.logradouro"
                  type="text"
                  class="input"
                  :disabled="!editandoEndereco"
                  required
                />
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-2">
                  Número
                </label>
                <input
                  v-model="endereco.numero"
                  type="text"
                  class="input"
                  :disabled="!editandoEndereco"
                  required
                />
              </div>
            </div>

            <!-- Complemento -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-2">
                Complemento
              </label>
              <input
                v-model="endereco.complemento"
                type="text"
                class="input"
                placeholder="Apto, bloco, etc."
                :disabled="!editandoEndereco"
              />
            </div>

            <!-- Bairro -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-2">
                Bairro
              </label>
              <input
                v-model="endereco.bairro"
                type="text"
                class="input"
                :disabled="!editandoEndereco"
                required
              />
            </div>

            <!-- Cidade e Estado -->
            <div class="grid grid-cols-2 gap-3">
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-2">
                  Cidade
                </label>
                <input
                  v-model="endereco.cidade"
                  type="text"
                  class="input"
                  :disabled="!editandoEndereco"
                  required
                />
              </div>
              <div>
                <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-2">
                  Estado
                </label>
                <input
                  v-model="endereco.estado"
                  type="text"
                  class="input"
                  maxlength="2"
                  :disabled="!editandoEndereco"
                  required
                />
              </div>
            </div>

            <!-- Ações -->
            <div v-if="editandoEndereco" class="flex gap-3 pt-2">
              <button
                type="button"
                @click="cancelarEdicaoEndereco"
                class="btn-secondary flex-1"
                :disabled="salvandoEndereco"
              >
                Cancelar
              </button>
              <button
                type="submit"
                class="btn-primary flex-1"
                :disabled="salvandoEndereco"
              >
                <span v-if="salvandoEndereco" class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span>
                {{ salvandoEndereco ? 'Salvando...' : 'Salvar' }}
              </button>
            </div>
          </form>
        </div>
      </div>

      <!-- Aba: Segurança -->
      <div v-if="abaAtiva === 'seguranca'" class="space-y-4">
        <!-- Alterar Senha -->
        <div class="card p-5">
          <h3 class="text-base font-bold text-gray-900 dark:text-white high-contrast:text-yellow-300 mb-4">
            Alterar Senha
          </h3>

          <form @submit.prevent="alterarSenha" class="space-y-4">
            <!-- Senha Atual -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-2">
                Senha Atual
              </label>
              <div class="relative">
                <input
                  v-model="senhaData.atual"
                  :type="mostrarSenhaAtual ? 'text' : 'password'"
                  class="input pr-10"
                  required
                />
                <button
                  type="button"
                  @click="mostrarSenhaAtual = !mostrarSenhaAtual"
                  class="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <EyeIcon v-if="!mostrarSenhaAtual" class="w-5 h-5 text-gray-500" />
                  <EyeSlashIcon v-else class="w-5 h-5 text-gray-500" />
                </button>
              </div>
            </div>

            <!-- Nova Senha -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-2">
                Nova Senha
              </label>
              <div class="relative">
                <input
                  v-model="senhaData.nova"
                  :type="mostrarSenhaNova ? 'text' : 'password'"
                  class="input pr-10"
                  required
                  minlength="8"
                />
                <button
                  type="button"
                  @click="mostrarSenhaNova = !mostrarSenhaNova"
                  class="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <EyeIcon v-if="!mostrarSenhaNova" class="w-5 h-5 text-gray-500" />
                  <EyeSlashIcon v-else class="w-5 h-5 text-gray-500" />
                </button>
              </div>
            </div>

            <!-- Confirmar Nova Senha -->
            <div>
              <label class="block text-xs font-bold text-gray-700 dark:text-gray-300 high-contrast:text-yellow-300 mb-2">
                Confirmar Nova Senha
              </label>
              <div class="relative">
                <input
                  v-model="senhaData.confirmacao"
                  :type="mostrarSenhaConfirmacao ? 'text' : 'password'"
                  class="input pr-10"
                  required
                  minlength="8"
                />
                <button
                  type="button"
                  @click="mostrarSenhaConfirmacao = !mostrarSenhaConfirmacao"
                  class="absolute right-2 top-1/2 -translate-y-1/2 p-1 rounded-full hover:bg-gray-100 dark:hover:bg-gray-700"
                >
                  <EyeIcon v-if="!mostrarSenhaConfirmacao" class="w-5 h-5 text-gray-500" />
                  <EyeSlashIcon v-else class="w-5 h-5 text-gray-500" />
                </button>
              </div>
            </div>

            <!-- Botão Alterar -->
            <button
              type="submit"
              class="btn-primary w-full"
              :disabled="alterandoSenha"
            >
              <span v-if="alterandoSenha" class="inline-block w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></span>
              {{ alterandoSenha ? 'Alterando...' : 'Alterar Senha' }}
            </button>
          </form>
        </div>

        <!-- LGPD: Anonimização de Dados -->
        <div class="card p-5 border-2 border-purple-200 dark:border-purple-800 high-contrast:border-purple-500">
          <div class="flex items-start gap-3">
            <div class="flex-shrink-0 w-10 h-10 bg-purple-100 dark:bg-purple-900/30 high-contrast:bg-transparent rounded-full flex items-center justify-center">
              <ShieldCheckIcon class="w-6 h-6 text-purple-600 dark:text-purple-400 high-contrast:text-purple-300" />
            </div>
            <div class="flex-1">
              <h3 class="text-base font-bold text-purple-900 dark:text-purple-100 high-contrast:text-purple-300 mb-2">
                Privacidade e LGPD
              </h3>
              <p class="text-sm text-purple-800 dark:text-purple-200 high-contrast:text-white high-contrast:font-bold mb-3">
                De acordo com a Lei Geral de Proteção de Dados, você pode solicitar a anonimização dos seus dados pessoais.
              </p>
              <div class="bg-purple-50 dark:bg-purple-900/20 high-contrast:bg-transparent border border-purple-200 dark:border-purple-800 high-contrast:border-purple-400 rounded-card p-3 mb-4">
                <p class="text-xs text-purple-700 dark:text-purple-300 high-contrast:text-white high-contrast:font-bold leading-relaxed">
                  <strong>O que será anonimizado:</strong><br>
                  • Nome, CPF, e-mail e telefone<br>
                  • Endereço e dados de localização<br>
                  • Histórico de protocolos mantido de forma agregada
                </p>
              </div>
              <button
                @click="solicitarAnonimizacao"
                class="btn-secondary !border-purple-300 !text-purple-700 dark:!text-purple-400 hover:!bg-purple-50 dark:hover:!bg-purple-900/20 high-contrast:!border-purple-500 high-contrast:!text-purple-300"
              >
                <ShieldCheckIcon class="w-4 h-4 inline-block mr-1" />
                Solicitar Anonimização de Dados
              </button>
            </div>
          </div>
        </div>

        <!-- Desativar Conta -->
        <div class="card p-5 border-2 border-red-200 dark:border-red-800 high-contrast:border-red-500">
          <div class="flex items-start gap-3">
            <div class="flex-shrink-0 w-10 h-10 bg-red-100 dark:bg-red-900/30 high-contrast:bg-transparent rounded-full flex items-center justify-center">
              <ExclamationTriangleIcon class="w-6 h-6 text-red-600 dark:text-red-400 high-contrast:text-red-300" />
            </div>
            <div class="flex-1">
              <h3 class="text-base font-bold text-red-900 dark:text-red-100 high-contrast:text-red-300 mb-2">
                Desativar Conta
              </h3>
              <p class="text-sm text-red-800 dark:text-red-200 high-contrast:text-white high-contrast:font-bold mb-4">
                A desativação da conta é irreversível. Todos os seus dados serão removidos permanentemente.
              </p>
              <button
                @click="confirmarDesativacao"
                class="btn-secondary !border-red-300 !text-red-700 dark:!text-red-400 hover:!bg-red-50 dark:hover:!bg-red-900/20 high-contrast:!border-red-500 high-contrast:!text-red-300"
              >
                <TrashIcon class="w-4 h-4 inline-block mr-1" />
                Desativar Conta
              </button>
            </div>
          </div>
        </div>
      </div>
    </main>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { usuarioService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'
import { useDialog } from '@/composables/useDialog'
import {
  ChevronLeftIcon,
  CameraIcon,
  UserIcon,
  MapPinIcon,
  ShieldCheckIcon,
  PencilIcon,
  MagnifyingGlassIcon,
  EyeIcon,
  EyeSlashIcon,
  ExclamationTriangleIcon,
  TrashIcon
} from '@heroicons/vue/24/outline'

const router = useRouter()
const authStore = useAuthStore()
const { confirm, alert } = useDialog()

const carregandoPerfil = ref(true)

const abaAtiva = ref('pessoais')
const abas = [
  { id: 'pessoais', label: 'Pessoais', icone: UserIcon },
  { id: 'endereco', label: 'Endereço', icone: MapPinIcon },
  { id: 'seguranca', label: 'Segurança', icone: ShieldCheckIcon }
]

// Dados Pessoais
const editandoPessoais = ref(false)
const salvandoPessoais = ref(false)
const dadosPessoais = ref({
  nome: '',
  email: '',
  telefone: ''
})
const dadosPessoaisOriginais = ref({})

// Endereço
const editandoEndereco = ref(false)
const salvandoEndereco = ref(false)
const buscandoCep = ref(false)
const endereco = ref({
  cep: '',
  logradouro: '',
  numero: '',
  complemento: '',
  bairro: '',
  cidade: '',
  estado: ''
})
const enderecoOriginal = ref({})

// Segurança
const alterandoSenha = ref(false)
const mostrarSenhaAtual = ref(false)
const mostrarSenhaNova = ref(false)
const mostrarSenhaConfirmacao = ref(false)
const senhaData = ref({
  atual: '',
  nova: '',
  confirmacao: ''
})

// Computed
const iniciais = computed(() => {
  const nome = authStore.userName || ''
  const partes = nome.trim().split(' ')
  if (partes.length >= 2) {
    return (partes[0][0] + partes[partes.length - 1][0]).toUpperCase()
  }
  return partes[0] ? partes[0][0].toUpperCase() : '?'
})

const enderecoVazio = () => ({
  cep: '',
  logradouro: '',
  numero: '',
  complemento: '',
  bairro: '',
  cidade: '',
  estado: ''
})

function aplicarPerfilNaTela(perfil) {
  if (!perfil) return

  dadosPessoais.value = {
    nome: perfil.nome || '',
    email: perfil.email || '',
    telefone: perfil.telefone || ''
  }
  dadosPessoaisOriginais.value = { ...dadosPessoais.value }

  const end = perfil.endereco || null
  endereco.value = end
    ? {
        cep: end.cep || '',
        logradouro: end.logradouro || '',
        numero: end.numero || '',
        complemento: end.complemento || '',
        bairro: end.bairro || '',
        cidade: end.cidade || '',
        estado: end.estado || ''
      }
    : enderecoVazio()
  enderecoOriginal.value = { ...endereco.value }
}

async function carregarPerfil() {
  carregandoPerfil.value = true
  try {
    const perfil = await usuarioService.obterPerfil()
    authStore.atualizarUsuarioPerfil(perfil)
    aplicarPerfilNaTela(perfil)
  } catch (error) {
    aplicarPerfilNaTela(authStore.user)
    await alert(
      getApiErrorMessage(error, 'Não foi possível carregar o perfil. Exibindo dados da sessão.'),
      'Aviso'
    )
  } finally {
    carregandoPerfil.value = false
  }
}

// Métodos
function voltar() {
  router.push('/app/dashboard')
}

function formatarCPF(cpf) {
  if (!cpf) return ''
  return cpf.replace(/(\d{3})(\d{3})(\d{3})(\d{2})/, '$1.$2.$3-$4')
}

async function salvarDadosPessoais() {
  salvandoPessoais.value = true

  try {
    const perfil = await usuarioService.atualizarPerfil({
      nome: dadosPessoais.value.nome,
      email: dadosPessoais.value.email,
      telefone: dadosPessoais.value.telefone
    })
    authStore.atualizarUsuarioPerfil(perfil)
    aplicarPerfilNaTela(perfil)
    editandoPessoais.value = false
    await alert('Dados atualizados com sucesso!', 'Sucesso')
  } catch (error) {
    await alert(getApiErrorMessage(error, 'Erro ao salvar dados. Tente novamente.'), 'Erro')
  } finally {
    salvandoPessoais.value = false
  }
}

function cancelarEdicaoPessoais() {
  dadosPessoais.value = { ...dadosPessoaisOriginais.value }
  editandoPessoais.value = false
}

async function buscarCEP() {
  if (!endereco.value.cep || endereco.value.cep.length < 8) return
  
  buscandoCep.value = true
  
  try {
    const cep = endereco.value.cep.replace(/\D/g, '')
    const response = await fetch(`https://viacep.com.br/ws/${cep}/json/`)
    const dados = await response.json()
    
    if (dados.erro) {
      await alert('CEP não encontrado', 'Erro')
      return
    }
    
    endereco.value.logradouro = dados.logradouro
    endereco.value.bairro = dados.bairro
    endereco.value.cidade = dados.localidade
    endereco.value.estado = dados.uf
  } catch (error) {
    await alert('Erro ao buscar CEP. Verifique sua conexão.', 'Erro')
  } finally {
    buscandoCep.value = false
  }
}

async function salvarEndereco() {
  salvandoEndereco.value = true

  try {
    const perfil = await usuarioService.atualizarPerfil({
      endereco: { ...endereco.value }
    })
    authStore.atualizarUsuarioPerfil(perfil)
    aplicarPerfilNaTela(perfil)
    editandoEndereco.value = false
    await alert('Endereço atualizado com sucesso!', 'Sucesso')
  } catch (error) {
    await alert(getApiErrorMessage(error, 'Erro ao salvar endereço. Tente novamente.'), 'Erro')
  } finally {
    salvandoEndereco.value = false
  }
}

function cancelarEdicaoEndereco() {
  endereco.value = { ...enderecoOriginal.value }
  editandoEndereco.value = false
}

async function alterarSenha() {
  if (senhaData.value.nova !== senhaData.value.confirmacao) {
    await alert('As senhas não coincidem', 'Erro')
    return
  }
  
  if (senhaData.value.nova.length < 8) {
    await alert('A senha deve ter no mínimo 8 caracteres', 'Erro')
    return
  }
  
  alterandoSenha.value = true
  
  try {
    await usuarioService.alterarSenha({
      senha_atual: senhaData.value.atual,
      nova_senha: senhaData.value.nova
    })
    senhaData.value = { atual: '', nova: '', confirmacao: '' }
    await alert('Senha alterada com sucesso!', 'Sucesso')
  } catch (error) {
    await alert(
      getApiErrorMessage(error, 'Erro ao alterar senha. Verifique sua senha atual.'),
      'Erro'
    )
  } finally {
    alterandoSenha.value = false
  }
}

async function solicitarAnonimizacao() {
  const confirmado = await confirm(
    'Ao solicitar a anonimização, seus dados pessoais (nome, CPF, e-mail, telefone e endereço) serão desvinculados dos seus protocolos.\n\nOs protocolos permanecerão no sistema de forma agregada para fins estatísticos, mas não será mais possível identificá-los como seus.\n\nEsta ação é irreversível. Deseja continuar?',
    'Anonimizar Dados Pessoais (LGPD)',
    'Sim, anonimizar',
    'Cancelar'
  )
  
  if (confirmado) {
    try {
      const { authService } = await import('@/services/api')
      const data = await authService.anonimizar({
        refresh_token: localStorage.getItem('sinapse_refresh_token')
      })

      await alert(
        data.mensagem +
          '\n\nPrazo de conclusão: ' +
          (data.prazo_execucao || '48h'),
        'Solicitação Enviada'
      )
      
      // Logout após anonimização
      await authStore.logout()
      router.push('/login')
    } catch (error) {
      await alert('Erro ao solicitar anonimização. Tente novamente.', 'Erro')
    }
  }
}

async function confirmarDesativacao() {
  const confirmado = await confirm(
    'Esta ação é irreversível. Todos os seus dados, incluindo protocolos e histórico, serão permanentemente excluídos. Deseja realmente desativar sua conta?',
    'Desativar Conta',
    'Sim, desativar',
    'Cancelar'
  )
  
  if (confirmado) {
    try {
      const data = await usuarioService.desativar({
        refresh_token: localStorage.getItem('sinapse_refresh_token')
      })
      await alert(data.mensagem || 'Conta desativada.', 'Conta desativada')
      await authStore.logout()
      router.push('/login')
    } catch (error) {
      await alert(getApiErrorMessage(error, 'Erro ao desativar conta. Tente novamente.'), 'Erro')
    }
  }
}

onMounted(() => {
  void carregarPerfil()
})
</script>
