<template>
  <div class="space-y-6 max-w-7xl">
    <!-- Header -->
    <div class="flex flex-col lg:flex-row lg:items-center justify-between gap-4">
      <div>
        <h2 class="text-2xl font-bold text-gray-900 dark:text-white">Catálogo de Serviços</h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          Gerencie categorias e serviços disponíveis para os cidadãos
        </p>
      </div>

      <div class="flex flex-wrap items-center gap-3">
        <div
          class="inline-flex p-1 bg-gray-100 dark:bg-gray-800 rounded-lg border border-gray-200 dark:border-gray-700"
          role="tablist"
        >
          <button
            type="button"
            role="tab"
            :aria-selected="subaba === 'servicos'"
            :class="tabClass('servicos')"
            @click="subaba = 'servicos'"
          >
            <Squares2X2Icon class="w-4 h-4" />
            Serviços
          </button>
          <button
            type="button"
            role="tab"
            :aria-selected="subaba === 'categorias'"
            :class="tabClass('categorias')"
            @click="subaba = 'categorias'"
          >
            <FolderIcon class="w-4 h-4" />
            Categorias
          </button>
        </div>

        <template v-if="subaba === 'servicos'">
          <button
            type="button"
            class="inline-flex items-center gap-2 !py-2 !px-4 text-sm font-semibold rounded-lg border-2 border-primary-300 dark:border-primary-600 text-primary-700 dark:text-primary-300 bg-gradient-to-r from-primary-50 to-cyan-50 dark:from-primary-950/40 dark:to-cyan-950/30 hover:shadow-md hover:-translate-y-0.5 transition-all"
            @click="bibliotecaAberta = true"
          >
            <SparklesIcon class="w-5 h-5 text-amber-500" />
            Explorar modelos prontos
          </button>
          <button
            type="button"
            class="btn-primary flex items-center gap-2 !py-2 !px-4 text-sm"
            @click="abrirModalCriacao"
          >
            <PlusCircleIcon class="w-5 h-5" />
            Criar Novo Serviço
          </button>
        </template>
      </div>
    </div>

  <GestaoCategoriasCatalogo v-if="subaba === 'categorias'" />

  <template v-else>
    <!-- Barra de filtros (design system) -->
    <div class="card !p-4">
      <div class="flex flex-col lg:flex-row gap-3">
        <div class="w-full lg:w-52 shrink-0">
          <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 uppercase tracking-wide">
            Status
          </label>
          <select v-model="filtroStatus" class="input text-sm !py-2.5">
            <option value="todos">Todos os status</option>
            <option value="ativo">Apenas ativos</option>
            <option value="inativo">Apenas inativos</option>
          </select>
        </div>

        <div class="w-full lg:w-56 shrink-0">
          <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 uppercase tracking-wide">
            Categoria
          </label>
          <select v-model="filtroCategoriaId" class="input text-sm !py-2.5">
            <option value="">Todas as categorias</option>
            <option v-for="cat in categoriasFiltro" :key="cat.id" :value="cat.id">
              {{ cat.nome }}{{ cat.ativo ? '' : ' (inativa)' }}
            </option>
          </select>
        </div>

        <div class="flex-1 min-w-0">
          <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1.5 uppercase tracking-wide">
            Busca
          </label>
          <div class="relative">
            <MagnifyingGlassIcon
              class="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400"
            />
            <input
              v-model="buscaNome"
              type="search"
              placeholder="Buscar por nome ou descrição..."
              class="input text-sm !py-2.5 !pl-10 w-full"
            />
          </div>
        </div>

        <div v-if="filtrosAtivos" class="flex items-end lg:pb-0.5">
          <button
            type="button"
            class="inline-flex items-center gap-1.5 px-3 py-2.5 text-sm font-medium text-gray-600 hover:text-gray-900 dark:text-gray-400 dark:hover:text-gray-200 rounded-lg hover:bg-gray-100 dark:hover:bg-gray-700 transition-colors"
            @click="limparFiltros"
          >
            <XMarkIcon class="w-4 h-4" />
            Limpar
          </button>
        </div>
      </div>
    </div>

    <!-- Loading -->
    <div v-if="catalogoStore.loadingServicos" class="py-12">
      <div class="flex flex-col items-center justify-center">
        <div class="w-12 h-12 border-4 border-primary-200 border-t-primary-600 rounded-full animate-spin mb-4" />
        <p class="text-sm text-gray-600 dark:text-gray-400">Carregando serviços...</p>
      </div>
    </div>

    <!-- Lista de Serviços -->
    <div v-else-if="servicosFiltrados.length > 0" class="grid grid-cols-1 lg:grid-cols-2 xl:grid-cols-3 gap-4">
      <div
        v-for="servico in servicosFiltrados"
        :key="servico.id"
        class="card !p-5 hover:shadow-card-hover border-2 border-transparent hover:border-primary-200 dark:hover:border-primary-800 transition-all duration-300"
        :class="{ 'opacity-60 pointer-events-none': duplicandoId === servico.id }"
      >
        <div class="flex items-start justify-between mb-3">
          <div class="flex-1 min-w-0">
            <h3 class="text-lg font-semibold text-gray-900 dark:text-white truncate">
              {{ servico.nome }}
            </h3>
            <p class="text-xs text-gray-500 dark:text-gray-400 mt-0.5">
              {{ servico.categoria_nome || 'Sem categoria' }}
            </p>
            <div class="flex flex-wrap items-center gap-1.5 mt-1.5">
              <span
                class="text-[10px] font-mono font-semibold px-1.5 py-0.5 rounded bg-slate-100 text-slate-600 dark:bg-slate-800 dark:text-slate-300"
              >
                v{{ servico.versao_publicada ?? 1 }}
              </span>
              <span
                v-if="servico.tem_rascunho_pendente"
                class="text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-amber-100 text-amber-800 dark:bg-amber-950/40 dark:text-amber-200"
              >
                Rascunho
              </span>
              <span
                v-if="servico.permite_cluster === false"
                class="inline-flex items-center gap-1 text-[10px] font-semibold px-1.5 py-0.5 rounded-full bg-violet-100 text-violet-800 dark:bg-violet-950/50 dark:text-violet-200 ring-1 ring-violet-200/80 dark:ring-violet-800/50"
                title="Demandas deste serviço não são agrupadas no mapa IA"
              >
                <UserIcon class="w-3 h-3 shrink-0" aria-hidden="true" />
                Atendimento individual
              </span>
              <span
                v-if="badgeGovernanca(servico)"
                class="text-[10px] font-semibold px-1.5 py-0.5 rounded-full"
                :class="badgeGovernanca(servico).class"
                :title="badgeGovernanca(servico).title"
              >
                {{ badgeGovernanca(servico).label }}
              </span>
            </div>
          </div>

          <span
            class="px-2 py-1 text-xs font-semibold rounded-full flex-shrink-0 ml-2"
            :class="
              servico.ativo
                ? 'bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400'
                : 'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-400'
            "
          >
            {{ servico.ativo ? 'Ativo' : 'Inativo' }}
          </span>
        </div>

        <p class="text-sm text-gray-600 dark:text-gray-400 mb-4 line-clamp-2">
          {{ servico.descricao || 'Sem descrição' }}
        </p>

        <div class="space-y-2 mb-4 text-sm">
          <div class="flex items-center gap-2 text-gray-600 dark:text-gray-400">
            <BuildingOffice2Icon class="w-4 h-4" />
            <span class="truncate">{{ servico.unidade_responsavel_nome || 'Sem unidade' }}</span>
          </div>

          <div class="flex items-center gap-2 text-gray-600 dark:text-gray-400">
            <ClockIcon class="w-4 h-4" />
            <span>SLA: {{ servico.sla_padrao_horas || 0 }}h ({{ calcularDias(servico.sla_padrao_horas) }})</span>
          </div>

          <div class="flex items-center gap-2 text-gray-600 dark:text-gray-400">
            <DocumentTextIcon class="w-4 h-4" />
            <span>{{ contarCampos(servico.formulario_schema) }} dados para a IA</span>
          </div>
        </div>

        <div class="flex items-center gap-2">
          <button type="button" class="btn-secondary flex-1 text-sm !py-2" @click="abrirModalEdicao(servico)">
            <PencilIcon class="w-4 h-4 mr-1.5" />
            Editar
          </button>

          <button
            type="button"
            class="btn-icon text-primary-600 hover:bg-primary-50 dark:text-primary-400 dark:hover:bg-primary-950/40 transition-colors disabled:opacity-50"
            title="Duplicar serviço"
            :disabled="Boolean(duplicandoId)"
            :aria-busy="duplicandoId === servico.id"
            @click="duplicarServico(servico)"
          >
            <span
              v-if="duplicandoId === servico.id"
              class="w-5 h-5 border-2 border-primary-500 border-t-transparent rounded-full animate-spin block"
            />
            <DocumentDuplicateIcon v-else class="w-5 h-5" />
          </button>

          <button
            type="button"
            class="btn-icon text-red-600 hover:bg-red-50 dark:hover:bg-red-900/20"
            title="Excluir"
            :disabled="Boolean(duplicandoId)"
            @click="confirmarExclusao(servico)"
          >
            <TrashIcon class="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>

    <!-- Estado vazio -->
    <div v-else class="card py-16 text-center">
      <DocumentTextIcon class="w-16 h-16 text-gray-400 dark:text-gray-600 mx-auto mb-4" />
      <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">
        {{ filtrosAtivos ? 'Nenhum serviço encontrado' : 'Nenhum serviço cadastrado' }}
      </h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-6">
        {{ filtrosAtivos ? 'Tente ajustar os filtros de busca' : 'Comece criando um novo serviço para o catálogo' }}
      </p>
      <button v-if="!filtrosAtivos" type="button" class="btn-primary" @click="abrirModalCriacao">
        <PlusCircleIcon class="w-5 h-5 mr-2" />
        Criar Primeiro Serviço
      </button>
    </div>

    <BibliotecaModelos
      :aberto="bibliotecaAberta"
      @fechar="bibliotecaAberta = false"
      @clonado="handleModeloClonado"
    />

    <Teleport to="body">
      <Transition name="modal">
        <FormBuilderServico
          v-if="modalAberto"
          :servico="servicoEmEdicao"
          @fechar="fecharModal"
          @sucesso="handleSucesso"
          @atualizado="handleAtualizado"
        />
      </Transition>
    </Teleport>

    <Teleport to="body">
      <Transition name="modal">
        <div
          v-if="servicoParaExcluir"
          class="fixed inset-0 z-[9999] flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm"
          @click.self="servicoParaExcluir = null"
        >
          <div class="bg-white dark:bg-gray-800 rounded-xl shadow-xl max-w-md w-full p-6">
            <div class="flex items-start gap-4">
              <div
                class="flex-shrink-0 w-12 h-12 rounded-full bg-red-100 dark:bg-red-900/30 flex items-center justify-center"
              >
                <ExclamationTriangleIcon class="w-6 h-6 text-red-600 dark:text-red-400" />
              </div>

              <div class="flex-1">
                <h3 class="text-lg font-semibold text-gray-900 dark:text-white mb-2">Excluir Serviço?</h3>
                <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
                  Tem certeza que deseja excluir o serviço <strong>{{ servicoParaExcluir.nome }}</strong>? Esta ação não
                  pode ser desfeita.
                </p>

                <div class="flex gap-3">
                  <button type="button" class="btn-secondary flex-1" @click="servicoParaExcluir = null">
                    Cancelar
                  </button>
                  <button
                    type="button"
                    class="btn-danger flex-1"
                    :disabled="excluindo"
                    @click="executarExclusao"
                  >
                    {{ excluindo ? 'Excluindo...' : 'Excluir' }}
                  </button>
                </div>
              </div>
            </div>
          </div>
        </div>
      </Transition>
    </Teleport>
  </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue'
