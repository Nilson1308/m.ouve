<template>
  <section
    class="rounded-modal overflow-hidden border-2 border-purple-300 dark:border-purple-700 shadow-float bg-white dark:bg-gray-900"
  >
    <!-- Header -->
    <div class="px-6 py-5 bg-gradient-to-r from-purple-600 to-primary-600 text-white">
      <div class="flex items-start gap-4">
        <div class="w-14 h-14 rounded-xl bg-white/20 backdrop-blur-sm flex items-center justify-center shrink-0">
          <ShieldCheckIcon class="w-7 h-7" />
        </div>
        <div class="min-w-0">
          <h2 class="text-xl font-bold">Despacho final — validação da Ouvidoria</h2>
          <p class="text-sm text-purple-100 mt-1 leading-relaxed">
            Encerra o protocolo, envia a resposta ao cidadão e libera a
            <strong class="text-white">avaliação do atendimento</strong> no aplicativo.
          </p>
        </div>
      </div>
    </div>

    <div class="p-6 space-y-5">
      <div class="alert-info">
        <InformationCircleIcon class="w-5 h-5 shrink-0 text-primary-500" />
        <p class="text-sm">
          Gather completo: {{ nosResumo.fechados }}/{{ nosResumo.total }} nós encerrados.
          Revise as evidências abaixo antes de validar.
        </p>
      </div>

      <!-- Evidências para o cidadão -->
      <div v-if="evidencias.length" class="rounded-lg border border-gray-200 dark:border-gray-700 p-4 bg-gray-50 dark:bg-gray-800/50">
        <div class="flex flex-wrap items-center justify-between gap-2 mb-3">
          <h3 class="text-sm font-semibold text-gray-900 dark:text-white flex items-center gap-2">
            <PhotoIcon class="w-5 h-5 text-purple-500" />
            Evidências do serviço ({{ evidencias.length }})
          </h3>
          <button type="button" class="text-xs font-medium text-primary-600 dark:text-primary-400 hover:underline" @click="alternarTodasEvidencias">
            {{ todasEvidenciasSelecionadas ? 'Desmarcar todas' : 'Selecionar todas' }}
          </button>
        </div>
        <p class="text-xs text-gray-600 dark:text-gray-400 mb-3">
          As fotos marcadas serão referenciadas na mensagem ao cidadão e permanecem visíveis na consulta do protocolo no app.
        </p>
        <div class="grid grid-cols-2 sm:grid-cols-3 gap-3 max-h-64 overflow-y-auto pr-1">
          <button
            v-for="ev in evidencias"
            :key="ev.id"
            type="button"
            class="relative text-left cursor-pointer rounded-lg border-2 overflow-hidden transition-colors"
            :class="
              selecionadas.has(ev.id)
                ? 'border-purple-500 ring-2 ring-purple-500/30'
                : 'border-gray-200 dark:border-gray-600 opacity-80 hover:opacity-100'
            "
            @click="toggleEvidencia(ev.id)"
          >
            <div class="aspect-square bg-gray-100 dark:bg-gray-700">
              <img :src="ev.url" :alt="ev.legenda" class="w-full h-full object-cover" />
            </div>
            <div class="absolute top-1.5 right-1.5">
              <span
                class="w-5 h-5 rounded-full flex items-center justify-center text-xs"
                :class="selecionadas.has(ev.id) ? 'bg-purple-600 text-white' : 'bg-black/40 text-white'"
              >
                {{ selecionadas.has(ev.id) ? '✓' : '' }}
              </span>
            </div>
            <p class="text-[10px] px-2 py-1 truncate text-gray-700 dark:text-gray-300 bg-white/90 dark:bg-gray-900/90">
              {{ ev.secretaria }} · {{ ev.legenda }}
            </p>
          </button>
        </div>
      </div>

      <!-- Relatos de campo -->
      <div v-if="relatos.length" class="rounded-lg border border-success-200 dark:border-success-800 bg-success-50/50 dark:bg-success-900/15 p-4">
        <label class="flex items-start gap-3 cursor-pointer">
          <input v-model="incluirRelatoCampo" type="checkbox" class="mt-1 rounded border-gray-300 text-purple-600 focus:ring-purple-500" />
          <div class="min-w-0 flex-1">
            <span class="text-sm font-semibold text-gray-900 dark:text-white">Incluir relato das equipes na resposta</span>
            <ul class="mt-2 space-y-2 text-xs text-gray-700 dark:text-gray-300">
              <li v-for="r in relatos" :key="r.ordemId">
                <strong>{{ r.secretaria }}:</strong> {{ r.texto }}
              </li>
            </ul>
          </div>
        </label>
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Resposta ao cidadão *
        </label>
        <select
          v-model="respostaSelecionada"
          class="input w-full mb-2"
          :disabled="carregandoTextos"
        >
          <option value="">
            {{ carregandoTextos ? 'Carregando textos padrão…' : 'Selecione um texto padrão ou escreva abaixo' }}
          </option>
          <option v-for="t in textosAtivos" :key="t.id" :value="t.texto">
            {{ t.titulo }}
          </option>
        </select>
        <textarea
          v-model="respostaLivre"
          rows="5"
          class="input w-full resize-none"
          placeholder="Personalize a mensagem que o cidadão receberá (notificação e consulta do protocolo)…"
        />
      </div>

      <div>
        <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">
          Observações internas (opcional)
        </label>
        <textarea
          v-model="observacoes"
          rows="2"
          class="input w-full resize-none"
          placeholder="Uso exclusivo da Ouvidoria — não é enviado ao cidadão."
        />
      </div>

      <div class="rounded-lg border border-purple-200 dark:border-purple-800 bg-purple-50/80 dark:bg-purple-900/20 p-4">
        <p class="text-xs font-semibold uppercase tracking-wide text-purple-800 dark:text-purple-200 mb-2">
          Prévia da mensagem ao cidadão
        </p>
        <p class="text-sm text-gray-800 dark:text-gray-200 whitespace-pre-wrap leading-relaxed">
          {{ previewCidadao || 'Selecione ou redija a resposta acima.' }}
        </p>
      </div>

      <div class="flex items-start gap-2 text-xs text-gray-500 dark:text-gray-400">
        <StarIcon class="w-4 h-4 text-amber-500 shrink-0 mt-0.5" />
        <span>Ao validar, o cidadão poderá <strong>avaliar o atendimento</strong> no aplicativo M.Ouve.</span>
      </div>

      <p v-if="!textoRespostaValido" class="text-xs text-amber-700 dark:text-amber-300">
        Informe a resposta ao cidadão para habilitar a validação.
      </p>

      <div class="space-y-3 pt-2 border-t border-gray-200 dark:border-gray-700">
        <button
          type="button"
          class="w-full btn-lg bg-purple-600 hover:bg-purple-700 text-white shadow-button flex items-center justify-center gap-2 disabled:opacity-50"
          :disabled="!textoRespostaValido || salvandoValidacao || salvandoDevolucao"
          @click="validarProtocolo"
        >
          <CheckCircleIcon class="w-5 h-5" />
          {{ salvandoValidacao ? 'Validando e notificando cidadão…' : 'Validar, responder ao cidadão e encerrar' }}
        </button>

        <button
          type="button"
          class="w-full btn-secondary text-danger-600 border-danger-200 hover:bg-danger-50 dark:hover:bg-danger-900/20"
          :disabled="salvandoValidacao || salvandoDevolucao"
          @click="mostrarModalDevolucao = true"
        >
          <ArrowUturnLeftIcon class="w-5 h-5 inline mr-1" />
          Devolver ordem à secretaria
        </button>
      </div>
    </div>

    <!-- Modal devolução -->
    <Transition name="fade">
      <div
        v-if="mostrarModalDevolucao"
        class="fixed inset-0 bg-black/50 backdrop-blur-sm z-[80] flex items-center justify-center p-4"
        @click.self="mostrarModalDevolucao = false"
      >
        <div class="bg-white dark:bg-gray-800 rounded-modal p-6 max-w-md w-full shadow-float border border-gray-200 dark:border-gray-700">
          <h3 class="text-xl font-bold text-gray-900 dark:text-white mb-4">Devolver à secretaria</h3>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Ordem de serviço</label>
            <select v-model="ordemDevolucaoId" class="input w-full">
              <option value="">Selecione…</option>
              <option v-for="ordem in ordensDevolviveis" :key="ordem.id" :value="ordem.id">
                {{ ordem.unidade }} — Concluída
              </option>
            </select>
          </div>
          <div class="mb-4">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Motivo</label>
            <select v-model="motivoDevolucao" class="input w-full">
              <option value="">Selecione…</option>
              <option value="foto_inadequada">Foto inadequada ou incompleta</option>
              <option value="servico_incompleto">Serviço incompleto</option>
              <option value="fora_padrao">Fora do padrão técnico</option>
              <option value="local_errado">Local incorreto</option>
              <option value="outro">Outro</option>
            </select>
          </div>
          <div class="mb-6">
            <label class="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2">Justificativa</label>
            <textarea v-model="justificativaDevolucao" rows="4" class="input w-full resize-none" />
          </div>
          <div class="flex gap-3">
            <button type="button" class="flex-1 btn-secondary" @click="mostrarModalDevolucao = false">Cancelar</button>
            <button
              type="button"
              class="flex-1 btn-danger disabled:opacity-50"
              :disabled="!ordemDevolucaoId || !motivoDevolucao || !justificativaDevolucao || salvandoDevolucao"
              @click="confirmarDevolucao"
            >
              {{ salvandoDevolucao ? 'Enviando…' : 'Confirmar' }}
            </button>
          </div>
        </div>
      </div>
    </Transition>
  </section>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import {
  ShieldCheckIcon,
  InformationCircleIcon,
  CheckCircleIcon,
  ArrowUturnLeftIcon,
  PhotoIcon,
  StarIcon
} from '@heroicons/vue/24/outline'
import { storeToRefs } from 'pinia'
import { useTextosPadraoStore } from '@/stores/textosPadrao'
import { evidenciasDoProtocolo, relatosCampoPorOrdem } from '@/utils/protocoloEvidencias'
import { resumoNos } from '@/utils/scatterGather'

