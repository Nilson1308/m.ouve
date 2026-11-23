<template>
  <section>
  <!-- Cabeçalho + guia rápida -->
  <div class="mb-5 rounded-xl border border-primary-100 dark:border-primary-900/40 bg-gradient-to-r from-primary-50/80 to-cyan-50/50 dark:from-primary-950/30 dark:to-cyan-950/20 p-4">
    <div class="flex flex-col sm:flex-row sm:items-start justify-between gap-4">
      <div class="flex-1">
        <h3 class="text-sm font-bold text-gray-900 dark:text-white flex items-center gap-2">
          <CpuChipIcon class="w-5 h-5 text-primary-600 dark:text-primary-400" />
          Roteiro da conversa no PWA
        </h3>
        <p class="text-xs text-gray-600 dark:text-gray-400 mt-1 max-w-2xl">
          Defina <strong>na ordem</strong> o que o assistente pergunta. Cada passo vira mensagem no chat — com
          textos, botões de escolha, mapa ou foto, conforme o tipo.
        </p>
        <ol class="mt-3 space-y-1 text-xs text-gray-600 dark:text-gray-400 list-decimal list-inside">
          <li>Escreva a <strong>pergunta</strong> como se fosse um atendente humano.</li>
          <li>Escolha o <strong>tipo de resposta</strong> (texto, lista, mapa, imagem).</li>
          <li>Use o <strong>ordenador</strong> (<code class="text-[10px]">≡</code>) para definir a sequência do chat.</li>
          <li>Opcional: <strong>regra de elegibilidade</strong> — encerrar com mensagem se a resposta não puder ser atendida.</li>
        </ol>
        <p class="mt-2 text-[11px] text-amber-800 dark:text-amber-200 bg-amber-50 dark:bg-amber-950/40 border border-amber-200 dark:border-amber-800 rounded-lg px-3 py-2 max-w-2xl">
          <strong>Mapa:</strong> use só um passo tipo «Mapa». Texto de endereço não substitui o GPS. Não duplique localização em passos de texto.
        </p>
      </div>
      <button
        type="button"
        class="inline-flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-primary-600 to-cyan-500 hover:from-primary-700 hover:to-cyan-600 text-white rounded-lg font-medium text-sm transition-colors shadow-lg shadow-primary-500/30 shrink-0"
        @click="adicionarRequisito"
      >
        <PlusCircleIcon class="w-5 h-5" />
        Adicionar passo
      </button>
    </div>
  </div>

    <div
      v-if="!modelValue.length"
      class="rounded-xl border-2 border-dashed border-primary-200 dark:border-primary-800 bg-gray-50 dark:bg-gray-800/50 p-10 text-center"
    >
      <SparklesIcon class="w-12 h-12 mx-auto text-primary-400 mb-3" />
      <h4 class="text-base font-semibold text-gray-900 dark:text-white mb-2">Nenhum passo configurado</h4>
      <p class="text-sm text-gray-600 dark:text-gray-400 mb-4 max-w-md mx-auto">
        Ex.: “Qual a idade aproximada do animal?” → Tipo texto → Obrigatório.
      </p>
      <button type="button" class="btn-primary text-sm !py-2 !px-4" @click="adicionarRequisito">
        Criar primeiro passo
      </button>
    </div>

    <div
      v-else
      class="relative pl-0 sm:pl-3 space-y-5"
    >
      <!-- Ordenador compacto do fluxo -->
      <div
        v-if="modelValue.length > 0"
        class="rounded-xl border border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800/90 shadow-soft p-3 sm:p-4"
      >
        <div class="flex items-center justify-between gap-2 mb-3">
          <p class="text-xs font-bold uppercase tracking-wide text-gray-700 dark:text-gray-300 flex items-center gap-2">
            <Bars3Icon class="w-4 h-4 text-primary-600" />
            Ordem do fluxo
          </p>
          <span class="text-[10px] text-gray-500 dark:text-gray-400">
            Arraste para reordenar · {{ modelValue.length }} passo(s)
          </span>
        </div>
        <ol class="space-y-1.5" role="list" aria-label="Ordem dos passos da conversa">
          <li
            v-for="(item, index) in modelValue"
            :key="`ordem-${item._id}`"
            role="listitem"
            class="flex items-center gap-2 rounded-lg border px-2 py-1.5 transition-all"
            :class="[
              dragFromIndex === index ? 'opacity-50 scale-[0.99]' : '',
              dragOverIndex === index && dragFromIndex !== null && dragFromIndex !== index
                ? 'border-primary-400 bg-primary-50/80 dark:bg-primary-950/30 ring-1 ring-primary-400/50'
                : 'border-gray-200 dark:border-gray-600 bg-gray-50/80 dark:bg-gray-900/40'
            ]"
            @dragover.prevent="onDragOver(index)"
            @dragleave="onDragLeave(index)"
            @drop.prevent="onDrop(index)"
          >
            <button
              type="button"
              class="p-1.5 rounded-md text-gray-400 hover:text-gray-700 hover:bg-gray-200/80 dark:hover:bg-gray-700 cursor-grab active:cursor-grabbing touch-none shrink-0"
              title="Arrastar para reordenar"
              draggable="true"
              :aria-label="`Arrastar passo ${index + 1}`"
              @dragstart="onDragStart(index, $event)"
              @dragend="onDragEnd"
            >
              <Bars3Icon class="w-4 h-4 pointer-events-none" aria-hidden="true" />
            </button>
            <span
              class="flex h-7 w-7 items-center justify-center rounded-full bg-primary-600 text-white text-xs font-bold shrink-0"
            >
              {{ index + 1 }}
            </span>
            <button
              type="button"
              class="min-w-0 flex-1 text-left text-xs text-gray-800 dark:text-gray-200 truncate hover:text-primary-700 dark:hover:text-primary-300"
              :title="item.pergunta || 'Defina a pergunta…'"
              @click="scrollParaPasso(item._id)"
            >
              {{ item.pergunta || 'Passo sem pergunta…' }}
            </button>
            <span
              class="text-[10px] font-semibold uppercase tracking-wide text-gray-500 dark:text-gray-400 shrink-0 hidden sm:inline"
            >
              {{ rotuloTipo(item.type) }}
            </span>
          </li>
        </ol>
      </div>

      <div
        class="hidden sm:block absolute left-4 top-4 bottom-4 w-0.5 bg-gradient-to-b from-primary-300 via-cyan-300 to-transparent dark:from-primary-700 dark:via-cyan-800"
        aria-hidden="true"
      />

      <TransitionGroup name="flow-list" tag="div" class="space-y-5">
        <article
          v-for="(item, index) in modelValue"
          :id="passoDomId(item._id)"
          :key="item._id"
          class="card !p-0 overflow-hidden border-primary-100 dark:border-gray-700 transition-all duration-300 scroll-mt-24"
          :class="[
            dragFromIndex === index ? 'opacity-60' : '',
            dragOverIndex === index && dragFromIndex !== null && dragFromIndex !== index
              ? 'ring-2 ring-primary-400/60 border-primary-300'
              : ''
          ]"
          @dragover.prevent="onDragOver(index)"
          @dragleave="onDragLeave(index)"
          @drop.prevent="onDrop(index)"
        >
          <header
            class="flex items-start justify-between gap-3 px-4 py-3 border-b border-gray-100 dark:border-gray-700 bg-white dark:bg-gray-800"
          >
            <div class="flex items-center gap-3 min-w-0">
              <button
                type="button"
                class="p-1.5 -ml-1 rounded-lg text-gray-400 hover:text-gray-600 hover:bg-gray-100 dark:hover:bg-gray-700 cursor-grab active:cursor-grabbing touch-none shrink-0 hidden sm:flex"
                title="Arrastar passo"
                draggable="true"
                :aria-label="`Arrastar passo ${index + 1}`"
                @dragstart="onDragStart(index, $event)"
                @dragend="onDragEnd"
              >
                <Bars3Icon class="w-5 h-5 pointer-events-none" />
              </button>
              <span
                class="flex h-9 w-9 items-center justify-center rounded-full bg-primary-600 text-white text-sm font-bold shadow-md shrink-0"
              >
                {{ index + 1 }}
              </span>
              <div class="min-w-0">
                <p class="text-[10px] font-bold uppercase tracking-wider text-primary-600 dark:text-primary-400">
                  Passo {{ index + 1 }} · {{ rotuloTipo(item.type) }}
                </p>
                <p class="text-sm font-semibold text-gray-900 dark:text-white truncate">
                  {{ item.pergunta || 'Defina a pergunta ao cidadão…' }}
                </p>
              </div>
            </div>
            <div class="flex items-center gap-0.5 shrink-0">
              <button
                type="button"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-30"
                :disabled="index === 0"
                title="Subir um passo"
                @click="mover(index, -1)"
              >
                <ChevronUpIcon class="w-4 h-4" />
              </button>
              <button
                type="button"
                class="p-2 rounded-lg text-gray-500 hover:bg-gray-100 dark:hover:bg-gray-700 disabled:opacity-30"
                :disabled="index === modelValue.length - 1"
                title="Descer um passo"
                @click="mover(index, 1)"
              >
                <ChevronDownIcon class="w-4 h-4" />
              </button>
              <button type="button" class="p-2 rounded-lg text-red-600 hover:bg-red-50 dark:hover:bg-red-900/30" @click="remover(index)">
                <TrashIcon class="w-4 h-4" />
              </button>
            </div>
          </header>

          <div class="p-4 space-y-5">
            <!-- 1 — Pergunta (principal) -->
            <div class="rounded-lg border-2 border-primary-200 dark:border-primary-800 bg-primary-50/50 dark:bg-primary-950/20 p-4">
              <label class="flex items-center gap-2 text-sm font-bold text-gray-900 dark:text-white mb-2">
                <ChatBubbleLeftRightIcon class="w-5 h-5 text-primary-600" />
                Como o assistente pergunta? *
              </label>
              <textarea
                :value="item.pergunta"
                rows="2"
                class="input text-sm min-h-[72px]"
                :placeholder="placeholderPergunta(item.type)"
                @input="onPerguntaInput(index, $event)"
              />
              <p class="text-[11px] text-gray-500 dark:text-gray-400 mt-2">
                Uma pergunta completa, em uma frase (ex.: «Qual é o seu animal de estimação?»). Não repita «Qual é o…» nem
                coloque instruções longas aqui — dicas da IA ficam nos campos abaixo. Em listas, as opções aparecem nos botões.
              </p>

              <!-- Prévia do chat -->
              <div class="mt-3 flex items-start gap-2">
                <div class="w-7 h-7 rounded-full bg-primary-500 flex items-center justify-center shrink-0">
                  <SparklesIcon class="w-3.5 h-3.5 text-white" />
                </div>
                <div class="rounded-2xl rounded-tl-sm bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 px-3 py-2 shadow-soft max-w-md">
                  <p class="text-xs text-gray-800 dark:text-gray-100 leading-relaxed">
                    {{ textoPreview(item) }}
                  </p>
                  <p v-if="item.type === 'select'" class="text-[10px] text-primary-600 mt-1">+ botões de escolha</p>
                  <p v-else-if="item.type === 'lookup'" class="text-[10px] text-primary-600 mt-1">+ lista de unidades (API)</p>
                  <p v-else-if="item.type === 'geo'" class="text-[10px] text-primary-600 mt-1">+ mapa de localização</p>
                  <p v-else-if="item.type === 'image'" class="text-[10px] text-primary-600 mt-1">+ envio de foto</p>
                </div>
              </div>
            </div>

            <!-- 2 — Tipo -->
            <div>
              <p class="text-xs font-bold text-gray-700 dark:text-gray-300 mb-2 uppercase tracking-wide">
                Tipo de resposta
              </p>
              <div class="grid grid-cols-2 lg:grid-cols-4 gap-2">
                <button
                  v-for="t in tiposDado"
                  :key="t.value"
                  type="button"
                  :class="tipoCardClass(item.type === t.value)"
                  @click="selecionarTipo(index, t.value)"
                >
                  <component :is="t.icon" class="w-5 h-5 mb-1" :class="item.type === t.value ? 'text-primary-600' : 'text-gray-500'" />
                  <span class="text-xs font-semibold block">{{ t.label }}</span>
                  <span class="text-[10px] text-gray-500 dark:text-gray-400 leading-tight mt-0.5 block">{{ t.dica }}</span>
                </button>
              </div>
            </div>

            <p
              v-if="item.type === 'geo'"
              class="text-xs text-cyan-800 dark:text-cyan-200 bg-cyan-50 dark:bg-cyan-950/30 border border-cyan-200 dark:border-cyan-800 rounded-lg px-3 py-2"
            >
              O cidadão verá o <strong>mapa</strong>. A resposta por texto não encerra este passo — só «Confirmar Local».
            </p>

            <p
              v-if="item.type === 'lookup'"
              class="text-xs text-cyan-800 dark:text-cyan-200 bg-cyan-50 dark:bg-cyan-950/30 border border-cyan-200 dark:border-cyan-800 rounded-lg px-3 py-2"
            >
              O PWA carrega as <strong>unidades administrativas ativas</strong> via API
              (<code class="text-[10px]">/catalogo/lookup/unidades</code>). O valor salvo é o UUID da unidade.
            </p>

            <div v-if="item.type === 'select'">
              <label class="block text-sm font-semibold text-gray-700 dark:text-gray-300 mb-2">
                Opções da lista <span class="font-normal text-gray-500">(uma por linha)</span>
              </label>
              <textarea
                :value="item.optionsText"
                rows="4"
                class="input text-sm font-mono min-h-[96px]"
                placeholder="Pequeno&#10;Médio&#10;Grande"
                @input="patch(index, { optionsText: $event.target.value })"
              />
            </div>

            <!-- 3 — Avançado -->
            <details class="group rounded-lg border border-gray-200 dark:border-gray-600 bg-gray-50/80 dark:bg-gray-900/40">
              <summary class="cursor-pointer px-4 py-3 text-sm font-semibold text-gray-800 dark:text-gray-200 list-none flex items-center justify-between">
                <span class="flex items-center gap-2">
                  <AdjustmentsHorizontalIcon class="w-4 h-4 text-gray-500" />
                  Ajustes para a IA e protocolo
                </span>
                <ChevronDownIcon class="w-4 h-4 text-gray-400 group-open:rotate-180 transition-transform" />
              </summary>
              <div class="px-4 pb-4 space-y-4 border-t border-gray-200 dark:border-gray-600 pt-4">
                <div>
                  <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">
                    Chave no protocolo (técnico, snake_case)
                  </label>
                  <input
                    :value="item.name"
                    type="text"
                    class="input font-mono text-xs !py-2"
                    placeholder="idade_animal"
                    @input="onNameInput(index, $event)"
                  />
                  <p class="text-[10px] text-gray-500 mt-1">Salvo em <code class="font-mono">dados_dinamicos</code>. Gerado a partir da pergunta se vazio.</p>
                </div>

                <div>
                  <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">
                    Como interpretar respostas livres
                    <span class="font-normal">(opcional)</span>
                  </label>
                  <textarea
                    :value="item.ia_instrucao"
                    rows="2"
                    class="input text-sm min-h-[64px]"
                    placeholder="Ex.: Extraia a idade em anos; se disser filhote, registre como menos de 1 ano."
                    @input="patch(index, { ia_instrucao: $event.target.value })"
                  />
                </div>

                <div>
                  <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">
                    Se o cidadão não responder direito
                    <span class="font-normal">(opcional)</span>
                  </label>
                  <textarea
                    :value="item.ia_repescagem"
                    rows="2"
                    class="input text-sm min-h-[64px]"
                    placeholder="Ex.: Você poderia confirmar se o animal apresenta alguma doença ou sintoma?"
                    @input="patch(index, { ia_repescagem: $event.target.value })"
                  />
                </div>

                <div class="rounded-lg border border-amber-200 dark:border-amber-800 bg-amber-50/60 dark:bg-amber-950/20 p-4 space-y-3">
                  <label class="flex items-start gap-3 cursor-pointer">
                    <input
                      type="checkbox"
                      class="mt-0.5 w-4 h-4 text-amber-600 rounded"
                      :checked="item.regra_elegibilidade_ativa"
                      @change="patch(index, { regra_elegibilidade_ativa: $event.target.checked })"
                    />
                    <span class="text-sm font-semibold text-gray-900 dark:text-white">
                      Regra de elegibilidade neste passo
                    </span>
                  </label>
                  <p class="text-[11px] text-gray-600 dark:text-gray-400">
                    Descreva a condição em linguagem natural — a IA interpreta a resposta. Sem precisar alterar código a cada regra nova.
                  </p>
                  <p
                    v-if="item.regra_elegibilidade_ativa && ehTipoEscolha(item.type)"
                    class="text-xs text-amber-800 dark:text-amber-200 bg-white/60 dark:bg-gray-900/40 border border-amber-200/80 dark:border-amber-800/60 rounded-lg px-2.5 py-2 leading-snug"
                  >
                    Esta regra avalia apenas a <strong>opção selecionada neste passo</strong> — não analisa textos livres
                    de outros passos.
                  </p>
                  <template v-if="item.regra_elegibilidade_ativa">
                    <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">Modo</label>
                    <select
                      :value="item.regra_tipo || 'interpretacao'"
                      class="input text-sm !py-2"
                      @change="patch(index, { regra_tipo: $event.target.value })"
                    >
                      <option value="interpretacao">Interpretação (recomendado)</option>
                      <option value="texto">Lista exata de palavras (rápido, sem IA)</option>
                    </select>

                    <template v-if="(item.regra_tipo || 'interpretacao') === 'interpretacao'">
                      <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1 mt-2">
                        Bloquear o atendimento quando…
                      </label>
                      <textarea
                        :value="item.regra_condicao"
                        rows="3"
                        class="input text-sm min-h-[80px]"
                        placeholder="Ex.: a idade do animal for menor que 12 meses ou maior que 9 anos."
                        @input="patch(index, { regra_condicao: $event.target.value })"
                      />
                      <div class="flex flex-wrap gap-2 mt-2">
                        <button
                          type="button"
                          class="text-[11px] px-2 py-1 rounded-md bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:border-primary-400"
                          @click="aplicarModeloRegra(index, 'idade')"
                        >
                          Modelo: faixa de idade
                        </button>
                        <button
                          type="button"
                          class="text-[11px] px-2 py-1 rounded-md bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-600 text-gray-700 dark:text-gray-300 hover:border-primary-400"
                          @click="aplicarModeloRegra(index, 'doenca')"
                        >
                          Modelo: animal doente
                        </button>
                      </div>
                    </template>

                    <template v-else>
                      <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">
                        Respostas que bloqueiam (uma por linha)
                      </label>
                      <textarea
                        :value="item.regra_texto_valores"
                        rows="2"
                        class="input text-sm font-mono min-h-[56px]"
                        placeholder="sim&#10;com doença"
                        @input="patch(index, { regra_texto_valores: $event.target.value })"
                      />
                    </template>

                    <label class="block text-xs font-semibold text-gray-600 dark:text-gray-400 mb-1">
                      Mensagem para o cidadão
                    </label>
                    <textarea
                      :value="item.regra_elegibilidade_mensagem"
                      rows="3"
                      class="input text-sm min-h-[72px]"
                      :placeholder="placeholderRegra(item)"
                      @input="patch(index, { regra_elegibilidade_mensagem: $event.target.value })"
                    />
                  </template>
                </div>

                <label class="flex items-center gap-3 p-3 rounded-lg bg-white dark:bg-gray-800 border border-gray-200 dark:border-gray-700 cursor-pointer">
                  <input
                    :id="`req-${item._id}`"
                    type="checkbox"
                    class="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
                    :checked="item.required"
                    @change="patch(index, { required: $event.target.checked })"
                  />
                  <span class="text-sm font-medium text-gray-900 dark:text-white">
                    Obrigatório — o assistente só avança depois de obter este dado
                  </span>
                </label>
              </div>
            </details>
          </div>
        </article>
      </TransitionGroup>
    </div>
  </section>
