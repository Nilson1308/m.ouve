<template>
  <div class="copiloto-texto space-y-2 text-sm leading-relaxed text-slate-800 dark:text-slate-100">
    <template v-for="(bloco, idx) in blocos" :key="idx">
      <ul
        v-if="bloco.tipo === 'lista'"
        class="list-disc pl-5 space-y-1 marker:text-primary-600 dark:marker:text-primary-400"
      >
        <li v-for="(item, j) in bloco.itens" :key="j">
          <CopilotoInline :partes="parseInline(item)" />
        </li>
      </ul>
      <p v-else class="whitespace-pre-wrap">
        <CopilotoInline :partes="parseInline(bloco.texto)" />
      </p>
    </template>
  </div>
</template>

<script setup>
import { computed, defineComponent, h } from 'vue'

const props = defineProps({
  texto: { type: String, default: '' }
})

const CopilotoInline = defineComponent({
  name: 'CopilotoInline',
  props: { partes: { type: Array, required: true } },
  setup(p) {
    return () =>
      p.partes.map((part, i) =>
        part.negrito
          ? h(
              'strong',
              {
                key: i,
                class: 'font-semibold text-slate-900 dark:text-white'
              },
              part.text
            )
          : h('span', { key: i }, part.text)
      )
  }
})

function parseInline(line) {
  const out = []
  const re = /\*\*(.+?)\*\*/g
  let last = 0
  let m
  const s = line || ''
  while ((m = re.exec(s)) !== null) {
    if (m.index > last) {
      out.push({ text: s.slice(last, m.index), negrito: false })
    }
    out.push({ text: m[1], negrito: true })
    last = m.index + m[0].length
  }
  if (last < s.length) {
    out.push({ text: s.slice(last), negrito: false })
  }
  if (!out.length) out.push({ text: s, negrito: false })
  return out
}

const blocos = computed(() => {
  const lines = (props.texto || '').split(/\n/)
  const result = []
  let buffer = []

  function flushList() {
    if (buffer.length) {
      result.push({ tipo: 'lista', itens: [...buffer] })
      buffer = []
    }
  }

  for (const raw of lines) {
    const line = raw.trimEnd()
    if (!line.trim()) {
      flushList()
      continue
    }
    const bullet = line.match(/^[-•*]\s+(.*)$/)
    if (bullet) {
      buffer.push(bullet[1])
    } else {
      flushList()
      result.push({ tipo: 'paragrafo', texto: line })
    }
  }
  flushList()
  return result
})
</script>