<template>
  <Teleport to="body">
    <Transition
      enter-active-class="transition-opacity duration-300"
      enter-from-class="opacity-0"
      leave-active-class="transition-opacity duration-200"
      leave-from-class="opacity-100"
      leave-to-class="opacity-0"
    >
      <div
        v-if="aberto"
        class="fixed inset-0 z-[10040] flex items-stretch justify-end bg-black/55 backdrop-blur-sm"
        role="dialog"
        aria-modal="true"
        aria-labelledby="bib-modelos-title"
        @click.self="$emit('fechar')"
      >
        <Transition
          appear
          enter-active-class="transition-transform duration-300 ease-out"
          enter-from-class="translate-x-full"
          enter-to-class="translate-x-0"
          leave-active-class="transition-transform duration-200 ease-in"
          leave-from-class="translate-x-0"
          leave-to-class="translate-x-full"
        >
          <aside
            v-if="aberto"
            class="relative w-full max-w-5xl h-full bg-gradient-to-b from-slate-50 to-white dark:from-gray-900 dark:to-gray-950 shadow-2xl flex flex-col border-l border-gray-200 dark:border-gray-800"
          >
            <header class="flex-shrink-0 px-6 sm:px-8 pt-8 pb-5 border-b border-gray-200/80 dark:border-gray-800">
              <div class="flex items-start justify-between gap-4">
                <div>
                  <p class="text-xs font-semibold uppercase tracking-[0.2em] text-primary-600 dark:text-primary-400 mb-2">
                    Biblioteca M.Ouve
                  </p>
                  <h2 id="bib-modelos-title" class="text-2xl font-bold text-gray-900 dark:text-white flex items-center gap-2">
                    <SparklesIcon class="w-7 h-7 text-amber-500" />
                    Modelos prontos com IA
                  </h2>
                  <p class="text-sm text-gray-600 dark:text-gray-400 mt-2 max-w-xl">
                    Instale serviços pré-configurados na sua secretaria. Cada modelo inclui perguntas,
                    extração e fluxo conversacional já treinados.
                  </p>
                </div>
                <button
                  type="button"
                  class="p-2 rounded-lg hover:bg-gray-200/80 dark:hover:bg-gray-800 transition-colors"
                  aria-label="Fechar galeria"
                  @click="$emit('fechar')"
                >
                  <XMarkIcon class="w-6 h-6 text-gray-600 dark:text-gray-300" />
                </button>
              </div>
            </header>

            <div class="flex-1 overflow-y-auto px-6 sm:px-8 py-6">
              <div v-if="loading" class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                <div v-for="n in 6" :key="n" class="h-64 rounded-2xl bg-gray-200/60 dark:bg-gray-800 animate-pulse" />
              </div>

              <p
                v-else-if="!templates.length"
                class="text-center text-sm text-gray-500 dark:text-gray-400 py-16"
              >
                Nenhum modelo disponível. Execute <code class="text-xs bg-gray-100 dark:bg-gray-800 px-1 rounded">seed_templates</code> no servidor.
              </p>

              <div v-else class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
                <article
                  v-for="tpl in templates"
                  :key="tpl.id"
                  class="group relative flex flex-col rounded-2xl border border-gray-200/90 dark:border-gray-700 bg-white dark:bg-gray-900/80 shadow-md hover:shadow-xl hover:-translate-y-1 transition-all duration-300 overflow-hidden"
                >
                  <div
                    class="h-1.5 w-full bg-gradient-to-r opacity-90"
                    :class="gradienteBarra(tpl.icone)"
                  />

                  <div class="p-5 flex flex-col flex-1">
                    <div class="flex items-start gap-3 mb-3">
                      <div
                        class="w-12 h-12 rounded-xl flex items-center justify-center shadow-inner text-white shrink-0"
                        :class="classeGradienteIconeCategoria(tpl.icone)"
                      >
                        <component :is="componenteIconeCategoria(tpl.icone)" class="w-6 h-6" />
                      </div>
                      <div class="min-w-0 flex-1">
                        <h3 class="font-bold text-gray-900 dark:text-white leading-snug line-clamp-2">
                          {{ tpl.nome }}
                        </h3>
                        <p class="text-xs font-medium text-primary-600 dark:text-primary-400 mt-1">
                          {{ tpl.categoria_nome || 'Categoria' }}
                        </p>
                      </div>
                    </div>

                    <p class="text-sm text-gray-600 dark:text-gray-400 line-clamp-3 mb-4 flex-1">
                      {{ tpl.descricao || 'Modelo sem descrição.' }}
                    </p>

                    <p class="text-[11px] text-gray-500 dark:text-gray-500 mb-4">
                      {{ contarCampos(tpl.formulario_schema) }} dados mapeados · SLA {{ tpl.sla_padrao_horas }}h
                    </p>

                    <!-- Painel de clonagem inline -->
                    <div
                      v-if="expandidoId === tpl.id"
                      class="rounded-xl bg-gray-50 dark:bg-gray-800/80 border border-primary-200 dark:border-primary-800 p-3 mb-3 space-y-3"
                    >
                      <label class="block text-xs font-semibold text-gray-700 dark:text-gray-300">
                        Para qual secretaria / unidade?
                      </label>
                      <select v-model="unidadeSelecionada" class="input text-sm !py-2" :disabled="clonando">
                        <option value="">Selecione…</option>
                        <option v-for="u in unidades" :key="u.id" :value="String(u.id)">
                          {{ u.sigla ? `${u.sigla} — ` : '' }}{{ u.nome }}
                        </option>
                      </select>
                      <div class="flex gap-2">
                        <button
                          type="button"
                          class="btn-secondary flex-1 text-sm !py-2"
                          :disabled="clonando"
                          @click="cancelarExpansao"
                        >
                          Voltar
                        </button>
                        <button
                          type="button"
                          class="btn-primary flex-1 text-sm !py-2 inline-flex items-center justify-center gap-2"
                          :disabled="clonando || !unidadeSelecionada"
                          @click="confirmarClonagem(tpl)"
                        >
                          <span
                            v-if="clonando && expandidoId === tpl.id"
                            class="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin"
                          />
                          {{ clonando && expandidoId === tpl.id ? 'Instalando serviço…' : 'Confirmar' }}
                        </button>
                      </div>
                    </div>

                    <button
                      v-else
                      type="button"
                      class="w-full py-2.5 rounded-xl text-sm font-semibold bg-gradient-to-r from-primary-600 to-cyan-600 hover:from-primary-700 hover:to-cyan-700 text-white shadow-md group-hover:shadow-lg transition-all"
                      @click="abrirClonagem(tpl)"
                    >
                      Usar este modelo
                    </button>
                  </div>
                </article>
              </div>
            </div>
          </aside>
        </Transition>
      </div>
    </Transition>
  </Teleport>