import { storeToRefs } from 'pinia'
import { useCatalogoStore } from '@/stores/catalogo'
import FormBuilderServico from './FormBuilderServico.vue'
import BibliotecaModelos from './BibliotecaModelos.vue'
import GestaoCategoriasCatalogo from './GestaoCategoriasCatalogo.vue'
import { useAdminToast } from '@/composables/useAdminToast'
import { badgeGovernancaServico as badgeGovernanca } from '@/constants/governancaFluxo'
import {
  PlusCircleIcon,
  PencilIcon,
  TrashIcon,
  DocumentTextIcon,
  BuildingOffice2Icon,
  ClockIcon,
  ExclamationTriangleIcon,
  MagnifyingGlassIcon,
  XMarkIcon,
  FolderIcon,
  Squares2X2Icon,
  SparklesIcon,
  DocumentDuplicateIcon,
  UserIcon
} from '@heroicons/vue/24/outline'

const catalogoStore = useCatalogoStore()
const { servicos, categoriasCatalogo, duplicandoServicoId } = storeToRefs(catalogoStore)
const duplicandoId = duplicandoServicoId
const { mostrarToast } = useAdminToast()

const subaba = ref('servicos')
const bibliotecaAberta = ref(false)
const modalAberto = ref(false)
const servicoEmEdicao = ref(null)
const servicoParaExcluir = ref(null)
const excluindo = ref(false)