</template>

<script setup>
import { ref } from 'vue'
import {
  PlusCircleIcon,
  TrashIcon,
  ChevronUpIcon,
  ChevronDownIcon,
  Bars3Icon,
  CpuChipIcon,
  SparklesIcon,
  ChatBubbleLeftRightIcon,
  AdjustmentsHorizontalIcon,
  MapPinIcon,
  PhotoIcon,
  ListBulletIcon,
  PencilSquareIcon
} from '@heroicons/vue/24/outline'
import { labelParaName } from '@/utils/catalogoMappers'
import { LOOKUP_DATASOURCE_UNIDADES } from '@/constants/fluxoTramitacao'
import { BuildingOffice2Icon } from '@heroicons/vue/24/outline'

const props = defineProps({
  modelValue: {
    type: Array,
    default: () => []
  }
})

const emit = defineEmits(['update:modelValue'])

let seq = 0

const dragFromIndex = ref(null)
const dragOverIndex = ref(null)

function passoDomId(id) {
  return `passo-fluxo-${id}`
}

function scrollParaPasso(id) {
  const el = document.getElementById(passoDomId(id))
  el?.scrollIntoView({ behavior: 'smooth', block: 'start' })
}

function limparDrag() {
  dragFromIndex.value = null
  dragOverIndex.value = null
}

