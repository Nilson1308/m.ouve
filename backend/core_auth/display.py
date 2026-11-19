"""Exibição segura de nomes de usuário (modelo Usuario customizado)."""


def nome_servidor(usuario) -> str:
    if not usuario:
        return ""
    nome = (getattr(usuario, "nome", None) or "").strip()
    if nome:
        return nome
    email = (getattr(usuario, "email", None) or "").strip()
    if email:
        return email
    return str(getattr(usuario, "pk", ""))