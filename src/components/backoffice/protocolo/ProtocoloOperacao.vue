<template>
  <div class="space-y-6">
    <section
      v-if="integradoSuperOs"
      class="card border-2 border-primary-300 dark:border-primary-600 bg-gradient-to-br from-primary-50/80 via-white to-purple-50/50 dark:from-primary-950/40 dark:via-gray-800 dark:to-purple-950/30 p-6"
    >
      <div class="flex items-start gap-3">
        <div
          class="flex h-10 w-10 shrink-0 items-center justify-center rounded-lg bg-gradient-to-br from-primary-500 to-purple-600 text-white text-lg"
          aria-hidden="true"
        >
          🔒
        </div>
        <div class="flex-1">
          <h2 class="text-base font-bold text-gray-900 dark:text-white mb-1">
            Protocolo integrado à Super OS
          </h2>
          <p class="text-sm text-gray-700 dark:text-gray-300 leading-relaxed mb-4">
            Gestão transferida ao incidente mestre
            <strong v-if="superOsCodigo" class="text-primary-700 dark:text-primary-300">
              {{ superOsCodigo }}
            </strong>.
            Despacho, validação e scatter individual estão bloqueados nesta tela.
          </p>
          <RouterLink
            v-if="superOsLink"
            :to="superOsLink"
            class="inline-flex w-full items-center justify-center gap-2 rounded-xl px-5 py-4 text-base font-bold text-white bg-gradient-to-r from-orange-500 via-red-500 to-purple-600 shadow-lg hover:shadow-xl hover:scale-[1.01] transition-all"
          >
            <span aria-hidden="true">🔗</span>
            Ir para Gestão da Super OS #{{ superOsCodigo || '—' }}
          </RouterLink>
        </div>
      </div>
    </section>

    <template v-else>
    <TriagemSugeridaCard
      :triagem="protocolo.triagemSugerida"
      :pode-despachar="podeDespacharTriagem"
      @preencher-despacho="$emit('preencher-despacho', $event)"
    />

    <!-- Validação: só no gather completo -->
    <AcoesValidacao
      v-if="prontoParaValidacao"
      :protocolo="protocolo"
      :salvando-validacao="salvandoValidacao"
      :salvando-devolucao="salvandoDevolucao"
      @validar="$emit('validar', $event)"
      @devolver="$emit('devolver', $event)"
    />

  <div
    v-else
    class="card border border-dashed border-gray-300 dark:border-gray-600 bg-gray-50/50 dark:bg-gray-800/40 p-5"
  >
    <p class="text-sm font-medium text-gray-800 dark:text-gray-200 mb-1">
      Validação final indisponível
    </p>
    <p class="text-xs text-gray-600 dark:text-gray-400 leading-relaxed">
      O despacho ao cidadão e o encerramento do protocolo ficam disponíveis em
      <strong>Aguardando validação</strong>, quando todos os nós do scatter-gather estiverem encerrados
      ({{ nosResumo.fechados }}/{{ nosResumo.total }}).
    </p>
  </div>

    <BackofficeAccordion
      titulo="Ordens de Serviço"
      :subtitulo="`Scatter-Gather · ${nosResumo.fechados}/${nosResumo.total} nós encerrados`"
      :icon="ClipboardDocumentListIcon"
      icon-wrapper-class="bg-warning-100 dark:bg-warning-900"
      icon-class="text-warning-600 dark:text-warning-400"
      :default-open="false"
      ajuda="Cada nó representa uma secretaria acionada. Acompanhe formalização e execução aqui."
    >
      <div class="flex justify-end mb-4">
        <button
          v-if="!prontoParaValidacao"
          type="button"
          class="btn-primary btn-sm shrink-0"
          title="Acionar nova secretaria neste protocolo"
          @click="$emit('adicionar-setor')"
        >
          <PlusIcon class="w-4 h-4 mr-1" />
          Adicionar Novo Setor
        </button>
      </div>

      <ul
        v-if="protocolo.ordens_servico?.length"
        class="mb-6 space-y-2 rounded-lg border border-gray-200 dark:border-gray-700 bg-gray-50/80 dark:bg-gray-800/50 p-3"
      >
        <li
          v-for="ordem in protocolo.ordens_servico"
          :key="'no-' + ordem.id"
          class="flex flex-wrap items-center justify-between gap-2 text-sm"
        >
          <span class="font-medium text-gray-900 dark:text-white">
            {{ nomeSecretariaNo(ordem) }}:
          </span>
          <span
            class="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-badge text-xs font-semibold"
            :class="
              noFechado(ordem)
                ? 'bg-emerald-100 text-emerald-800 dark:bg-emerald-900/40 dark:text-emerald-200'
                : 'bg-amber-100 text-amber-900 dark:bg-amber-900/30 dark:text-amber-200'
            "
          >
            <LockClosedIcon v-if="noFechado(ordem)" class="w-3.5 h-3.5" aria-hidden="true" />
            {{ emojiStatusNo(ordem) }}
            {{ noFechado(ordem) ? 'Concluído' : 'Pendente' }}
            <span class="font-normal opacity-90">({{ legendaStatusNo(ordem) }})</span>
          </span>
        </li>
      </ul>

      <div class="relative border-l-2 border-gray-200 dark:border-gray-700 ml-5 pl-6 space-y-8">
        <OrdemServicoItem
          v-for="(ordem, index) in protocolo.ordens_servico"
          :key="ordem.id"
          :ordem="ordem"
          :index="index"
          variant="revisao"
        />
      </div>
    </BackofficeAccordion>

    <BackofficeAccordion
      titulo="Resumo executivo"
      subtitulo="Indicadores rápidos do protocolo"
      :default-open="false"
      ajuda="Visão condensada de status, SLA e nós — ideal para checagem rápida."
    >
      <div class="space-y-2 rounded-lg bg-gradient-to-br from-gray-50 to-gray-100 dark:from-gray-800 dark:to-gray-900/80 border border-gray-200 dark:border-gray-700 p-4">
        <div class="flex items-center justify-between gap-3 text-sm">
          <span class="text-gray-600 dark:text-gray-400 shrink-0">Status Geral:</span>
          <StatusBadge :status="protocolo.status" tipo="zeladoria" :show-icon="true" />
        </div>
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-600 dark:text-gray-400">Nós encerrados:</span>
          <span class="font-semibold text-gray-900 dark:text-white">
            {{ nosResumo.fechados }} de {{ nosResumo.total }}
          </span>
        </div>
        <div v-if="ordensEmFormalizacao > 0" class="flex items-center justify-between text-sm">
          <span class="text-gray-600 dark:text-gray-400">Aguard. formalização:</span>
          <span class="font-semibold text-indigo-700 dark:text-indigo-300">
            {{ ordensEmFormalizacao }}
          </span>
        </div>
        <div class="flex items-center justify-between text-sm">
          <span class="text-gray-600 dark:text-gray-400">Tempo em atendimento:</span>
          <span class="font-semibold text-gray-900 dark:text-white">
            {{ tempoEmAtendimento }}
          </span>
        </div>
        <div v-if="slaResumo" class="flex items-center justify-between text-sm pt-1 border-t border-gray-200 dark:border-gray-600">
          <span class="text-gray-600 dark:text-gray-400">SLA:</span>
          <span class="font-medium" :class="slaResumo.classe">{{ slaResumo.texto }}</span>
        </div>
      </div>
    </BackofficeAccordion>
    </template>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ClipboardDocumentListIcon, PlusIcon, LockClosedIcon } from '@heroicons/vue/24/outline'