const filtroStatus = ref('todos')
const filtroCategoriaId = ref('')
const buscaNome = ref('')

const categoriasFiltro = computed(() => categoriasCatalogo.value)

const filtrosAtivos = computed(() => {
  return (
    filtroStatus.value !== 'todos' ||
    Boolean(filtroCategoriaId.value) ||
    Boolean(buscaNome.value.trim())
  )
})

function tabClass(id) {
  return [
    'inline-flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-all duration-200',
    subaba.value === id
      ? 'bg-white dark:bg-gray-700 text-primary-700 dark:text-primary-300 shadow-sm'
      : 'text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-gray-200'
  ]
}

function limparFiltros() {
  filtroStatus.value = 'todos'
  filtroCategoriaId.value = ''
  buscaNome.value = ''
}

const servicosFiltrados = computed(() => {
  let resultado = servicos.value

  if (filtroStatus.value === 'ativo') {
    resultado = resultado.filter((s) => s.ativo)
  } else if (filtroStatus.value === 'inativo') {
    resultado = resultado.filter((s) => !s.ativo)
  }

  if (filtroCategoriaId.value) {
    resultado = resultado.filter((s) => String(s.categoria_id) === filtroCategoriaId.value)
  }

  if (buscaNome.value.trim()) {
    const busca = buscaNome.value.toLowerCase()
    resultado = resultado.filter(
      (s) => s.nome.toLowerCase().includes(busca) || s.descricao?.toLowerCase().includes(busca)
    )
  }

  return resultado
})