function onDragStart(index, event) {
  dragFromIndex.value = index
  if (event?.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/plain', String(index))
  }
}

function onDragOver(index) {
  if (dragFromIndex.value === null) return
  dragOverIndex.value = index
}

function onDragLeave(index) {
  if (dragOverIndex.value === index) dragOverIndex.value = null
}

function onDrop(index) {
  const from = dragFromIndex.value
  if (from === null || from === index) {
    limparDrag()
    return
  }
  reordenarLista(from, index)
  limparDrag()
}

function onDragEnd() {
  limparDrag()
}

function reordenarLista(from, to) {
  if (from === to || from < 0 || to < 0 || from >= props.modelValue.length || to >= props.modelValue.length) {
    return
  }
  const lista = [...props.modelValue]
  const [item] = lista.splice(from, 1)
  lista.splice(to, 0, item)
  emitir(lista)
}

const tiposDado = [
  { value: 'text', label: 'Texto', dica: 'Resposta digitada', icon: PencilSquareIcon },
  { value: 'select', label: 'Lista', dica: 'Botões de escolha', icon: ListBulletIcon },
  {
    value: 'lookup',
    label: 'Unidades',
    dica: 'Lista do sistema',
    icon: BuildingOffice2Icon
  },
  { value: 'geo', label: 'Mapa', dica: 'Card de localização', icon: MapPinIcon },
  { value: 'image', label: 'Foto', dica: 'Anexo de imagem', icon: PhotoIcon }
]