import StatusBadge from '@/components/shared/StatusBadge.vue'
import AcoesValidacao from './AcoesValidacao.vue'
import OrdemServicoItem from './OrdemServicoItem.vue'
import BackofficeAccordion from '@/components/backoffice/BackofficeAccordion.vue'
import TriagemSugeridaCard from '@/components/backoffice/protocolo/TriagemSugeridaCard.vue'
import {
  resumoNos,
  noFechado,
  emojiStatusNo,
  legendaStatusNo,
  nomeSecretariaNo,
  protocoloAguardandoValidacao
} from '@/utils/scatterGather'

const props = defineProps({
  protocolo: {
    type: Object,
    required: true
  },
  salvandoValidacao: {
    type: Boolean,
    default: false
  },
  salvandoDevolucao: {
    type: Boolean,
    default: false
  },
  integradoSuperOs: {
    type: Boolean,
    default: false
  },
  superOsCodigo: {
    type: String,
    default: ''
  },
  superOsId: {
    type: String,
    default: ''
  }
})

const superOsLink = computed(() => {
  const id = props.superOsId || props.protocolo?.superOsId
  if (!id) return null
  return { name: 'backoffice-super-os-detalhes', params: { id } }
})

defineEmits(['validar', 'devolver', 'adicionar-setor', 'preencher-despacho'])

