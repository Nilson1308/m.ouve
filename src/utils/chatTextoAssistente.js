/** Formata negrito **texto** e quebras de linha em mensagens da IA (somente tags permitidas). */

const BOLD_RE = /\*\*([^*]+)\*\*/g

export function formatarConteudoAssistente(texto) {
  const bruto = (texto || '').trim()
  if (!bruto) return ''

  const partes = bruto.split(BOLD_RE)
  const html = partes
    .map((pedaco, i) => {
      const esc = pedaco
        .replace(/&/g, '&amp;')
        .replace(/</g, '&lt;')
        .replace(/>/g, '&gt;')
        .replace(/"/g, '&quot;')
      if (i % 2 === 1) {
        return `<strong class="font-semibold">${esc}</strong>`
      }
      return esc.replace(/\n/g, '<br>')
    })
    .join('')

  return html
}