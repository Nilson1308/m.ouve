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
      class="fixed inset-0 bg-black/60 backdrop-blur-sm z-50 flex items-center justify-center p-4 overflow-y-auto"
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
        <div class="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl w-full max-w-6xl my-8 overflow-hidden">
          <!-- Header Épico com Gradiente -->
          <div class="relative bg-gradient-to-r from-purple-600 via-pink-600 to-purple-600 p-6 overflow-hidden">
            <!-- Efeito de Brilho Animado -->
            <div class="absolute inset-0 bg-gradient-to-r from-transparent via-white/20 to-transparent animate-shimmer"></div>
            
            <div class="relative flex items-start justify-between">
              <div class="flex items-center gap-4">
                <div class="p-3 bg-white/20 backdrop-blur-sm rounded-xl">
                  <ShieldCheckIcon class="w-8 h-8 text-white" />
                </div>
                <div>
                  <h2 class="text-2xl font-bold text-white mb-1 flex items-center gap-2">
                    {{ perfil ? 'Editar Perfil' : 'Novo Perfil de Acesso' }}
                    <SparklesIcon class="w-6 h-6 text-pink-200 animate-pulse" />
                  </h2>
                  <p class="text-purple-100">
                    Matriz de Permissões Granulares
                  </p>
                </div>
              </div>

              <button
                @click="$emit('fechar')"
                class="p-2 hover:bg-white/20 rounded-lg transition-colors"
              >
                <XMarkIcon class="w-6 h-6 text-white" />
              </button>
            </div>
          </div>

          <!-- Formulário (footer dentro do form para o botão type="submit") -->
          <form
            @submit.prevent="salvar"
            class="flex flex-col max-h-[calc(100vh-8rem)]"
          >
            <div class="flex-1 overflow-y-auto p-6 space-y-6">
            <!-- Seção: Informações Básicas -->
            <div class="pb-6 border-b border-gray-200 dark:border-gray-700">
              <h3 class="text-sm font-bold text-gray-900 dark:text-white mb-4 flex items-center gap-2">
                <InformationCircleIcon class="w-5 h-5 text-gray-600 dark:text-gray-400" />
                Informações do Perfil
              </h3>

              <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                <!-- Nome -->
                <div>
                  <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Nome do Perfil *
                  </label>
                  <input
                    v-model="formulario.nome"
                    type="text"
                    placeholder="Ex: Chefe de Gabinete"
                    required
                    class="input"
                  />
                </div>

                <!-- Slug (opcional, gerado automaticamente) -->
                <div>
                  <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Slug (identificador)
                  </label>
                  <input
                    v-model="formulario.slug"
                    type="text"
                    placeholder="chefe_gabinete (auto)"
                    class="input font-mono text-sm"
                  />
                  <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                    Gerado automaticamente se deixado em branco
                  </p>
                </div>

                <!-- Descrição (col-span-2) -->
                <div class="md:col-span-2">
                  <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                    Descrição
                  </label>
                  <textarea
                    v-model="formulario.descricao"
                    rows="2"
                    placeholder="Descreva as responsabilidades deste perfil..."
                    class="input resize-none"
                  ></textarea>
                </div>

                <!-- Requer Vínculo -->
                <div class="flex items-start gap-3 p-3 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800 md:col-span-2">
                  <input
                    v-model="formulario.requer_vinculo"
                    type="checkbox"
                    id="requer-vinculo"
                    class="mt-0.5 w-4 h-4 text-primary-600 bg-gray-100 border-gray-300 rounded focus:ring-primary-500"
                  />
                  <div class="flex-1">
                    <label for="requer-vinculo" class="block text-sm font-semibold text-gray-900 dark:text-white cursor-pointer">
                      Requer Vínculo de Unidade Administrativa
                    </label>
                    <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      Se marcado, usuários com este perfil devem estar vinculados a uma Secretaria/Órgão
                    </p>
                  </div>
                </div>

                <!-- Status Ativo -->
                <div class="flex items-start gap-3 p-3 bg-gray-50 dark:bg-gray-700/50 rounded-lg border border-gray-200 dark:border-gray-600 md:col-span-2">
                  <input
                    v-model="formulario.ativo"
                    type="checkbox"
                    id="perfil-ativo"
                    class="mt-0.5 w-4 h-4 text-green-600 bg-gray-100 border-gray-300 rounded focus:ring-green-500"
                  />
                  <div class="flex-1">
                    <label for="perfil-ativo" class="block text-sm font-semibold text-gray-900 dark:text-white cursor-pointer">
                      Perfil Ativo
                    </label>
                    <p class="text-xs text-gray-600 dark:text-gray-400 mt-1">
                      Perfis inativos não podem ser atribuídos a novos usuários
                    </p>
                  </div>
                </div>
              </div>
            </div>

            <!-- Seção: MATRIZ DE PERMISSÕES 🎯 -->
            <div>
              <div class="flex items-center justify-between mb-4">
                <h3 class="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
                  <CubeIcon class="w-5 h-5 text-purple-600 dark:text-purple-400" />
                  Matriz de Permissões por Módulo
                </h3>
                <div class="flex items-center gap-2">
                  <button
                    type="button"
                    @click="marcarTodos(true)"
                    class="text-xs font-medium text-green-600 hover:text-green-700 dark:text-green-400 dark:hover:text-green-300"
                  >
                    Marcar Todos
                  </button>
                  <span class="text-gray-300 dark:text-gray-600">|</span>
                  <button
                    type="button"
                    @click="marcarTodos(false)"
                    class="text-xs font-medium text-red-600 hover:text-red-700 dark:text-red-400 dark:hover:text-red-300"
                  >
                    Desmarcar Todos
                  </button>
                </div>
              </div>

              <!-- Tabela Matriz (Responsiva com Scroll Horizontal) -->
              <div class="overflow-x-auto rounded-lg border-2 border-purple-200 dark:border-purple-800 shadow-lg">
                <table class="w-full min-w-[800px]">
                  <thead>
                    <tr class="bg-gradient-to-r from-purple-100 to-pink-100 dark:from-purple-900/40 dark:to-pink-900/40">
                      <th class="px-4 py-3 text-left text-xs font-bold text-purple-900 dark:text-purple-100 uppercase tracking-wider w-64">
                        Módulo do Sistema
                      </th>
                      <th
                        v-for="acao in acoes"
                        :key="acao.key"
                        class="px-4 py-3 text-center text-xs font-bold text-purple-900 dark:text-purple-100 uppercase tracking-wider"
                      >
                        <div class="flex flex-col items-center gap-1">
                          <component :is="acao.icon" class="w-5 h-5" />
                          <span>{{ acao.label }}</span>
                        </div>
                      </th>
                    </tr>
                  </thead>
                  <tbody class="divide-y divide-gray-200 dark:divide-gray-700">
                    <tr
                      v-for="modulo in modulos"
                      :key="modulo.key"
                      class="hover:bg-gray-50 dark:hover:bg-gray-800/50 transition-colors"
                    >
                      <!-- Nome do Módulo -->
                      <td class="px-4 py-4 bg-gray-50 dark:bg-gray-800/50">
                        <div class="flex items-center gap-3">
                          <component :is="modulo.icon" class="w-5 h-5 text-gray-600 dark:text-gray-400 shrink-0" />
                          <div>
                            <p class="text-sm font-semibold text-gray-900 dark:text-white">
                              {{ modulo.label }}
                            </p>
                            <p class="text-xs text-gray-500 dark:text-gray-400">
                              {{ modulo.descricao }}
                            </p>
                          </div>
                        </div>
                      </td>

                      <!-- Toggles de Permissões -->
                      <td
                        v-for="acao in acoes"
                        :key="acao.key"
                        class="px-4 py-4 text-center"
                      >
                        <label class="relative inline-flex items-center cursor-pointer">
                          <input
                            type="checkbox"
                            v-model="formulario.permissoes[modulo.key][acao.key]"
                            class="sr-only peer"
                            @change="onPermissaoChange(modulo.key, acao.key)"
                          />
                          <div class="w-11 h-6 bg-gray-200 peer-focus:outline-none peer-focus:ring-4 peer-focus:ring-purple-300 dark:peer-focus:ring-purple-800 rounded-full peer dark:bg-gray-700 peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all dark:border-gray-600 peer-checked:bg-gradient-to-r peer-checked:from-purple-600 peer-checked:to-pink-600 peer-checked:shadow-lg peer-checked:shadow-purple-500/50"></div>
                        </label>
                      </td>
                    </tr>
                  </tbody>
                </table>
              </div>

              <!-- Legenda -->
              <div class="mt-4 p-3 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                <p class="text-xs text-purple-800 dark:text-purple-200 flex items-start gap-2">
                  <InformationCircleIcon class="w-4 h-4 shrink-0 mt-0.5" />
                  <span>
                    <strong>Dica:</strong> Ative apenas as permissões necessárias para cada perfil. 
                    Por exemplo, um "Operador de Máquinas" precisa apenas visualizar (Ler) ordens de serviço, 
                    mas não criar ou excluir protocolos.
                  </span>
                </p>
              </div>
            </div>
            </div>

            <!-- Footer -->
            <div class="shrink-0 px-6 py-4 bg-gray-50 dark:bg-gray-700/50 border-t border-gray-200 dark:border-gray-600 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
            <div>
              <p class="text-xs text-gray-500 dark:text-gray-400">
                * Campos obrigatórios
              </p>
              <p class="text-xs text-gray-500 dark:text-gray-400 mt-1">
                As permissões serão salvas no formato JSON estruturado por módulo
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
                type="submit"
                :disabled="!formularioValido || salvando"
                class="flex-1 sm:flex-none px-6 py-2 bg-gradient-to-r from-purple-600 to-pink-600 hover:from-purple-700 hover:to-pink-700 text-white rounded-lg font-bold transition-all disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2 shadow-lg shadow-purple-500/50"
              >
                <div v-if="salvando" class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"></div>
                <CheckIcon v-else class="w-5 h-5" />
                {{ salvando ? 'Salvando...' : perfil ? 'Salvar Alterações' : 'Criar Perfil' }}
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
import {
  ShieldCheckIcon,
  SparklesIcon,
  XMarkIcon,
  CheckIcon,
  InformationCircleIcon,
  CubeIcon,
  EyeIcon,
  PlusCircleIcon,
  PencilSquareIcon,
  TrashIcon,
  ClipboardDocumentListIcon,
  BuildingOffice2Icon,
  MapIcon,
  Cog6ToothIcon,
  DocumentTextIcon,
  UserGroupIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  perfil: {
    type: Object,
    default: null
  }
})

