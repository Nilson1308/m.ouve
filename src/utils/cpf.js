/** Mesma regra de validação do backend (core_auth.utils.cpf_valido). */

export function normalizarCpf(cpf) {
  return String(cpf || '').replace(/\D/g, '')
}

export function cpfValido(cpf) {
  const digits = normalizarCpf(cpf)
  if (digits.length !== 11 || digits === digits[0].repeat(11)) {
    return false
  }

  const calcDigit = (slice, pesoInicial) => {
    let total = 0
    for (let i = 0; i < slice.length; i += 1) {
      total += Number(slice[i]) * (pesoInicial - i)
    }
    const rest = (total * 10) % 11
    return rest === 10 ? 0 : rest
  }

  const d1 = calcDigit(digits.slice(0, 9), 10)
  const d2 = calcDigit(digits.slice(0, 10), 11)
  return digits.slice(-2) === `${d1}${d2}`
}
