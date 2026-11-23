<template>
  <div class="max-w-7xl">
    <div class="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4 mb-6">
      <div>
        <h2 class="text-lg font-bold text-gray-900 dark:text-white">Equipamentos Públicos</h2>
        <p class="text-sm text-gray-600 dark:text-gray-400 mt-1">
          UBS, escolas, CRAS e demais locais físicos vinculados às secretarias
        </p>
      </div>
      <button
        type="button"
        class="inline-flex items-center gap-2 px-4 py-2 bg-primary-600 hover:bg-primary-700 text-white rounded-lg font-medium text-sm shadow-button"
        @click="abrirModalCriacao"
      >
        <PlusIcon class="w-5 h-5" />
        Novo equipamento
      </button>
    </div>

    <div class="card p-4 mb-4">
      <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-6 gap-3">
        <div class="lg:col-span-2">
          <label class="sr-only">Busca</label>
          <input
            v-model="filtrosLocais.busca"
            type="search"
            class="input text-sm"
            placeholder="Buscar por nome ou apelido..."
            @keydown.enter="aplicarFiltros"
          />
        </div>
        <select v-model="filtrosLocais.unidade_id" class="input text-sm">
          <option value="">Todas as secretarias</option>
          <option v-for="u in unidadesAtivas" :key="u.id" :value="u.id">
            {{ u.sigla || u.nome }}
          </option>
        </select>
        <select v-model="filtrosLocais.tipo" class="input text-sm">
          <option value="">Todos os tipos</option>
          <option v-for="t in TIPOS_EQUIPAMENTO_PUBLICO" :key="t.value" :value="t.value">
            {{ t.label }}
          </option>
        </select>
        <select v-model="filtrosLocais.ativo" class="input text-sm">
          <option value="">Ativo e inativo</option>
          <option value="true">Somente ativos</option>
          <option value="false">Somente inativos</option>
        </select>
        <select v-model="filtrosLocais.georreferenciado" class="input text-sm" title="Filtro geoespacial">
          <option value="">GPS: todos</option>
          <option value="true">No mapa</option>
          <option value="false">Sem GPS (curadoria)</option>
        </select>
      </div>
      <div class="flex flex-wrap gap-2 mt-3">
        <button type="button" class="btn-primary text-sm py-1.5 px-3" @click="aplicarFiltros">Filtrar</button>
        <button type="button" class="btn-secondary text-sm py-1.5 px-3" @click="limparFiltros">Limpar</button>
      </div>
    </div>

    <div v-if="loadingEquipamentos" class="card p-12 flex flex-col items-center">
      <div class="animate-spin rounded-full h-12 w-12 border-4 border-primary-500 border-t-transparent" />
      <p class="text-sm text-gray-500 mt-4">Carregando equipamentos...</p>
    </div>

    <div v-else-if="!equipamentos.length" class="card p-12 text-center">
      <BuildingStorefrontIcon class="w-12 h-12 text-gray-400 mx-auto mb-4" />
      <h3 class="text-base font-semibold text-gray-900 dark:text-white mb-2">Nenhum equipamento encontrado</h3>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-4">
        Ajuste os filtros ou cadastre o primeiro equipamento público.
      </p>
      <button type="button" class="btn-primary" @click="abrirModalCriacao">Cadastrar equipamento</button>
    </div>

    <div v-else class="card overflow-hidden">
      <div class="overflow-x-auto">
        <table class="w-full">
          <thead class="bg-gray-50 dark:bg-gray-800 border-b border-gray-200 dark:border-gray-700">
            <tr>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Nome</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Tipo</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Secretaria</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Bairro</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Apelidos</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Mapa</th>
              <th class="px-4 py-3 text-left text-xs font-semibold uppercase text-gray-500">Status</th>
              <th class="px-4 py-3 text-right text-xs font-semibold uppercase text-gray-500">Ações</th>
            </tr>
          </thead>
          <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
            <tr
              v-for="eq in equipamentos"
              :key="eq.id"
              class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
            >
              <td class="px-4 py-3 text-sm font-semibold text-gray-900 dark:text-white">{{ eq.nome }}</td>
              <td class="px-4 py-3">
                <span :class="badgeClassTipoEquipamento(eq.tipo)">{{ labelTipoEquipamento(eq.tipo) }}</span>
              </td>
              <td class="px-4 py-3 text-sm text-gray-700 dark:text-gray-300 max-w-[12rem] truncate" :title="eq.unidadeResponsavelNome">
                {{ eq.unidadeResponsavelNome || '—' }}
              </td>
              <td class="px-4 py-3 text-sm text-gray-600 dark:text-gray-400">{{ eq.bairro || '—' }}</td>
              <td class="px-4 py-3">
                <div class="flex flex-wrap gap-1 max-w-[14rem]">
                  <span
                    v-for="(a, i) in (eq.apelidos || []).slice(0, 3)"
                    :key="i"
                    class="text-[10px] px-2 py-0.5 rounded-full bg-slate-100 dark:bg-slate-700 text-slate-700 dark:text-slate-200"
                  >
                    {{ a }}
                  </span>
                  <span v-if="(eq.apelidos || []).length > 3" class="text-[10px] text-gray-500">+{{ eq.apelidos.length - 3 }}</span>
                </div>
              </td>
              <td class="px-4 py-3">
                <span
                  v-if="eq.georreferenciado"
                  class="inline-flex items-center gap-1 text-[11px] font-medium text-emerald-800 dark:text-emerald-200"
                  title="Coordenadas PostGIS cadastradas"
                >
                  <MapPinIcon class="w-4 h-4 text-emerald-500 shrink-0" aria-hidden="true" />
                  No mapa
                </span>
                <span
                  v-else
                  class="inline-flex items-center gap-1 text-[11px] font-medium text-gray-500 dark:text-gray-400"
                  title="Sem georreferência — edite para posicionar no mapa"
                >
                  <MapPinIcon class="w-4 h-4 text-gray-400 shrink-0" aria-hidden="true" />
                  Sem GPS
                </span>
              </td>
              <td class="px-4 py-3">
                <span
                  :class="[
                    'inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-semibold',
                    eq.ativo
                      ? 'bg-green-100 text-green-800 dark:bg-green-900/30 dark:text-green-300'
                      : 'bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400'
                  ]"
                >
                  <span :class="['w-1.5 h-1.5 rounded-full', eq.ativo ? 'bg-green-500' : 'bg-gray-400']" />
                  {{ eq.ativo ? 'Ativo' : 'Inativo' }}
                </span>
              </td>
              <td class="px-4 py-3 text-right">
                <button
                  type="button"
                  class="inline-flex items-center gap-1 text-sm font-medium text-primary-600 hover:text-primary-700"
                  @click="abrirModalEdicao(eq)"
                >
                  <PencilSquareIcon class="w-4 h-4" />
                  Editar
                </button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <ModalEquipamento
      v-if="modalAberto"
      :equipamento="selecionado"
      :unidades-ativas="unidadesAtivas"
      @fechar="fecharModal"
      @salvo="onSalvo"
    />
  </div>
