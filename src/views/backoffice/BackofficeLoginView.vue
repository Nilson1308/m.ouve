<template>
  <div
    class="min-h-screen flex items-center justify-center p-6 relative overflow-hidden bg-gradient-to-br from-slate-950 via-slate-900 to-indigo-950"
  >
    <div
      class="absolute inset-0 opacity-[0.06] pointer-events-none"
      style="
        background-image: radial-gradient(circle at 1px 1px, rgb(148 163 184) 1px, transparent 0);
        background-size: 28px 28px;
      "
      aria-hidden="true"
    />
    <div class="absolute top-6 right-6 z-20">
      <ThemeToggle surface="dark" />
    </div>

    <div class="w-full max-w-md relative z-10">
      <div class="text-center mb-8">
        <img
          :src="BRAND.logos.dark"
          :alt="BRAND.name"
          class="h-14 mx-auto object-contain mb-4"
        />
        <p class="text-xs uppercase tracking-[0.2em] text-cyan-400/90 font-semibold">Backoffice</p>
        <h1 class="text-2xl font-bold text-white mt-2">Acesso de servidores</h1>
        <p class="text-sm text-slate-400 mt-2">CPF e senha corporativa</p>
      </div>

      <form
        class="rounded-2xl border border-slate-700/60 bg-slate-900/70 backdrop-blur-xl shadow-2xl p-8 space-y-5"
        @submit.prevent="entrar"
      >
        <div
          v-if="authStore.error"
          class="p-3 rounded-lg bg-red-950/50 border border-red-800/60 text-sm text-red-200"
        >
          {{ authStore.error }}
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1.5">CPF</label>
          <input
            v-model="cpf"
            type="text"
            inputmode="numeric"
            autocomplete="username"
            required
            class="input w-full bg-slate-950/50 border-slate-600 text-white"
            placeholder="000.000.000-00"
          />
        </div>

        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1.5">Senha</label>
          <input
            v-model="senha"
            type="password"
            autocomplete="current-password"
            required
            class="input w-full bg-slate-950/50 border-slate-600 text-white"
          />
        </div>

        <button
          type="submit"
          :disabled="authStore.loading"
          class="w-full py-3 rounded-xl bg-gradient-to-r from-cyan-600 to-primary-600 hover:from-cyan-500 hover:to-primary-500 text-white font-bold text-sm transition-all disabled:opacity-50"
        >
          {{ authStore.loading ? 'Entrando…' : 'Entrar no Backoffice' }}
        </button>

        <p class="text-center text-xs text-slate-500">
          É cidadão?
          <router-link to="/app/login" class="text-cyan-400 hover:text-cyan-300 font-medium">
            Acesse o aplicativo
          </router-link>
        </p>
      </form>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { useRouter } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { BRAND } from '@/constants/brand'
import ThemeToggle from '@/components/shared/ThemeToggle.vue'

const router = useRouter()
const authStore = useAuthStore()
const cpf = ref('')
const senha = ref('')

async function entrar() {
  const result = await authStore.login(cpf.value, senha.value)
  if (!result.success) return

  if (!authStore.isBackoffice) {
    authStore.error =
      'Esta conta não possui perfil de servidor ou permissões no backoffice. Use o login do aplicativo.'
    await authStore.logout()
    return
  }

  const destino = (router.currentRoute.value.query.redirect || '/backoffice/mesa-trabalho')
  router.push(typeof destino === 'string' ? destino : '/backoffice/mesa-trabalho')
}
</script>