function abrirModalCriacao() {
  servicoEmEdicao.value = null
  modalAberto.value = true
}

function abrirModalEdicao(servico) {
  servicoEmEdicao.value = servico
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
  servicoEmEdicao.value = null
}

function handleSucesso() {
  fecharModal()
  catalogoStore.carregarServicosCatalogo().catch(() => {})
}

function handleAtualizado(servico) {
  servicoEmEdicao.value = servico
  catalogoStore.carregarServicosCatalogoSilencioso().catch(() => {})
}

async function handleModeloClonado(novoServico) {
  bibliotecaAberta.value = false
  mostrarToast('Serviço clonado com sucesso!')
  await catalogoStore.carregarServicosCatalogo().catch(() => {})
  const atualizado = catalogoStore.getServicoPorId(novoServico?.id) || novoServico
  abrirModalEdicao(atualizado)
}

async function duplicarServico(servico) {
  if (!servico?.id || duplicandoId.value) return
  try {
    const novo = await catalogoStore.duplicarServico(servico.id)
    mostrarToast('Serviço duplicado. A cópia está inativa para revisão.')
    await catalogoStore.carregarServicosCatalogo().catch(() => {})
    const atualizado = catalogoStore.getServicoPorId(novo?.id) || novo
    abrirModalEdicao(atualizado)
  } catch (err) {
    console.error('Erro ao duplicar:', err)
    mostrarToast(catalogoStore.erro || 'Não foi possível duplicar o serviço.', true)
  }
}

function confirmarExclusao(servico) {
  servicoParaExcluir.value = servico
}

async function executarExclusao() {
  if (!servicoParaExcluir.value) return

  excluindo.value = true
  try {
    await catalogoStore.excluirServicoCatalogo(servicoParaExcluir.value.id)
    servicoParaExcluir.value = null
  } catch (err) {
    console.error('Erro ao excluir:', err)
  } finally {
    excluindo.value = false
  }
}

function calcularDias(horas) {
  if (!horas) return '0 dias'
  const dias = Math.floor(horas / 24)
  const horasRestantes = horas % 24

  if (dias === 0) return `${horas}h`
  if (horasRestantes === 0) return `${dias}d`
  return `${dias}d ${horasRestantes}h`
}

function contarCampos(schema) {
  if (!schema) return 0
  if (Array.isArray(schema)) return schema.length
  if (typeof schema === 'string') {
    try {
      const parsed = JSON.parse(schema)
      return Array.isArray(parsed) ? parsed.length : 0
    } catch {
      return 0
    }
  }
  return 0
}

onMounted(() => {
  catalogoStore.carregarServicosCatalogo().catch(() => {})
  catalogoStore.carregarCategoriasCatalogo().catch(() => {})
})
</script>

<style scoped>
.modal-enter-active,
.modal-leave-active {
  transition: opacity 0.3s ease;
}

.modal-enter-from,
.modal-leave-to {
  opacity: 0;
}

.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>