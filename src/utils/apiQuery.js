/** Serializa parâmetros de query com suporte a arrays repetidos (Django). */
export function serializarQueryParams(flat) {
  const search = new URLSearchParams()
  for (const [key, val] of Object.entries(flat)) {
    if (val === undefined || val === null || val === '') continue
    if (Array.isArray(val)) {
      for (const item of val) {
        if (item !== undefined && item !== null && item !== '') {
          search.append(key, String(item))
        }
      }
    } else {
      search.append(key, String(val))
    }
  }
  return search.toString()
}