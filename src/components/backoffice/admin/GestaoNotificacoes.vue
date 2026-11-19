<template>
  <div class="max-w-7xl space-y-8">
    <div>
      <h2 class="text-lg font-bold text-gray-900 dark:text-white">Central de Notificações</h2>
      <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
        Gatilhos automáticos, broadcast global e auditoria de envios internos
      </p>
    </div>

    <!-- Bloco 1: Gatilhos -->
    <section class="card p-6">
      <div class="flex items-start justify-between gap-4 mb-5">
        <div>
          <h3 class="text-base font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <BoltIcon class="w-5 h-5 text-amber-500" />
            Gatilhos globais (automações)
          </h3>
          <p class="text-sm text-gray-500 dark:text-gray-400 mt-1">
            Controla quando o sistema dispara notificações in-app automaticamente.
          </p>
        </div>
        <span
          v-if="salvandoGatilhos"
          class="text-xs text-primary-600 dark:text-primary-400 animate-pulse shrink-0"
        >
          Salvando…
        </span>
      </div>

      <div v-if="loadingConfig" class="py-8 flex justify-center">
        <div class="animate-spin rounded-full h-10 w-10 border-4 border-primary-500 border-t-transparent" />
      </div>

      <ul v-else class="divide-y divide-gray-200 dark:divide-gray-700">
        <li
          v-for="item in gatilhosUi"
          :key="item.campo"
          class="flex items-center justify-between gap-4 py-4 first:pt-0 last:pb-0"
        >
          <div>
            <p class="text-sm font-medium text-gray-900 dark:text-white">{{ item.titulo }}</p>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">{{ item.descricao }}</p>
          </div>
          <button
            type="button"
            role="switch"
            :aria-checked="configuracao?.[item.campo]"
            :disabled="!configuracao || salvandoGatilhos"
            :class="[
              'relative inline-flex h-6 w-11 shrink-0 cursor-pointer rounded-full border-2 border-transparent transition-colors disabled:opacity-50',
              configuracao?.[item.campo] ? 'bg-primary-600' : 'bg-gray-300 dark:bg-gray-600'
            ]"
            @click="alternarGatilho(item.campo)"
          >
            <span
              :class="[
                'pointer-events-none inline-block h-5 w-5 transform rounded-full bg-white shadow transition',
                configuracao?.[item.campo] ? 'translate-x-5' : 'translate-x-0'
              ]"
            />
          </button>
        </li>
      </ul>
    </section>

    <!-- Bloco 2: Broadcast -->
    <section class="card p-6">
      <h3 class="text-base font-semibold text-gray-900 dark:text-white flex items-center gap-2 mb-5">
        <MegaphoneIcon class="w-5 h-5 text-cyan-600" />
        Disparo de broadcast (aviso global)
      </h3>

      <form class="space-y-4 max-w-2xl" @submit.prevent="enviarBroadcast">
        <div>
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Título *</label>
          <input v-model="broadcast.titulo" type="text" required class="input" placeholder="Ex.: Manutenção programada" />
        </div>
        <div>
          <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Mensagem *</label>
          <textarea
            v-model="broadcast.mensagem"
            rows="4"
            required
            class="input resize-none"
            placeholder="Texto exibido na central de notificações dos servidores"
          />
        </div>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Urgência</label>
            <select v-model="broadcast.nivel_urgencia" class="input">
              <option value="normal">Normal</option>
              <option value="alta">Alta</option>
            </select>
          </div>
          <div>
            <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">Destino</label>
            <select v-model="broadcast.unidade_alvo_id" class="input">
              <option value="">Todas as unidades / Global</option>
              <option v-for="u in unidadesAtivas" :key="u.id" :value="u.id">
                {{ u.sigla ? `${u.sigla} — ` : '' }}{{ u.nome }}
              </option>
            </select>
          </div>
        </div>
        <div class="flex justify-end pt-2">
          <button
            type="submit"
            class="btn-primary inline-flex items-center gap-2"
            :disabled="loadingBroadcast || !broadcastValido"
          >
            <PaperAirplaneIcon class="w-5 h-5" />
            {{ loadingBroadcast ? 'Disparando…' : 'Disparar Aviso' }}
          </button>
        </div>
      </form>
    </section>

    <!-- Bloco 3: Auditoria -->
    <section class="card overflow-hidden">
      <div class="p-6 border-b border-gray-200 dark:border-gray-700">
        <h3 class="text-base font-semibold text-gray-900 dark:text-white flex items-center gap-2 mb-4">
          <ClipboardDocumentListIcon class="w-5 h-5 text-gray-600 dark:text-gray-400" />
          Auditoria de notificações
        </h3>
        <div class="flex flex-col sm:flex-row gap-3">
          <select v-model="filtroLida" class="input sm:max-w-xs" @change="recarregarAuditoria">
            <option value="">Todas (status)</option>
            <option value="nao_lida">Não lidas</option>
            <option value="lida">Lidas</option>
          </select>
          <div class="relative flex-1">
            <MagnifyingGlassIcon class="w-5 h-5 text-gray-400 absolute left-3 top-1/2 -translate-y-1/2 pointer-events-none" />
            <input
              v-model="buscaDestinatario"
              type="search"
              class="input pl-10"
              placeholder="Buscar por nome do destinatário…"
              @input="debounceBusca"
            />
          </div>
        </div>
      </div>

      <div v-if="loadingAuditoria && !auditoria.length" class="p-12 flex flex-col items-center">
        <div class="animate-spin rounded-full h-10 w-10 border-4 border-primary-500 border-t-transparent" />
        <p class="text-sm text-gray-500 mt-3">Carregando auditoria…</p>
      </div>

      <div v-else class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
            <tr>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">Data/Hora</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">Destinatário</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">Título</th>
              <th class="px-6 py-3 text-left text-xs font-semibold text-gray-600 dark:text-gray-400 uppercase">Leitura</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr v-for="row in auditoria" :key="row.id" class="hover:bg-gray-50 dark:hover:bg-gray-800/50">
              <td class="px-6 py-4 text-sm text-gray-700 dark:text-gray-300 whitespace-nowrap">
                {{ formatarDataHora(row.data_criacao) }}
              </td>
              <td class="px-6 py-4">
                <p class="text-sm font-medium text-gray-900 dark:text-white">{{ row.usuario_destino_nome }}</p>
                <p class="text-xs text-gray-500 dark:text-gray-400">
                  {{ row.unidade_destino_nome || 'Mesa / sem unidade' }}
                </p>
              </td>
              <td class="px-6 py-4 text-sm text-gray-800 dark:text-gray-200 max-w-md truncate" :title="row.titulo">
                {{ row.titulo }}
              </td>
              <td class="px-6 py-4">
                <span
                  :class="[
                    'inline-flex px-2.5 py-1 rounded-badge text-xs font-semibold',
                    row.lida
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/40 dark:text-green-300'
                      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300'
                  ]"
                >
                  {{ row.lida ? 'Lida' : 'Não lida' }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
      </div>

      <div v-if="!loadingAuditoria && auditoria.length === 0" class="p-12 text-center text-sm text-gray-500">
        Nenhuma notificação encontrada com os filtros atuais.
      </div>

      <div
        v-if="auditoriaNext"
        class="p-4 border-t border-gray-200 dark:border-gray-700 flex justify-center"
      >
        <button type="button" class="btn-secondary text-sm" :disabled="loadingAuditoria" @click="carregarMais">
          {{ loadingAuditoria ? 'Carregando…' : 'Carregar mais' }}
        </button>
      </div>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue'
import { storeToRefs } from 'pinia'
import {
  BoltIcon,
  MegaphoneIcon,
  PaperAirplaneIcon,
  ClipboardDocumentListIcon,
  MagnifyingGlassIcon
} from '@heroicons/vue/24/outline'
import { useNotificacoesAdminStore } from '@/stores/notificacoesAdmin'
import { useAdminStore } from '@/stores/admin'
import { useAdminToast } from '@/composables/useAdminToast'

const notifStore = useNotificacoesAdminStore()
const adminStore = useAdminStore()
const { mostrarToast } = useAdminToast()

const {
  configuracao,
  loadingConfig,
  salvandoGatilhos,
  auditoria,
  auditoriaNext,
  loadingAuditoria,
  loadingBroadcast
} = storeToRefs(notifStore)
const { unidadesAtivas } = storeToRefs(adminStore)

const gatilhosUi = [
  {
    campo: 'notificar_novos_despachos',
    titulo: 'Notificar novos despachos',
    descricao: 'Scatter para a secretaria ao despachar protocolos na mesa.'
  },
  {
    campo: 'notificar_sla_vencido',
    titulo: 'Notificar SLA vencido',
    descricao: 'Job automático alerta responsáveis quando o prazo estoura.'
  },
  {
    campo: 'notificar_novas_super_os',
    titulo: 'Notificar novas Super OS',
    descricao: 'Avisos ao despachar ordens vinculadas a uma Super OS.'
  }
]

const broadcast = ref({
  titulo: '',
  mensagem: '',
  nivel_urgencia: 'normal',
  unidade_alvo_id: ''
})

const filtroLida = ref('')
const buscaDestinatario = ref('')
const paginaAuditoria = ref(1)
let buscaTimer = null

const broadcastValido = computed(
  () => Boolean(broadcast.value.titulo?.trim()) && Boolean(broadcast.value.mensagem?.trim())
)

function formatarDataHora(iso) {
  if (!iso) return '—'
  try {
    return new Date(iso).toLocaleString('pt-BR', {
      day: '2-digit',
      month: '2-digit',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return iso
  }
}

function paramsAuditoria() {
  let lida = null
  if (filtroLida.value === 'lida') lida = true
  if (filtroLida.value === 'nao_lida') lida = false
  return {
    page: paginaAuditoria.value,
    lida,
    busca: buscaDestinatario.value
  }
}

async function recarregarAuditoria() {
  paginaAuditoria.value = 1
  await notifStore.carregarAuditoria(paramsAuditoria()).catch(() => {})
}

function debounceBusca() {
  if (buscaTimer) clearTimeout(buscaTimer)
  buscaTimer = setTimeout(() => {
    recarregarAuditoria()
  }, 400)
}

async function carregarMais() {
  paginaAuditoria.value += 1
  await notifStore.carregarAuditoria(paramsAuditoria()).catch(() => {})
}

async function alternarGatilho(campo) {
  if (!configuracao.value) return
  const valorAtual = Boolean(configuracao.value[campo])
  try {
    await notifStore.atualizarGatilhos({ [campo]: !valorAtual })
    mostrarToast('Gatilho atualizado.')
  } catch {
    mostrarToast(notifStore.erro || 'Erro ao salvar gatilho.', true)
  }
}

async function enviarBroadcast() {
  try {
    const res = await notifStore.dispararBroadcast({ ...broadcast.value })
    mostrarToast(
      `Aviso enviado para ${res.criadas ?? 0} servidor(es).`
    )
    broadcast.value = {
      titulo: '',
      mensagem: '',
      nivel_urgencia: 'normal',
      unidade_alvo_id: ''
    }
    await recarregarAuditoria()
  } catch {
    mostrarToast(notifStore.erro || 'Erro ao disparar aviso.', true)
  }
}

onMounted(async () => {
  notifStore.carregarConfiguracao().catch(() => {})
  if (!unidadesAtivas.value.length) {
    adminStore.carregarUnidades({ silencioso: true }).catch(() => {})
  }
  recarregarAuditoria()
})

onUnmounted(() => {
  if (buscaTimer) clearTimeout(buscaTimer)
})
</script>