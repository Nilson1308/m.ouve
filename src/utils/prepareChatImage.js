const MAX_DIM = 2048
const JPEG_QUALITY = 0.82
const TARGET_MAX_BYTES = 4 * 1024 * 1024

function nomeJpeg(originalName) {
  const base = (originalName || 'foto').replace(/\.[^.]+$/, '')
  return `${base.slice(0, 200)}.jpg`
}

async function comprimirComCanvas(file) {
  const bitmap = await createImageBitmap(file)
  let { width, height } = bitmap
  const ratio = Math.min(1, MAX_DIM / Math.max(width, height))
  width = Math.round(width * ratio)
  height = Math.round(height * ratio)

  const canvas = document.createElement('canvas')
  canvas.width = width
  canvas.height = height
  const ctx = canvas.getContext('2d')
  if (!ctx) {
    bitmap.close?.()
    throw new Error('canvas')
  }
  ctx.drawImage(bitmap, 0, 0, width, height)
  bitmap.close?.()

  const blob = await new Promise((resolve, reject) => {
    canvas.toBlob(
      (b) => (b ? resolve(b) : reject(new Error('toBlob'))),
      'image/jpeg',
      JPEG_QUALITY
    )
  })

  return new File([blob], nomeJpeg(file.name), {
    type: 'image/jpeg',
    lastModified: Date.now()
  })
}

/**
 * Reduz fotos de câmera (mobile) antes do upload; arquivos já pequenos passam direto.
 */
export async function prepareChatImageFiles(fileList) {
  const arquivos = Array.from(fileList || [])
  const preparados = []

  for (const file of arquivos) {
    if (!file) continue

    const pareceImagem =
      (file.type && file.type.startsWith('image/')) ||
      /\.(jpe?g|png|webp|heic|heif)$/i.test(file.name || '')

    if (!pareceImagem) {
      preparados.push(file)
      continue
    }

    if (file.size <= TARGET_MAX_BYTES && /^image\/jpe?g$/i.test(file.type || '')) {
      preparados.push(file)
      continue
    }

    try {
      const comprimido = await comprimirComCanvas(file)
      preparados.push(comprimido.size < file.size ? comprimido : file)
    } catch {
      preparados.push(file)
    }
  }

  return preparados
}