const podeDespacharTriagem = computed(() => {
  const s = props.protocolo?.status
  return s === 'em_analise' || s === 'em_andamento'
})

const prontoParaValidacao = computed(() => protocoloAguardandoValidacao(props.protocolo))

const STATUS_PROTOCOLO_ENCERRADO = new Set([
  'concluido',
  'resolvido',
  'nao_procedente',
  'rejeitado',
  'arquivado'
])

const nosResumo = computed(() => resumoNos(props.protocolo.ordens_servico))

function statusOs(ordem) {
  return ordem.statusApi || ordem.status
}

const ordensEmFormalizacao = computed(() => {
  return (props.protocolo.ordens_servico || []).filter(
    (o) => statusOs(o) === 'aguardando_formalizacao'
  ).length
})

function parseDataIso(valor) {
  if (!valor) return null
  const d = new Date(valor)
  return Number.isNaN(d.getTime()) ? null : d
}

const tempoEmAtendimento = computed(() => {
  const inicio = parseDataIso(props.protocolo.criadoEm)
  if (!inicio) return '—'

  const encerrado = STATUS_PROTOCOLO_ENCERRADO.has(props.protocolo.status)
  let fim = encerrado ? parseDataIso(props.protocolo.atualizadoEm) : null

  if (!fim || fim < inicio) {
    const ordens = props.protocolo.ordens_servico || []
    const datasOrdens = ordens
      .map((o) => parseDataIso(o.concluido_em))
      .filter(Boolean)
    if (datasOrdens.length) {
      fim = new Date(Math.max(...datasOrdens.map((d) => d.getTime())))
    }
  }

  if (!fim || fim < inicio) {
    fim = new Date()
  }

  const diffMs = fim - inicio
  const diffHoras = Math.floor(diffMs / (1000 * 60 * 60))

  if (diffHoras < 1) {
    const min = Math.max(1, Math.floor(diffMs / (1000 * 60)))
    return `${min}min`
  }
  if (diffHoras < 24) {
    return `${diffHoras}h`
  }
  const dias = Math.floor(diffHoras / 24)
  const horas = diffHoras % 24
  return horas > 0 ? `${dias}d ${horas}h` : `${dias}d`
})

const slaResumo = computed(() => {
  const sla = props.protocolo.sla
  if (!sla) return null

  if (sla.vencido) {
    return { texto: 'SLA vencido', classe: 'text-red-600 dark:text-red-400' }
  }

  const horas = Number(sla.horasRestantes ?? 0)
  if (horas > 0) {
    return {
      texto: horas >= 24 ? `${Math.floor(horas / 24)}d restantes` : `${horas}h restantes`,
      classe: horas <= 6 ? 'text-amber-600 dark:text-amber-400' : 'text-green-600 dark:text-green-400'
    }
  }

  if (sla.prazo) {
    const prazo = parseDataIso(sla.prazo)
    if (prazo) {
      return {
        texto: prazo.toLocaleString('pt-BR', {
          day: '2-digit',
          month: '2-digit',
          hour: '2-digit',
          minute: '2-digit'
        }),
        classe: 'text-gray-800 dark:text-gray-200'
      }
    }
  }

  return null
})
</script>