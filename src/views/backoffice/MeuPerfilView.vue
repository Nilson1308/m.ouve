<template>
  <div class="px-4 sm:px-6 lg:px-8 py-8 max-w-3xl mx-auto">
    <header class="mb-8">
      <h1 class="text-2xl font-bold text-gray-900 dark:text-white">Meu perfil</h1>
      <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
        Dados da conta e segurança de acesso
      </p>
    </header>

    <div class="flex gap-2 p-1 rounded-xl bg-gray-100 dark:bg-gray-800/80 border border-gray-200 dark:border-gray-700 mb-6">
      <button
        v-for="tab in ['dados', 'seguranca']"
        :key="tab"
        type="button"
        :class="[
          'flex-1 py-2.5 px-4 rounded-lg text-sm font-semibold transition-colors',
          aba === tab
            ? 'bg-white dark:bg-gray-900 text-primary-600 dark:text-primary-400 shadow-sm'
            : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white'
        ]"
        @click="aba = tab"
      >
        {{ tab === 'dados' ? 'Dados básicos' : 'Segurança' }}
      </button>
    </div>

    <div
      v-if="mensagem"
      class="mb-4 p-3 rounded-lg text-sm"
      :class="
        mensagemErro
          ? 'bg-red-50 dark:bg-red-950/40 text-red-800 dark:text-red-200 border border-red-200 dark:border-red-800'
          : 'bg-emerald-50 dark:bg-emerald-950/40 text-emerald-800 dark:text-emerald-200 border border-emerald-200 dark:border-emerald-800'
      "
    >
      {{ mensagem }}
    </div>

    <form v-if="aba === 'dados'" class="space-y-5" @submit.prevent="salvarDados">
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
        <div class="sm:col-span-2">
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Nome</label>
          <input v-model="formDados.nome" type="text" required class="input w-full" />
        </div>
        <div>
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">E-mail</label>
          <input v-model="formDados.email" type="email" required class="input w-full" />
        </div>
        <div>
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Telefone</label>
          <input v-model="formDados.telefone" type="text" class="input w-full" />
        </div>
        <div class="sm:col-span-2">
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Perfil de acesso</label>
          <input
            :value="perfilLabel"
            type="text"
            disabled
            class="input w-full opacity-70 cursor-not-allowed bg-gray-50 dark:bg-gray-900"
          />
        </div>
        <div class="sm:col-span-2">
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Unidade administrativa</label>
          <input
            :value="unidadeLabel"
            type="text"
            disabled
            class="input w-full opacity-70 cursor-not-allowed bg-gray-50 dark:bg-gray-900"
          />
        </div>
      </div>
      <button
        type="submit"
        :disabled="salvando"
        class="btn-primary px-6 py-2.5"
      >
        {{ salvando ? 'Salvando…' : 'Salvar alterações' }}
      </button>
    </form>

    <form v-else class="space-y-5 max-w-md" @submit.prevent="alterarSenha">
      <div>
        <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Senha atual</label>
        <input v-model="formSenha.senha_atual" type="password" required class="input w-full" />
      </div>
      <div>
        <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Nova senha</label>
        <input v-model="formSenha.nova_senha" type="password" required minlength="8" class="input w-full" />
      </div>
      <div>
        <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-1.5">Confirmar nova senha</label>
        <input
          v-model="formSenha.confirmar_nova_senha"
          type="password"
          required
          minlength="8"
          class="input w-full"
        />
      </div>
      <button
        type="submit"
        :disabled="salvandoSenha"
        class="btn-primary px-6 py-2.5"
      >
        {{ salvandoSenha ? 'Atualizando…' : 'Alterar senha' }}
      </button>
    </form>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { useAuthStore } from '@/stores/auth'
import { usuarioService } from '@/services/api'
import { getApiErrorMessage } from '@/utils/apiError'

const authStore = useAuthStore()
const aba = ref('dados')
const salvando = ref(false)
const salvandoSenha = ref(false)
const mensagem = ref('')
const mensagemErro = ref(false)

const formDados = ref({ nome: '', email: '', telefone: '' })
const formSenha = ref({
  senha_atual: '',
  nova_senha: '',
  confirmar_nova_senha: ''
})

const perfilLabel = computed(() => {
  const p = authStore.user?.perfil
  return p ? `${p.nome} (${p.codigo || '—'})` : '—'
})

const unidadeLabel = computed(() => {
  const u = authStore.user?.unidade_administrativa
  return u ? `${u.nome}${u.sigla ? ` · ${u.sigla}` : ''}` : '—'
})

function preencherForm() {
  const u = authStore.user
  if (!u) return
  formDados.value = {
    nome: u.nome || '',
    email: u.email || '',
    telefone: u.telefone || ''
  }
}

onMounted(async () => {
  await authStore.refreshPerfil().catch(() => {})
  preencherForm()
})

async function salvarDados() {
  salvando.value = true
  mensagem.value = ''
  try {
    const data = await usuarioService.atualizarPerfil({
      nome: formDados.value.nome,
      email: formDados.value.email,
      telefone: formDados.value.telefone
    })
    authStore.atualizarUsuarioPerfil(data)
    mensagemErro.value = false
    mensagem.value = 'Dados atualizados com sucesso.'
  } catch (e) {
    mensagemErro.value = true
    mensagem.value = getApiErrorMessage(e, 'Não foi possível salvar.')
  } finally {
    salvando.value = false
  }
}

async function alterarSenha() {
  if (formSenha.value.nova_senha !== formSenha.value.confirmar_nova_senha) {
    mensagemErro.value = true
    mensagem.value = 'A confirmação não coincide com a nova senha.'
    return
  }
  salvandoSenha.value = true
  mensagem.value = ''
  try {
    await usuarioService.alterarSenha(formSenha.value)
    formSenha.value = { senha_atual: '', nova_senha: '', confirmar_nova_senha: '' }
    mensagemErro.value = false
    mensagem.value = 'Senha alterada com sucesso.'
  } catch (e) {
    mensagemErro.value = true
    mensagem.value = getApiErrorMessage(e, 'Não foi possível alterar a senha.')
  } finally {
    salvandoSenha.value = false
  }
}
</script>