</template>

<script setup>
import { computed, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { SparklesIcon, XMarkIcon } from '@heroicons/vue/24/outline'
import { useCatalogoStore } from '@/stores/catalogo'
import { useAdminStore } from '@/stores/admin'
import {
  classeGradienteIconeCategoria,
  componenteIconeCategoria,
  gradienteIconeCategoria
} from '@/utils/catalogoIcones'

const props = defineProps({
  aberto: { type: Boolean, default: false }
})

const emit = defineEmits(['fechar', 'clonado'])

const catalogoStore = useCatalogoStore()
const adminStore = useAdminStore()
const { templates, loadingTemplates, clonandoTemplate } = storeToRefs(catalogoStore)
const { unidadesAtivas } = storeToRefs(adminStore)

const loading = computed(() => loadingTemplates.value)
const clonando = computed(() => clonandoTemplate.value)
const unidades = computed(() => unidadesAtivas.value)

const expandidoId = ref(null)
const unidadeSelecionada = ref('')

function gradienteBarra(icone) {
  return gradienteIconeCategoria(icone)
}

function contarCampos(schema) {
  if (!Array.isArray(schema)) return 0
  return schema.length
}

function abrirClonagem(tpl) {
  expandidoId.value = tpl.id
  unidadeSelecionada.value = ''
}

function cancelarExpansao() {
  expandidoId.value = null
  unidadeSelecionada.value = ''
}

async function confirmarClonagem(tpl) {
  if (!unidadeSelecionada.value || clonando.value) return
  try {
    const novo = await catalogoStore.clonarTemplate(tpl.id, unidadeSelecionada.value)
    emit('clonado', novo)
  } catch (err) {
    console.error('Erro ao clonar template:', err)
  }
}

watch(
  () => props.aberto,
  async (open) => {
    if (!open) {
      cancelarExpansao()
      return
    }
    await Promise.all([
      catalogoStore.buscarTemplates().catch(() => {}),
      adminStore.carregarUnidades({ silencioso: true }).catch(() => {})
    ])
  }
)
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.line-clamp-3 {
  display: -webkit-box;
  -webkit-line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
</style>