</template>

<script setup>
import { onMounted, reactive, ref } from 'vue'
import { storeToRefs } from 'pinia'
import { BuildingStorefrontIcon, PlusIcon, PencilSquareIcon, MapPinIcon } from '@heroicons/vue/24/outline'
import {
  TIPOS_EQUIPAMENTO_PUBLICO,
  badgeClassTipoEquipamento,
  labelTipoEquipamento
} from '@/constants/equipamentosPublicos'
import { useAdminStore } from '@/stores/admin'
import { useAdminToast } from '@/composables/useAdminToast'
import ModalEquipamento from './ModalEquipamento.vue'

const adminStore = useAdminStore()
const { mostrarToast } = useAdminToast()
const { equipamentos, loadingEquipamentos, unidadesAtivas } = storeToRefs(adminStore)

const modalAberto = ref(false)
const selecionado = ref(null)

const filtrosLocais = reactive({
  busca: '',
  unidade_id: '',
  tipo: '',
  ativo: '',
  georreferenciado: ''
})

function paramsApi() {
  const p = {}
  if (filtrosLocais.busca.trim()) p.busca = filtrosLocais.busca.trim()
  if (filtrosLocais.unidade_id) p.unidade_id = filtrosLocais.unidade_id
  if (filtrosLocais.tipo) p.tipo = filtrosLocais.tipo
  if (filtrosLocais.ativo === 'true') p.ativo = true
  if (filtrosLocais.ativo === 'false') p.ativo = false
  if (filtrosLocais.georreferenciado === 'true') p.georreferenciado = true
  if (filtrosLocais.georreferenciado === 'false') p.georreferenciado = false
  return p
}

async function aplicarFiltros() {
  try {
    await adminStore.carregarEquipamentos(paramsApi())
  } catch {
    mostrarToast(adminStore.erro || 'Erro ao filtrar equipamentos', true)
  }
}

function limparFiltros() {
  filtrosLocais.busca = ''
  filtrosLocais.unidade_id = ''
  filtrosLocais.tipo = ''
  filtrosLocais.ativo = ''
  filtrosLocais.georreferenciado = ''
  aplicarFiltros()
}

function abrirModalCriacao() {
  selecionado.value = null
  modalAberto.value = true
}

function abrirModalEdicao(eq) {
  selecionado.value = { ...eq }
  modalAberto.value = true
}

function fecharModal() {
  modalAberto.value = false
  selecionado.value = null
}

async function onSalvo() {
  mostrarToast('Equipamento salvo com sucesso.')
  await aplicarFiltros()
}

onMounted(async () => {
  await Promise.all([
    adminStore.carregarUnidades({ silencioso: true }).catch(() => null),
    aplicarFiltros()
  ])
})
</script>