const emit = defineEmits(['fechar', 'salvar'])

// Definição dos Módulos do Sistema
const modulos = [
  {
    key: 'mesa_trabalho',
    label: 'Mesa de Trabalho',
    descricao: 'Visualizar e gerenciar protocolos gerais',
    icon: ClipboardDocumentListIcon
  },
  {
    key: 'painel_setorial',
    label: 'Painel Setorial',
    descricao: 'Gestão de OS da unidade vinculada',
    icon: BuildingOffice2Icon
  },
  {
    key: 'mapa_ia',
    label: 'Mapa & IA',
    descricao: 'Visualização geográfica e clusterização',
    icon: MapIcon
  },
  {
    key: 'configuracoes',
    label: 'Configurações',
    descricao: 'Administração do sistema',
    icon: Cog6ToothIcon
  },
  {
    key: 'textos_padrao',
    label: 'Textos Padrão',
    descricao: 'Gerenciar modelos de despacho',
    icon: DocumentTextIcon
  },
  {
    key: 'gestao_usuarios',
    label: 'Gestão de Usuários',
    descricao: 'Criar e editar usuários',
    icon: UserGroupIcon
  }
]

// Definição das Ações (Colunas)
const acoes = [
  { key: 'ler', label: 'Ler', icon: EyeIcon },
  { key: 'criar', label: 'Criar', icon: PlusCircleIcon },
  { key: 'editar', label: 'Editar', icon: PencilSquareIcon },
  { key: 'excluir', label: 'Excluir', icon: TrashIcon }
]

