/** Tipos aceitos na galeria/anexo do chat (alinhado ao que o backend persiste em midia). */
export const CHAT_GALLERY_ACCEPT = [
  'image/*',
  'application/pdf',
  'application/msword',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.ms-excel',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'text/plain',
].join(',')

export function arquivoEhImagem(file) {
  if (!file) return false
  return (
    (file.type && file.type.startsWith('image/')) ||
    /\.(jpe?g|png|webp|heic|heif|gif|bmp)$/i.test(file.name || '')
  )
}

export function textoResumoAnexos(arquivos) {
  const total = arquivos?.length || 0
  if (!total) return '📎 Anexo enviado'

  const imgs = arquivos.filter(arquivoEhImagem).length
  const docs = total - imgs

  if (docs === 0) {
    return `📷 ${total} ${total === 1 ? 'foto enviada' : 'fotos enviadas'}`
  }
  if (imgs === 0) {
    return `📎 ${total} ${total === 1 ? 'arquivo enviado' : 'arquivos enviados'}`
  }
  return `📷📎 ${total} anexos enviados`
}

export function mensagemStatusAnexo(fase, quantidade = 1) {
  const q = Math.max(1, quantidade)
  if (fase === 'preparando') {
    return q > 1 ? `Preparando ${q} fotos…` : 'Preparando foto…'
  }
  if (fase === 'enviando') {
    return q > 1 ? `Enviando ${q} anexos…` : 'Enviando anexo…'
  }
  return ''
}