function emitir(lista) {
  emit('update:modelValue', lista)
}

function rotuloTipo(type) {
  return tiposDado.find((t) => t.value === type)?.label || 'Texto'
}

function ehTipoEscolha(type) {
  return type === 'select' || type === 'lookup'
}

function placeholderPergunta(type) {
  const map = {
    text: 'Ex.: Qual a idade aproximada do animal?',
    select: 'Ex.: Qual o porte do animal?',
    lookup: 'Ex.: Qual secretaria está relacionada à sua manifestação?',
    geo: 'Ex.: Onde o problema está acontecendo?',
    image: 'Ex.: Pode enviar uma foto do local ou do animal?'
  }
  return map[type] || map.text
}

function textoPreview(item) {
  let base = (item.pergunta || '').trim() || placeholderPergunta(item.type).replace(/^Ex\.: /, '')
  base = base.replace(/^qual é o\s+/i, '').trim()
  if (base && !/[?.!]$/.test(base)) base = `${base}?`
  if (item.type === 'select') return base
  if (item.type === 'lookup') return base
  if (item.type === 'geo' && !/mapa|local/i.test(base)) return `${base} (com mapa abaixo)`
  if (item.type === 'image' && !/foto|imagem/i.test(base)) return `${base} (com envio de foto)`
  return base
}