const props = defineProps({
  protocolo: { type: Object, required: true },
  salvandoValidacao: { type: Boolean, default: false },
  salvandoDevolucao: { type: Boolean, default: false }
})

const emit = defineEmits(['validar', 'devolver'])

const textosStore = useTextosPadraoStore()
const { itens: textosPadrao, loading: carregandoTextos } = storeToRefs(textosStore)

const respostaSelecionada = ref('')
const respostaLivre = ref('')
const observacoes = ref('')
const incluirRelatoCampo = ref(true)
const selecionadasIds = ref([])
const mostrarModalDevolucao = ref(false)
const motivoDevolucao = ref('')
const justificativaDevolucao = ref('')
const ordemDevolucaoId = ref('')

const nosResumo = computed(() => resumoNos(props.protocolo?.ordens_servico))
const evidencias = computed(() => evidenciasDoProtocolo(props.protocolo?.ordens_servico))
const relatos = computed(() => relatosCampoPorOrdem(props.protocolo?.ordens_servico))

const selecionadas = computed(() => new Set(selecionadasIds.value))

const textosAtivos = computed(() => (textosPadrao.value || []).filter((t) => t.ativo !== false))

const todasEvidenciasSelecionadas = computed(
  () => evidencias.value.length > 0 && selecionadasIds.value.length === evidencias.value.length
)

