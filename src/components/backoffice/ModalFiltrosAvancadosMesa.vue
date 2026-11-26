<template>
  <Teleport to="body">
    <Transition name="fade">
      <div
        v-if="aberto"
        class="fixed inset-0 z-[70] flex items-end sm:items-center justify-center p-0 sm:p-4 bg-black/50 backdrop-blur-sm"
        @click.self="fechar"
      >
        <Transition name="slide-up">
          <div
            v-if="aberto"
            class="bg-white dark:bg-gray-900 w-full sm:max-w-2xl sm:rounded-modal shadow-float max-h-[92vh] flex flex-col border border-gray-200 dark:border-gray-700"
            role="dialog"
            aria-modal="true"
            aria-labelledby="filtros-mesa-titulo"
          >
            <div class="px-6 py-5 border-b border-gray-200 dark:border-gray-700 bg-gradient-to-r from-primary-500 to-primary-600 shrink-0 sm:rounded-t-modal">
              <div class="flex items-start justify-between gap-3">
                <div>
                  <h2 id="filtros-mesa-titulo" class="text-xl font-bold text-white">Filtros avançados</h2>
                  <p class="text-sm text-primary-100 mt-0.5">
                    Setor, serviço, local, status e urgência
                  </p>
                </div>
                <button
                  type="button"
                  class="text-white/80 hover:text-white p-1 rounded-lg hover:bg-white/10"
                  aria-label="Fechar"
                  @click="fechar"
                >
                  ✕
                </button>
              </div>
            </div>

            <div class="flex-1 overflow-y-auto p-6 space-y-6">
              <section>
                <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                  <BuildingOffice2Icon class="w-5 h-5 text-primary-500" />
                  Setor / secretaria responsável
                </h3>
                <input
                  v-model="buscaUnidade"
                  type="search"
                  class="input w-full mb-2 text-sm"
                  placeholder="Buscar secretaria…"
                />
                <div class="flex flex-wrap gap-2 max-h-36 overflow-y-auto p-1">
                  <button
                    v-for="u in unidadesFiltradas"
                    :key="u.id"
                    type="button"
                    class="badge text-xs px-3 py-1.5 transition-colors"
                    :class="
                      local.unidadesIds.includes(u.id)
                        ? 'bg-primary-600 text-white ring-2 ring-primary-400'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
                    "
                    @click="toggleItem(local.unidadesIds, u.id)"
                  >
                    {{ u.sigla || u.nome }}
                  </button>
                </div>
                <p v-if="!unidades.length" class="text-xs text-gray-500">Nenhuma unidade disponível.</p>
              </section>

              <section>
                <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                  <WrenchScrewdriverIcon class="w-5 h-5 text-primary-500" />
                  Serviço
                </h3>
                <input
                  v-model="buscaServico"
                  type="search"
                  class="input w-full mb-2 text-sm"
                  placeholder="Buscar serviço…"
                />
                <div class="flex flex-wrap gap-2 max-h-36 overflow-y-auto p-1">
                  <button
                    v-for="s in servicosFiltrados"
                    :key="s.id"
                    type="button"
                    class="badge text-xs px-3 py-1.5 max-w-[14rem] truncate transition-colors"
                    :class="
                      local.servicoIds.includes(s.id)
                        ? 'bg-primary-600 text-white ring-2 ring-primary-400'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                    "
                    :title="s.nome"
                    @click="toggleItem(local.servicoIds, s.id)"
                  >
                    {{ s.nome }}
                  </button>
                </div>
              </section>

              <section>
                <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                  <BuildingOffice2Icon class="w-5 h-5 text-primary-500" />
                  Equipamento público
                </h3>
                <input
                  v-model="buscaEquipamento"
                  type="search"
                  class="input w-full mb-2 text-sm"
                  placeholder="Buscar UBS, escola, CRAS..."
                  autocomplete="off"
                />
                <div v-if="loadingEquipamentosLookup" class="text-xs text-gray-500 py-2">Buscando...</div>
                <div
                  v-else
                  class="flex flex-col gap-1 max-h-40 overflow-y-auto p-0.5"
                  role="listbox"
                  aria-label="Equipamentos"
                >
                  <button
                    type="button"
                    class="text-left w-full min-h-[44px] px-3 py-2 rounded-lg text-sm transition-colors"
                    :class="
                      !local.equipamentoId
                        ? 'bg-primary-50 dark:bg-primary-950/40 text-primary-800 dark:text-primary-200 ring-1 ring-primary-300'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300'
                    "
                    @click="selecionarEquipamento('', '')"
                  >
                    Qualquer equipamento
                  </button>
                  <button
                    v-for="eq in equipamentosOpcoes"
                    :key="eq.id"
                    type="button"
                    class="text-left w-full min-h-[44px] px-3 py-2 rounded-lg text-sm transition-colors"
                    :class="
                      local.equipamentoId === eq.id
                        ? 'bg-primary-50 dark:bg-primary-950/40 text-primary-800 dark:text-primary-200 ring-1 ring-primary-300'
                        : 'hover:bg-gray-100 dark:hover:bg-gray-800 text-gray-700 dark:text-gray-300'
                    "
                    @click="selecionarEquipamento(eq.id, rotuloEquipamento(eq))"
                  >
                    <span class="font-medium block truncate">{{ eq.nome }}</span>
                    <span class="text-[11px] text-gray-500 dark:text-gray-400 block truncate">
                      {{ subtituloEquipamento(eq) }}
                    </span>
                  </button>
                  <p
                    v-if="!equipamentosOpcoes.length && buscaEquipamento.trim()"
                    class="text-xs text-gray-500 py-2 italic"
                  >
                    Nenhum equipamento encontrado.
                  </p>
                </div>
              </section>

              <section>
                <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2 flex items-center gap-2">
                  <MapPinIcon class="w-5 h-5 text-primary-500" />
                  Local (bairro)
                </h3>
                <input
                  v-model="buscaBairro"
                  type="search"
                  class="input w-full mb-2 text-sm"
                  placeholder="Buscar bairro…"
                />
                <div class="flex flex-wrap gap-2 max-h-32 overflow-y-auto p-1">
                  <button
                    v-for="b in bairrosFiltrados"
                    :key="b"
                    type="button"
                    class="badge text-xs px-3 py-1.5 transition-colors"
                    :class="
                      local.bairros.includes(b)
                        ? 'bg-primary-600 text-white ring-2 ring-primary-400'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                    "
                    @click="toggleItem(local.bairros, b)"
                  >
                    {{ b }}
                  </button>
                </div>
                <p v-if="!(opcoes.bairros || []).length" class="text-xs text-gray-500 italic">
                  Nenhum bairro nos protocolos ainda.
                </p>
              </section>

              <section>
                <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">Status do protocolo</h3>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="st in opcoes.status"
                    :key="st.value"
                    type="button"
                    class="badge text-xs px-3 py-1.5 transition-colors"
                    :class="
                      local.statusLista.includes(st.value)
                        ? 'bg-purple-600 text-white ring-2 ring-purple-400'
                        : 'bg-gray-100 dark:bg-gray-700 text-gray-700 dark:text-gray-300'
                    "
                    @click="toggleItem(local.statusLista, st.value)"
                  >
                    {{ labelStatus(st.value, st.label) }}
                  </button>
                </div>
              </section>

              <section>
                <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">Cobrança do cidadão</h3>
                <label class="flex items-center gap-3 min-h-[44px] cursor-pointer">
                  <input v-model="local.apenasCobrados" type="checkbox" class="w-4 h-4 rounded text-primary-600" />
                  <span class="text-sm text-gray-700 dark:text-gray-300">Apenas protocolos cobrados pelo cidadão</span>
                </label>
              </section>

              <section>
                <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">Retrabalho</h3>
                <label class="flex items-center gap-3 min-h-[44px] cursor-pointer">
                  <input v-model="local.apenasReabertos" type="checkbox" class="w-4 h-4 rounded text-primary-600" />
                  <span class="text-sm text-gray-700 dark:text-gray-300">Apenas reabertos</span>
                </label>
              </section>

              <section>
                <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">Urgência</h3>
                <div class="flex flex-wrap gap-2">
                  <button
                    v-for="u in opcoes.urgencias"
                    :key="u.value"
                    type="button"
                    class="badge text-xs px-3 py-1.5 transition-colors"
                    :class="chipUrgenciaClass(u.value)"
                    @click="toggleItem(local.urgenciaLista, u.value)"
                  >
                    {{ u.label }}
                  </button>
                </div>
              </section>

              <section>
                <h3 class="text-sm font-semibold text-gray-900 dark:text-white mb-2">Triagem de urgência</h3>
                <label class="flex items-center gap-3 min-h-[44px] cursor-pointer">
                  <input
                    v-model="local.apenasSugestaoUrgenciaIa"
                    type="checkbox"
                    class="w-4 h-4 rounded text-violet-600 focus:ring-violet-500 dark:focus:ring-violet-400"
                  />
                  <span class="text-sm text-gray-700 dark:text-gray-300">
                    Somente com sugestão de urgência aguardando sua revisão
                  </span>
                </label>
              </section>
            </div>

            <div class="shrink-0 px-6 py-4 border-t border-gray-200 dark:border-gray-700 flex flex-col-reverse sm:flex-row gap-2 sm:justify-between bg-gray-50 dark:bg-gray-800/80 sm:rounded-b-modal">
              <button type="button" class="btn-secondary" @click="limparLocal">Limpar seleção</button>
              <div class="flex flex-col-reverse sm:flex-row gap-2">
                <button type="button" class="btn-secondary" @click="fechar">Cancelar</button>
                <button type="button" class="btn-primary" @click="aplicar">
                  Aplicar{{ totalSelecionados ? ` (${totalSelecionados})` : '' }}
                </button>
              </div>
            </div>
          </div>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { ref, computed, watch, reactive } from 'vue'