function tipoCardClass(ativo) {
  return [
    'flex flex-col items-start p-3 rounded-xl border-2 text-left transition-all',
    ativo
      ? 'border-primary-500 bg-primary-50 dark:bg-primary-950/40 shadow-sm'
      : 'border-gray-200 dark:border-gray-600 bg-white dark:bg-gray-800 hover:border-primary-300'
  ]
}

function adicionarRequisito() {
  const nomes = new Set(props.modelValue.map((r) => r.name).filter(Boolean))
  const sugestao = labelParaName(`passo_${props.modelValue.length + 1}`, nomes)
  emitir([
    ...props.modelValue,
    {
      _id: `req-${++seq}-${Date.now()}`,
      name: sugestao,
      pergunta: '',
      type: 'text',
      required: true,
      ia_instrucao: '',
      ia_repescagem: '',
      optionsText: '',
      regra_elegibilidade_ativa: false,
      regra_tipo: 'interpretacao',
      regra_condicao: '',
      regra_elegibilidade_mensagem: '',
      regra_texto_valores: ''
    }
  ])
}

const MODELOS_REGRA = {
  idade:
    'Bloquear se a idade informada for menor que 12 meses ou maior que 9 anos (incluindo respostas como "8 meses", "10 anos", "filhote recém-nascido").',
  doenca:
    'Bloquear se o cidadão indicar que o animal está doente, com sintomas, em tratamento veterinário urgente, ou necessidade de atendimento clínico imediato.'
}

