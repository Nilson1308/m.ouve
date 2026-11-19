"""Utilitários de autenticação e formatação."""

import re


def normalizar_cpf(cpf: str) -> str:
    """Remove máscara e retorna apenas dígitos."""
    return re.sub(r"\D", "", cpf or "")


def formatar_cpf(cpf: str) -> str:
    """Formata CPF como 000.000.000-00."""
    digits = normalizar_cpf(cpf)
    if len(digits) != 11:
        return cpf
    return f"{digits[:3]}.{digits[3:6]}.{digits[6:9]}-{digits[9:]}"


def cpf_valido(cpf: str) -> bool:
    """Validação básica de CPF (dígitos verificadores)."""
    digits = normalizar_cpf(cpf)
    if len(digits) != 11 or digits == digits[0] * 11:
        return False

    def calc_digit(slice_cpf, peso_inicial):
        total = sum(int(d) * p for d, p in zip(slice_cpf, range(peso_inicial, 1, -1)))
        rest = (total * 10) % 11
        return 0 if rest == 10 else rest

    d1 = calc_digit(digits[:9], 10)
    d2 = calc_digit(digits[:10], 11)
    return digits[-2:] == f"{d1}{d2}"