watch(
  evidencias,
  (lista) => {
    selecionadasIds.value = lista.map((e) => e.id)
  },
  { immediate: true }
)

watch(respostaSelecionada, (v) => {
  if (v && !respostaLivre.value) respostaLivre.value = v
})

const textoBase = computed(() => (respostaLivre.value || respostaSelecionada.value || '').trim())

const textoRespostaValido = computed(() => textoBase.value.length >= 20)

const previewCidadao = computed(() => montarMensagemCidadao(textoBase.value, false))

const ordensDevolviveis = computed(() => {
  const ordens = props.protocolo?.ordens_servico || []
  return ordens.filter((o) => o.status === 'concluido' || o.statusApi === 'concluida')
})

onMounted(() => {
  textosStore.carregar().catch(() => null)
})

function alternarTodasEvidencias() {
  if (todasEvidenciasSelecionadas.value) {
    selecionadasIds.value = []
  } else {
    selecionadasIds.value = evidencias.value.map((e) => e.id)
  }
}

function toggleEvidencia(id) {
  const set = new Set(selecionadasIds.value)
  if (set.has(id)) set.delete(id)
  else set.add(id)
  selecionadasIds.value = [...set]
}

function montarMensagemCidadao(texto, paraEnvio = true) {
  if (!texto) return ''
  const partes = [texto]
  if (incluirRelatoCampo.value && relatos.value.length) {
    const bloco = relatos.value.map((r) => `• ${r.secretaria}: ${r.texto}`).join('\n')
    partes.push('\n\nRelato das equipes de campo:\n' + bloco)
  }
  const selecionadasEv = evidencias.value.filter((e) => selecionadas.value.has(e.id))
  if (selecionadasEv.length) {
    if (paraEnvio) {
      const links = selecionadasEv.map((e) => `• ${e.secretaria} — ${e.legenda}: ${e.url}`)
      partes.push('\n\nEvidências do serviço realizado:\n' + links.join('\n'))
    } else {
      partes.push(
        `\n\n[${selecionadasEv.length} foto(s) de evidência incluída(s) na consulta do protocolo.]`
      )
    }
  }
  return partes.join('')
}

function validarProtocolo() {
  if (!textoRespostaValido.value) return
  emit('validar', {
    resposta: montarMensagemCidadao(textoBase.value, true),
    observacoes: observacoes.value
  })
}

function confirmarDevolucao() {
  emit('devolver', {
    ordemId: ordemDevolucaoId.value,
    motivo: motivoDevolucao.value,
    justificativa: justificativaDevolucao.value
  })
  mostrarModalDevolucao.value = false
  motivoDevolucao.value = ''
  justificativaDevolucao.value = ''
  ordemDevolucaoId.value = ''
}
</script>

<style scoped>
.btn-lg {
  @apply px-5 py-3 rounded-button text-sm font-semibold transition-all;
}
.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.2s ease;
}
.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}
</style>