function aplicarModeloRegra(index, chave) {
  const texto = MODELOS_REGRA[chave]
  if (!texto) return
  patch(index, { regra_tipo: 'interpretacao', regra_condicao: texto, regra_elegibilidade_ativa: true })
}

function placeholderRegra(item) {
  if ((item.regra_tipo || 'interpretacao') === 'interpretacao') {
    return 'Mensagem exibida quando a condição acima for considerada verdadeira.'
  }
  return 'Este canal não realiza este tipo de atendimento. Orientação alternativa...'
}

function selecionarTipo(index, tipo) {
  const extra = {}
  if (tipo === 'lookup') {
    extra.datasource = LOOKUP_DATASOURCE_UNIDADES
    extra.ui_widget = 'searchable_select'
    extra.optionsText = ''
  }
  patch(index, { type: tipo, ...extra })
}

function patch(index, partial) {
  const copia = props.modelValue.map((item, i) => (i === index ? { ...item, ...partial } : item))
  emitir(copia)
}

function onNameInput(index, event) {
  const bruto = event.target.value
  const snake = bruto
    .toLowerCase()
    .normalize('NFD')
    .replace(/[\u0300-\u036f]/g, '')
    .replace(/[^a-z0-9]+/g, '_')
    .replace(/^_|_$/g, '')
  patch(index, { name: snake })
}

function onPerguntaInput(index, event) {
  const pergunta = event.target.value
  const item = props.modelValue[index]
  const partial = { pergunta }
  const nomeAtual = (item.name || '').trim()
  const nomePadrao = /^passo_\d+$|^dado_\d+$/.test(nomeAtual)
  if (!nomeAtual || nomePadrao) {
    const nomes = new Set(props.modelValue.map((r, i) => (i === index ? null : r.name)).filter(Boolean))
    partial.name = labelParaName(pergunta, nomes)
  }
  patch(index, partial)
}

function remover(index) {
  emitir(props.modelValue.filter((_, i) => i !== index))
}

function mover(index, dir) {
  const dest = index + dir
  if (dest < 0 || dest >= props.modelValue.length) return
  reordenarLista(index, dest)
}
</script>

<style scoped>
.flow-list-move,
.flow-list-enter-active,
.flow-list-leave-active {
  transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
}

.flow-list-enter-from,
.flow-list-leave-to {
  opacity: 0;
  transform: translateY(8px);
}

.flow-list-leave-active {
  position: absolute;
  width: calc(100% - 0.75rem);
}

details summary::-webkit-details-marker {
  display: none;
}
</style>