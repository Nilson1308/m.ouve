<template>
  <div class="min-h-full bg-gray-50 dark:bg-gray-900 px-4 sm:px-6 lg:px-8 py-6">
    <header class="mb-6 flex flex-col lg:flex-row lg:items-end lg:justify-between gap-4">
      <div>
        <h1 class="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <ClockIcon class="w-8 h-8 text-amber-600" />
          SLA & Cobranças
        </h1>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Protocolos em atraso, cobranças do cidadão e histórico de envios digest.
        </p>
      </div>
      <div class="flex border border-gray-200 dark:border-gray-700 rounded-button p-1 bg-white dark:bg-gray-800">
        <button
          type="button"
          class="px-4 py-2 text-sm font-medium rounded-button min-h-[44px]"
          :class="aba === 'atrasados' ? 'bg-primary-600 text-white' : 'text-gray-600 dark:text-gray-300'"
          @click="aba = 'atrasados'"
        >
          Protocolos em atraso
        </button>
        <button
          type="button"
          class="px-4 py-2 text-sm font-medium rounded-button min-h-[44px]"
          :class="aba === 'envios' ? 'bg-primary-600 text-white' : 'text-gray-600 dark:text-gray-300'"
          @click="aba = 'envios'; carregarEnvios()"
        >
          Histórico de envios
        </button>
      </div>
    </header>

    <template v-if="aba === 'atrasados'">
      <div v-if="resumo" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div class="card p-4 border-l-4 border-amber-500">
          <p class="text-xs uppercase font-semibold text-gray-500">Total em atraso</p>
          <p class="text-3xl font-bold text-gray-900 dark:text-white">{{ resumo.total_atrasados }}</p>
        </div>
        <div class="card p-4 border-l-4 border-rose-600">
          <p class="text-xs uppercase font-semibold text-gray-500">Críticos em aberto</p>
          <p class="text-3xl font-bold text-rose-800 dark:text-rose-200">
            {{ resumo.total_criticos_abertos ?? 0 }}
          </p>
        </div>
        <div class="card p-4 border-l-4 border-red-500">
          <p class="text-xs uppercase font-semibold text-gray-500">Com cobrança do cidadão</p>
          <p class="text-3xl font-bold text-red-700 dark:text-red-300">{{ resumo.total_com_cobranca }}</p>
        </div>
        <div class="card p-4 border-l-4 border-purple-500">
          <p class="text-xs uppercase font-semibold text-gray-500">Escalonados à controladoria</p>
          <p class="text-3xl font-bold text-purple-800 dark:text-purple-200">{{ resumo.total_escalonados }}</p>
        </div>
      </div>

      <div v-if="resumo?.por_unidade?.length" class="card p-4 mb-6 overflow-x-auto">
        <h2 class="text-sm font-semibold text-gray-800 dark:text-gray-200 mb-3">Resumo por secretaria</h2>
        <table class="w-full text-sm">
          <thead>
            <tr class="text-left text-xs uppercase text-gray-500">
              <th class="pb-2">Secretaria</th>
              <th class="pb-2">Atrasados</th>
              <th class="pb-2">Com cobrança</th>
            </tr>
          </thead>
          <tbody>
            <tr
              v-for="u in resumo.por_unidade"
              :key="u.unidade_id"
              class="border-t border-gray-100 dark:border-gray-800 cursor-pointer hover:bg-gray-50 dark:hover:bg-gray-800/50"
              @click="aplicarUnidade(u.unidade_id)"
            >
              <td class="py-2 font-medium text-primary-700 dark:text-primary-300">{{ u.nome }}</td>
              <td class="py-2">{{ u.total }}</td>
              <td class="py-2">{{ u.com_cobranca }}</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="card p-4 mb-4 flex flex-wrap gap-3 items-end">
        <div class="w-full sm:w-auto min-w-[160px]">
          <label class="text-xs font-medium text-gray-500 block mb-1">Secretaria</label>
          <select v-model="filtros.unidade_id" class="input w-full text-sm">
            <option value="">Todas</option>
            <option v-for="u in unidades" :key="u.id" :value="u.id">{{ u.sigla || u.nome }}</option>
          </select>
        </div>
        <div class="w-full sm:w-auto min-w-[160px]">
          <label class="text-xs font-medium text-gray-500 block mb-1">Serviço</label>
          <select v-model="filtros.servico_id" class="input w-full text-sm">
            <option value="">Todos</option>
            <option v-for="s in servicos" :key="s.id" :value="s.id">{{ s.nome }}</option>
          </select>
        </div>
        <div class="w-full sm:min-w-[200px] sm:flex-1">
          <label class="text-xs font-medium text-gray-500 block mb-1">Equipamento</label>
          <input
            v-model="buscaEquipamento"
            type="search"
            class="input w-full text-sm mb-1"
            placeholder="Buscar equipamento…"
            autocomplete="off"
          />
          <select v-model="filtros.equipamento_id" class="input w-full text-sm">
            <option value="">Qualquer</option>
            <option v-for="eq in equipamentosOpcoes" :key="eq.id" :value="eq.id">
              {{ eq.nome }}{{ eq.bairro ? ` · ${eq.bairro}` : '' }}
            </option>
          </select>
        </div>
        <div class="w-full sm:w-auto min-w-[120px]">
          <label class="text-xs font-medium text-gray-500 block mb-1">Dias mín.</label>
          <input v-model.number="filtros.dias_atraso_min" type="number" min="0" class="input w-full text-sm" />
        </div>
        <label class="flex items-center gap-2 min-h-[44px] cursor-pointer">
          <input v-model="filtros.apenas_cobrados" type="checkbox" class="rounded text-primary-600 w-4 h-4" />
          <span class="text-sm">Apenas cobrados</span>
        </label>
        <div>
          <label class="text-xs font-medium text-gray-500 block mb-1">Ordenação</label>
          <select v-model="filtros.ordenacao" class="input text-sm">
            <option value="atraso_desc">Maior atraso</option>
            <option value="cobrancas_desc">Mais cobranças</option>
          </select>
        </div>
        <button type="button" class="btn-primary min-h-[44px]" @click="pagina = 1; carregarAtrasados()">Filtrar</button>
      </div>

      <div class="flex flex-wrap gap-2 mb-4">
        <button type="button" class="btn-secondary min-h-[44px]" :disabled="exportando" @click="exportarCsv">
          {{ exportando ? 'Exportando…' : 'Exportar CSV' }}
        </button>
        <button type="button" class="btn-primary min-h-[44px]" @click="modalDisparo = true">
          Disparar relatório agora
        </button>
      </div>

      <p v-if="carregando" class="text-sm text-gray-500 py-8 text-center">Carregando protocolos…</p>

      <div v-else class="card overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 dark:bg-gray-800 text-xs uppercase text-gray-500">
            <tr>
              <th class="px-4 py-3 text-left">Protocolo</th>
              <th class="px-4 py-3 text-left">Serviço</th>
              <th class="px-4 py-3 text-left">Urgência</th>
              <th class="px-4 py-3 text-left">Secretaria</th>
              <th class="px-4 py-3 text-left">Equipamento</th>
              <th class="px-4 py-3 text-left">Responsável</th>
              <th class="px-4 py-3 text-left">Atraso</th>
              <th class="px-4 py-3 text-left">Cobranças</th>
              <th class="px-4 py-3 text-left">Alerta</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
            <tr
              v-for="row in resultados"
              :key="row.protocolo_id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800/50 cursor-pointer"
              @click="irProtocolo(row.codigo)"
            >
              <td class="px-4 py-3 font-mono text-primary-600 dark:text-primary-400">{{ row.codigo }}</td>
              <td class="px-4 py-3 max-w-[12rem] truncate">{{ row.servico_nome }}</td>
              <td class="px-4 py-3">
                <UrgenciaBadge :nivel="row.urgencia" size="sm" />
              </td>
              <td class="px-4 py-3 max-w-[10rem] truncate">{{ row.unidade_nome }}</td>
              <td class="px-4 py-3 max-w-[8rem] truncate">{{ row.equipamento || '—' }}</td>
              <td class="px-4 py-3 max-w-[8rem] truncate">{{ row.responsavel_nome }}</td>
              <td class="px-4 py-3">
                <span :class="badgeAtraso(row.dias_atraso)" class="badge text-xs">{{ row.dias_atraso }}d</span>
              </td>
              <td class="px-4 py-3">
                <span
                  v-if="row.qtd_cobrancas_cidadao > 0"
                  class="inline-flex items-center gap-1 badge bg-amber-100 text-amber-900 dark:bg-amber-900/40 dark:text-amber-100"
                >
                  <BellAlertIcon class="w-3.5 h-3.5" />
                  {{ row.qtd_cobrancas_cidadao }}
                </span>
                <span v-else class="text-gray-400">0</span>
                <p v-if="row.ultima_cobranca_em" class="text-[10px] text-gray-500 mt-0.5">
                  {{ formatarData(row.ultima_cobranca_em) }}
                </p>
              </td>
              <td class="px-4 py-3">
                <span
                  :class="classeNivelAlertaSla(row.ultimo_alerta_sla_nivel)"
                  class="text-xs px-2 py-0.5 rounded-full border"
                >
                  {{ labelNivelAlertaSla(row.ultimo_alerta_sla_nivel) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="!resultados.length" class="text-center py-12 text-gray-500 text-sm">Nenhum protocolo encontrado.</p>
      </div>

      <div v-if="paginacao.total > paginacao.tamanho_pagina" class="flex justify-center gap-2 mt-4">
        <button
          type="button"
          class="btn-secondary"
          :disabled="pagina <= 1"
          @click="pagina--; carregarAtrasados()"
        >
          Anterior
        </button>
        <span class="text-sm text-gray-600 self-center">
          Página {{ pagina }} / {{ totalPaginas }}
        </span>
        <button
          type="button"
          class="btn-secondary"
          :disabled="pagina >= totalPaginas"
          @click="pagina++; carregarAtrasados()"
        >
          Próxima
        </button>
      </div>
    </template>

    <template v-else>
      <p v-if="carregandoEnvios" class="text-sm text-gray-500 py-8 text-center">Carregando…</p>
      <div v-else class="card overflow-x-auto">
        <table class="w-full text-sm">
          <thead class="bg-gray-50 dark:bg-gray-800 text-xs uppercase text-gray-500">
            <tr>
              <th class="px-4 py-3 text-left">Data</th>
              <th class="px-4 py-3 text-left">Tipo</th>
              <th class="px-4 py-3 text-left">Unidade</th>
              <th class="px-4 py-3 text-left">Destinatários</th>
              <th class="px-4 py-3 text-left">Protocolos</th>
              <th class="px-4 py-3 text-left">Cobrados</th>
              <th class="px-4 py-3 text-left">Status</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-100 dark:divide-gray-800">
            <tr v-for="e in envios" :key="e.id">
              <td class="px-4 py-3 whitespace-nowrap">{{ formatarData(e.criado_em) }}</td>
              <td class="px-4 py-3">{{ labelTipoEnvioSla(e.tipo) }}</td>
              <td class="px-4 py-3">{{ e.unidade || '—' }}</td>
              <td class="px-4 py-3">{{ (e.destinatarios || []).length }}</td>
              <td class="px-4 py-3">{{ e.total_protocolos }}</td>
              <td class="px-4 py-3">{{ e.total_cobrados }}</td>
              <td class="px-4 py-3">
                <span
                  :title="e.status === 'erro' ? e.erro_detalhe : ''"
                  class="text-xs font-medium"
                  :class="
                    e.status === 'enviado'
                      ? 'text-emerald-700'
                      : e.status === 'erro'
                        ? 'text-red-700 cursor-help underline decoration-dotted'
                        : 'text-gray-600'
                  "
                >
                  {{ labelStatusEnvioSla(e.status) }}
                </span>
              </td>
            </tr>
          </tbody>
        </table>
        <p v-if="!envios.length" class="text-center py-12 text-gray-500 text-sm">Nenhum envio registrado.</p>
      </div>
    </template>

    <Teleport to="body">
      <div
        v-if="modalDisparo"
        class="fixed inset-0 z-[80] flex items-center justify-center p-4 bg-black/50"
        @click.self="modalDisparo = false"
      >
        <div
          class="bg-white dark:bg-gray-900 w-full max-w-md rounded-modal shadow-float max-h-[90dvh] flex flex-col overflow-hidden border border-gray-200 dark:border-gray-700"
          role="dialog"
          aria-modal="true"
          aria-labelledby="titulo-disparo"
        >
          <div class="shrink-0 px-5 py-4 border-b border-gray-200 dark:border-gray-700">
            <h2 id="titulo-disparo" class="text-lg font-bold text-gray-900 dark:text-white">Disparar digest agora</h2>
          </div>
          <div class="flex-1 overflow-y-auto p-5 space-y-4">
            <div>
              <label class="text-sm font-medium text-gray-700 dark:text-gray-300 block mb-1">Unidade (opcional)</label>
              <select v-model="disparo.unidade_id" class="input w-full">
                <option value="">Todas com pendências</option>
                <option v-for="u in unidades" :key="u.id" :value="u.id">{{ u.nome }}</option>
              </select>
            </div>
            <label class="flex items-center gap-2 min-h-[44px] cursor-pointer">
              <input v-model="disparo.incluir_controladoria" type="checkbox" class="rounded text-primary-600" />
              <span class="text-sm">Incluir resumo da controladoria</span>
            </label>
            <pre v-if="resultadoDisparo" class="text-xs bg-gray-100 dark:bg-gray-800 p-3 rounded-lg overflow-auto max-h-40">{{ resultadoDisparo }}</pre>
            <p v-if="erroDisparo" class="text-sm text-red-600">{{ erroDisparo }}</p>
          </div>
          <div class="shrink-0 px-5 py-4 border-t border-gray-200 dark:border-gray-700 flex gap-2 justify-end bg-gray-50 dark:bg-gray-800/80">
            <button type="button" class="btn-secondary min-h-[44px]" @click="modalDisparo = false">Cancelar</button>
            <button type="button" class="btn-primary min-h-[44px]" :disabled="disparando" @click="confirmarDisparo">
              {{ disparando ? 'Enviando…' : 'Disparar' }}
            </button>
          </div>
        </div>
      </div>
    </Teleport>
  </div>
</template>

<script setup>
import { computed, onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { ClockIcon, BellAlertIcon } from '@heroicons/vue/24/outline'
import UrgenciaBadge from '@/components/backoffice/common/UrgenciaBadge.vue'
import { catalogoLookupService, slaCobrancaService } from '@/services/api'
import { useBackofficeStore } from '@/stores/backoffice'
import { getApiErrorMessage } from '@/utils/apiError'
import {
  classeNivelAlertaSla,
  labelNivelAlertaSla,
  labelStatusEnvioSla,
  labelTipoEnvioSla
} from '@/utils/slaAlertaLabels'

const router = useRouter()
const backofficeStore = useBackofficeStore()

const aba = ref('atrasados')
const carregando = ref(false)
const exportando = ref(false)
const resumo = ref(null)
const resultados = ref([])
const paginacao = ref({ pagina: 1, tamanho_pagina: 25, total: 0 })
const pagina = ref(1)

const filtros = reactive({
  unidade_id: '',
  servico_id: '',
  equipamento_id: '',
  apenas_cobrados: false,
  dias_atraso_min: null,
  ordenacao: 'atraso_desc'
})

const unidades = ref([])
const servicos = ref([])
const buscaEquipamento = ref('')
const equipamentosOpcoes = ref([])
let debounceEquip = null

const modalDisparo = ref(false)
const disparo = reactive({ unidade_id: '', incluir_controladoria: true })
const disparando = ref(false)
const resultadoDisparo = ref('')
const erroDisparo = ref('')

const carregandoEnvios = ref(false)
const envios = ref([])
const paginaEnvios = ref(1)

const totalPaginas = computed(() =>
  Math.max(1, Math.ceil((paginacao.value.total || 0) / (paginacao.value.tamanho_pagina || 25)))
)

watch(buscaEquipamento, () => {
  if (debounceEquip) clearTimeout(debounceEquip)
  debounceEquip = setTimeout(buscarEquipamentos, 300)
})

async function buscarEquipamentos() {
  try {
    const params = { limit: 20 }
    const q = buscaEquipamento.value.trim()
    if (q) params.busca = q
    equipamentosOpcoes.value = await catalogoLookupService.listarEquipamentos(params)
  } catch {
    equipamentosOpcoes.value = []
  }
}

onMounted(async () => {
  buscarEquipamentos()
  await Promise.all([
    backofficeStore.carregarUnidades().then((u) => {
      unidades.value = u || backofficeStore.unidades
    }),
    backofficeStore.carregarOpcoesFiltrosMesa().then((o) => {
      servicos.value = o?.servicos || []
    }),
    carregarAtrasados()
  ])
})

function paramsApi() {
  const p = {
    page: pagina.value,
    page_size: 25,
    ordenacao: filtros.ordenacao
  }
  if (filtros.unidade_id) p.unidade_id = filtros.unidade_id
  if (filtros.servico_id) p.servico_id = filtros.servico_id
  if (filtros.equipamento_id) p.equipamento_id = filtros.equipamento_id
  if (filtros.apenas_cobrados) p.apenas_cobrados = true
  if (filtros.dias_atraso_min != null && filtros.dias_atraso_min !== '') {
    p.dias_atraso_min = filtros.dias_atraso_min
  }
  return p
}

async function carregarAtrasados() {
  carregando.value = true
  try {
    const data = await slaCobrancaService.listarAtrasados(paramsApi())
    resumo.value = data.resumo
    resultados.value = data.resultados || []
    paginacao.value = data.paginacao || paginacao.value
    pagina.value = paginacao.value.pagina || pagina.value
  } catch (e) {
    console.error(getApiErrorMessage(e))
    resultados.value = []
  } finally {
    carregando.value = false
  }
}

function aplicarUnidade(id) {
  filtros.unidade_id = id
  pagina.value = 1
  carregarAtrasados()
}

function badgeAtraso(dias) {
  const d = Number(dias) || 0
  if (d >= 7) return 'bg-red-100 text-red-800 dark:bg-red-900/40 dark:text-red-200'
  if (d >= 3) return 'bg-orange-100 text-orange-900 dark:bg-orange-900/40 dark:text-orange-200'
  return 'bg-amber-100 text-amber-900 dark:bg-amber-900/40 dark:text-amber-200'
}

function formatarData(iso) {
  if (!iso) return '—'
  const d = new Date(iso)
  if (Number.isNaN(d.getTime())) return iso
  return d.toLocaleString('pt-BR', { day: '2-digit', month: '2-digit', year: 'numeric', hour: '2-digit', minute: '2-digit' })
}

function irProtocolo(codigo) {
  router.push({ name: 'backoffice-protocolo-detalhes', params: { id: codigo } })
}

async function exportarCsv() {
  exportando.value = true
  try {
    const p = { ...paramsApi() }
    delete p.page
    delete p.page_size
    const response = await slaCobrancaService.exportarAtrasadosCsv(p)
    const blob = new Blob([response.data], { type: 'text/csv;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = 'sla-atrasados.csv'
    a.click()
    URL.revokeObjectURL(url)
  } catch (e) {
    alert(getApiErrorMessage(e, 'Falha ao exportar CSV.'))
  } finally {
    exportando.value = false
  }
}

async function confirmarDisparo() {
  disparando.value = true
  erroDisparo.value = ''
  resultadoDisparo.value = ''
  try {
    const body = { incluir_controladoria: Boolean(disparo.incluir_controladoria) }
    if (disparo.unidade_id) body.unidade_id = disparo.unidade_id
    const data = await slaCobrancaService.dispararDigest(body)
    const linhas = (data.envios || []).map(
      (e) => `${labelTipoEnvioSla(e.tipo)} · ${e.status} · ${e.total_protocolos} protocolos`
    )
    resultadoDisparo.value = linhas.length ? linhas.join('\n') : 'Nenhum envio gerado.'
  } catch (e) {
    erroDisparo.value = getApiErrorMessage(e, 'Erro ao disparar.')
  } finally {
    disparando.value = false
  }
}

async function carregarEnvios() {
  carregandoEnvios.value = true
  try {
    const data = await slaCobrancaService.listarEnvios({ page: paginaEnvios.value, page_size: 20 })
    envios.value = data.resultados || []
  } catch {
    envios.value = []
  } finally {
    carregandoEnvios.value = false
  }
}
</script>