import {
  BuildingOffice2Icon,
  WrenchScrewdriverIcon,
  MapPinIcon
} from '@heroicons/vue/24/outline'
import { catalogoLookupService } from '@/services/api'

const props = defineProps({
  aberto: Boolean,
  filtrosAtuais: { type: Object, required: true },
  unidades: { type: Array, default: () => [] },
  opcoes: {
    type: Object,
    default: () => ({
      bairros: [],
      servicos: [],
      status: [],
      urgencias: []
    })
  }
})

const emit = defineEmits(['fechar', 'aplicar'])

const buscaUnidade = ref('')
const buscaServico = ref('')
const buscaBairro = ref('')
const buscaEquipamento = ref('')
const equipamentosOpcoes = ref([])
const loadingEquipamentosLookup = ref(false)
let debounceEquipamento = null

const local = reactive({
  unidadesIds: [],
  servicoIds: [],
  bairros: [],
  statusLista: [],
  urgenciaLista: [],
  equipamentoId: '',
  equipamentoRotulo: '',
  apenasCobrados: false,
  apenasReabertos: false,
  apenasSugestaoUrgenciaIa: false
})

function snapshotFromStore() {
  const f = props.filtrosAtuais
  local.unidadesIds = [...(f.unidadesIds || [])]
  local.servicoIds = [...(f.servicoIds || [])]
  local.bairros = [...(f.bairros || [])]
  local.statusLista = [...(f.statusLista || [])]
  local.urgenciaLista = [...(f.urgenciaLista || [])]
  local.equipamentoId = f.equipamentoId || ''
  local.equipamentoRotulo = f.equipamentoRotulo || ''
  buscaEquipamento.value = f.equipamentoRotulo || ''
  local.apenasCobrados = Boolean(f.apenasCobrados)
  local.apenasReabertos = Boolean(f.apenasReabertos)
  local.apenasSugestaoUrgenciaIa = Boolean(f.apenasSugestaoUrgenciaIa)
}

