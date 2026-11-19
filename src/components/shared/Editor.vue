<template>
  <div class="editor-root">
    <div
      class="flex flex-wrap items-center gap-0.5 px-2 py-2 border border-b-0 border-gray-200 dark:border-gray-600 rounded-t-lg bg-gray-50 dark:bg-gray-700/50"
      role="toolbar"
      aria-label="Formatação de texto"
    >
      <div class="flex items-center gap-0.5">
        <button
          type="button"
          class="editor-btn"
          title="Desfazer (Ctrl+Z)"
          @mousedown.prevent="aplicar('undo')"
        >
          <ArrowUturnLeftIcon class="w-4 h-4" />
        </button>
        <button
          type="button"
          class="editor-btn"
          title="Refazer (Ctrl+Y)"
          @mousedown.prevent="aplicar('redo')"
        >
          <ArrowUturnRightIcon class="w-4 h-4" />
        </button>
      </div>

      <span class="editor-sep" aria-hidden="true" />

      <div class="flex items-center gap-0.5">
        <button
          type="button"
          class="editor-btn editor-btn-text"
          title="Negrito (Ctrl+B)"
          @mousedown.prevent="aplicar('bold')"
        >
          <span class="font-bold">B</span>
        </button>
        <button
          type="button"
          class="editor-btn editor-btn-text"
          title="Itálico (Ctrl+I)"
          @mousedown.prevent="aplicar('italic')"
        >
          <span class="italic">I</span>
        </button>
        <button
          type="button"
          class="editor-btn editor-btn-text"
          title="Sublinhado (Ctrl+U)"
          @mousedown.prevent="aplicar('underline')"
        >
          <span class="underline">U</span>
        </button>
        <button
          type="button"
          class="editor-btn editor-btn-text"
          title="Tachado"
          @mousedown.prevent="aplicar('strikeThrough')"
        >
          <span class="line-through">S</span>
        </button>
      </div>

      <span class="editor-sep" aria-hidden="true" />

      <div class="flex items-center gap-0.5">
        <button
          type="button"
          class="editor-btn"
          title="Lista com marcadores"
          @mousedown.prevent="aplicar('insertUnorderedList')"
        >
          <ListBulletIcon class="w-4 h-4" />
        </button>
        <button
          type="button"
          class="editor-btn"
          title="Lista numerada"
          @mousedown.prevent="aplicar('insertOrderedList')"
        >
          <NumberedListIcon class="w-4 h-4" />
        </button>
      </div>

      <span class="editor-sep" aria-hidden="true" />

      <div class="flex items-center gap-0.5">
        <button
          type="button"
          class="editor-btn text-xs px-2 min-w-[2rem]"
          title="Parágrafo normal"
          @mousedown.prevent="formatarBloco('p')"
        >
          P
        </button>
        <button
          type="button"
          class="editor-btn text-xs font-semibold px-2 min-w-[2rem]"
          title="Subtítulo"
          @mousedown.prevent="formatarBloco('h3')"
        >
          H3
        </button>
      </div>

      <span class="editor-sep" aria-hidden="true" />

      <div class="flex items-center gap-0.5">
        <button
          type="button"
          class="editor-btn"
          title="Inserir link"
          @mousedown.prevent="inserirLink"
        >
          <LinkIcon class="w-4 h-4" />
        </button>
        <button
          type="button"
          class="editor-btn"
          title="Remover formatação"
          @mousedown.prevent="aplicar('removeFormat')"
        >
          <BackspaceIcon class="w-4 h-4" />
        </button>
      </div>
    </div>

    <div
      ref="areaRef"
      class="editor-area input rounded-t-none min-h-[140px] max-h-[320px] overflow-y-auto"
      :class="{ 'rounded-b-none': mostrarContagem }"
      :data-placeholder="placeholder"
      contenteditable="true"
      role="textbox"
      :aria-multiline="true"
      @input="onInput"
      @blur="onInput"
      @paste="onPaste"
      @keydown="onKeydown"
    />

    <div
      v-if="mostrarContagem"
      class="flex justify-end px-2 py-1 text-xs text-gray-500 dark:text-gray-400 border border-t-0 border-gray-200 dark:border-gray-600 rounded-b-lg bg-gray-50/80 dark:bg-gray-800/50"
    >
      {{ contagemCaracteres }} caracteres
    </div>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, computed } from 'vue'
import {
  ArrowUturnLeftIcon,
  ArrowUturnRightIcon,
  ListBulletIcon,
  NumberedListIcon,
  LinkIcon,
  BackspaceIcon
} from '@heroicons/vue/24/outline'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: ''
  },
  mostrarContagem: {
    type: Boolean,
    default: true
  }
})

const emit = defineEmits(['update:modelValue'])

const areaRef = ref(null)

const contagemCaracteres = computed(() => (props.modelValue || '').length)

function conteudoParaTexto(el) {
  if (!el) return ''
  return (el.innerText || '').replace(/\u00a0/g, ' ').trimEnd()
}

function onInput() {
  emit('update:modelValue', conteudoParaTexto(areaRef.value))
}

function onPaste(e) {
  e.preventDefault()
  const texto = (e.clipboardData || window.clipboardData).getData('text/plain')
  document.execCommand('insertText', false, texto)
  onInput()
}

function aplicar(cmd) {
  areaRef.value?.focus()
  document.execCommand(cmd, false, null)
  onInput()
}

function formatarBloco(tag) {
  areaRef.value?.focus()
  document.execCommand('formatBlock', false, tag)
  onInput()
}

function inserirLink() {
  const url = window.prompt('URL do link (https://…):')
  if (!url) return
  const href = url.trim()
  if (!href) return
  areaRef.value?.focus()
  document.execCommand('createLink', false, href)
  onInput()
}

function onKeydown(e) {
  if (!e.ctrlKey && !e.metaKey) return
  const map = {
    b: 'bold',
    i: 'italic',
    u: 'underline',
    z: 'undo',
    y: 'redo'
  }
  const cmd = map[e.key.toLowerCase()]
  if (!cmd) return
  e.preventDefault()
  aplicar(cmd)
}

function definirConteudo(valor) {
  const el = areaRef.value
  if (!el) return
  const atual = conteudoParaTexto(el)
  if (atual === (valor || '').trim()) return
  el.innerText = valor || ''
}

watch(
  () => props.modelValue,
  (val) => definirConteudo(val),
  { immediate: false }
)

onMounted(() => definirConteudo(props.modelValue))
</script>

<style scoped>
.editor-btn {
  @apply p-1.5 rounded text-gray-700 dark:text-gray-200 hover:bg-gray-200 dark:hover:bg-gray-600 transition-colors;
}

.editor-btn-text {
  @apply min-w-[2rem] text-sm;
}

.editor-sep {
  @apply w-px h-6 bg-gray-300 dark:bg-gray-600 mx-1 shrink-0;
}

.editor-area:empty::before {
  content: attr(data-placeholder);
  @apply text-gray-400 dark:text-gray-500 pointer-events-none;
}

.editor-area:focus {
  @apply outline-none ring-2 ring-primary-500 ring-opacity-50;
}

.editor-area :deep(ul),
.editor-area :deep(ol) {
  @apply pl-5 my-2;
}

.editor-area :deep(h3) {
  @apply text-base font-semibold my-2;
}

.editor-area :deep(a) {
  @apply text-primary-600 dark:text-primary-400 underline;
}
</style>