// Formulário
const formulario = ref({
  nome: '',
  slug: '',
  descricao: '',
  requer_vinculo: false,
  ativo: true,
  permissoes: {}
})

const salvando = ref(false)

// Inicializar matriz de permissões
function inicializarPermissoes() {
  const perms = {}
  modulos.forEach(modulo => {
    perms[modulo.key] = {}
    acoes.forEach(acao => {
      perms[modulo.key][acao.key] = false
    })
  })
  return perms
}

// Preencher formulário se estiver editando
watch(() => props.perfil, (perfil) => {
  if (perfil) {
    formulario.value = {
      nome: perfil.nome || '',
      slug: perfil.slug || '',
      descricao: perfil.descricao || '',
      requer_vinculo: perfil.requer_vinculo || false,
      ativo: perfil.ativo !== false,
      permissoes: perfil.permissoes ? JSON.parse(JSON.stringify(perfil.permissoes)) : inicializarPermissoes()
    }
    
    // Garantir que todos os módulos existem
    modulos.forEach(modulo => {
      if (!formulario.value.permissoes[modulo.key]) {
        formulario.value.permissoes[modulo.key] = {}
      }
      acoes.forEach(acao => {
        if (formulario.value.permissoes[modulo.key][acao.key] === undefined) {
          formulario.value.permissoes[modulo.key][acao.key] = false
        }
      })
    })
  } else {
    formulario.value = {
      nome: '',
      slug: '',
      descricao: '',
      requer_vinculo: false,
      ativo: true,
      permissoes: inicializarPermissoes()
    }
  }
}, { immediate: true })

// Validação
const formularioValido = computed(() => {
  return formulario.value.nome.trim().length >= 3
})

// Funções
function marcarTodos(valor) {
  modulos.forEach(modulo => {
    acoes.forEach(acao => {
      formulario.value.permissoes[modulo.key][acao.key] = valor
    })
  })
}

function onPermissaoChange(moduloKey, acaoKey) {
  // Lógica adicional se necessário (ex: dependências)
  // Por exemplo: se marcar "editar", auto-marcar "ler"
  if (acaoKey === 'editar' && formulario.value.permissoes[moduloKey][acaoKey]) {
    formulario.value.permissoes[moduloKey]['ler'] = true
  }
  if (acaoKey === 'excluir' && formulario.value.permissoes[moduloKey][acaoKey]) {
    formulario.value.permissoes[moduloKey]['ler'] = true
  }
  if (acaoKey === 'criar' && formulario.value.permissoes[moduloKey][acaoKey]) {
    formulario.value.permissoes[moduloKey]['ler'] = true
  }
}

function salvar() {
  if (!formularioValido.value || salvando.value) return

  salvando.value = true
  emit('salvar', formulario.value)
}

function resetSalvando() {
  salvando.value = false
}

defineExpose({ resetSalvando })
</script>

<style scoped>
@keyframes shimmer {
  0% {
    transform: translateX(-100%);
  }
  100% {
    transform: translateX(100%);
  }
}

.animate-shimmer {
  animation: shimmer 3s infinite;
}
</style>