async function buscarEquipamentosLookup() {
  loadingEquipamentosLookup.value = true
  try {
    const params = { limit: 25 }
    const q = buscaEquipamento.value.trim()
    if (q) params.busca = q
    equipamentosOpcoes.value = await catalogoLookupService.listarEquipamentos(params)
  } catch {
    equipamentosOpcoes.value = []
  } finally {
    loadingEquipamentosLookup.value = false
  }
}

watch(buscaEquipamento, () => {
  if (debounceEquipamento) clearTimeout(debounceEquipamento)
  debounceEquipamento = setTimeout(() => {
    buscarEquipamentosLookup()
  }, 300)
})

watch(
  () => props.aberto,
  (aberto) => {
    if (aberto) buscarEquipamentosLookup()
  }
)

function rotuloEquipamento(eq) {
  return eq.bairro ? `${eq.nome} · ${eq.bairro}` : eq.nome
}

function subtituloEquipamento(eq) {
  const partes = []
  if (eq.bairro) partes.push(eq.bairro)
  if (eq.unidade_nome) partes.push(eq.unidade_nome)
  return partes.join(' · ') || 'Sem detalhes adicionais'
}

function selecionarEquipamento(id, rotulo) {
  local.equipamentoId = id
  local.equipamentoRotulo = rotulo
  if (id && rotulo) buscaEquipamento.value = rotulo.split(' · ')[0]
}

watch(
  () => props.aberto,
  (v) => {
    if (v) snapshotFromStore()
  }
)

const unidadesFiltradas = computed(() => {
  const t = buscaUnidade.value.trim().toLowerCase()
  let lista = props.unidades || []
  if (t) {
    lista = lista.filter(
      (u) =>
        (u.nome || '').toLowerCase().includes(t) ||
        (u.sigla || '').toLowerCase().includes(t)
    )
  }
  return lista.slice(0, 80)
})

const servicosFiltrados = computed(() => {
  const t = buscaServico.value.trim().toLowerCase()
  let lista = props.opcoes.servicos || []
  if (t) lista = lista.filter((s) => (s.nome || '').toLowerCase().includes(t))
  return lista.slice(0, 80)
})

const bairrosFiltrados = computed(() => {
  const t = buscaBairro.value.trim().toLowerCase()
  let lista = props.opcoes.bairros || []
  if (t) lista = lista.filter((b) => b.toLowerCase().includes(t))
  return lista.slice(0, 60)
})

const totalSelecionados = computed(
  () =>
    local.unidadesIds.length +
    local.servicoIds.length +
    local.bairros.length +
    local.statusLista.length +
    local.urgenciaLista.length +
    (local.equipamentoId ? 1 : 0) +
    (local.apenasCobrados ? 1 : 0) +
    (local.apenasReabertos ? 1 : 0) +
    (local.apenasSugestaoUrgenciaIa ? 1 : 0)
)

function toggleItem(arr, value) {
  const idx = arr.indexOf(value)
  if (idx >= 0) arr.splice(idx, 1)
  else arr.push(value)
}

function labelStatus(value, fallback) {
  if (value === 'aguardando_revisao') return 'Aguardando validação'
  if (value === 'aguardando_cidadao') return 'Aguardando cidadão'
  return fallback
}

function chipUrgenciaClass(value) {
  const selected = local.urgenciaLista.includes(value)
  const map = {
    baixa: selected
      ? 'bg-emerald-600 text-white ring-2 ring-emerald-400'
      : 'bg-emerald-50 dark:bg-emerald-900/30 text-emerald-800 dark:text-emerald-200',
    normal: selected
      ? 'bg-sky-600 text-white ring-2 ring-sky-400'
      : 'bg-sky-50 dark:bg-sky-900/30 text-sky-900 dark:text-sky-200',
    alta: selected
      ? 'bg-orange-600 text-white ring-2 ring-orange-400'
      : 'bg-orange-50 dark:bg-orange-900/30 text-orange-900 dark:text-orange-200',
    critica: selected
      ? 'bg-red-600 text-white ring-2 ring-red-400'
      : 'bg-red-50 dark:bg-red-900/30 text-red-900 dark:text-red-200'
  }
  return map[value] || 'bg-gray-100 text-gray-700'
}

function fechar() {
  emit('fechar')
}

function limparLocal() {
  local.unidadesIds = []
  local.servicoIds = []
  local.bairros = []
  local.statusLista = []
  local.urgenciaLista = []
  local.equipamentoId = ''
  local.equipamentoRotulo = ''
  buscaEquipamento.value = ''
  local.apenasCobrados = false
  local.apenasReabertos = false
  local.apenasSugestaoUrgenciaIa = false
}

function aplicar() {
  emit('aplicar', {
    unidadesIds: [...local.unidadesIds],
    servicoIds: [...local.servicoIds],
    bairros: [...local.bairros],
    statusLista: [...local.statusLista],
    urgenciaLista: [...local.urgenciaLista],
    equipamentoId: local.equipamentoId,
    equipamentoRotulo: local.equipamentoRotulo,
    apenasCobrados: local.apenasCobrados,
    apenasReabertos: local.apenasReabertos,
    apenasSugestaoUrgenciaIa: local.apenasSugestaoUrgenciaIa
  })
}
</script>

<style scoped>
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
.slide-up-enter-active,
.slide-up-leave-active {
  transition: transform 0.25s ease, opacity 0.25s ease;
}
.slide-up-enter-from,
.slide-up-leave-to {
  transform: translateY(1rem);
  opacity: 0;
}
</style>