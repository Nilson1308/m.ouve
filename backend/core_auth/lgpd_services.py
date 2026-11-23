"""Serviços LGPD — anonimização de conta do cidadão."""

from __future__ import annotations

import uuid

from django.contrib.auth import get_user_model
from django.db import transaction
from django.utils import timezone

from core_auth.avatar_service import remover_avatar
from core_auth.models import EnderecoCidadao

Usuario = get_user_model()


def anonimizar_usuario(usuario: Usuario) -> None:
    """Remove PII, desativa conta e invalida credenciais."""
    with transaction.atomic():
        sufixo = uuid.uuid4().hex[:12]
        usuario.nome = "Usuário Anonimizado"
        usuario.cpf = f"9{sufixo}"[:11].ljust(11, "0")
        usuario.email = f"anonimizado+{sufixo}@ouvia.invalid"
        usuario.telefone = ""
        remover_avatar(usuario)
        usuario.is_active = False
        usuario.set_unusable_password()
        usuario.save(
            update_fields=[
                "nome",
                "cpf",
                "email",
                "telefone",
                "is_active",
                "password",
            ]
        )

        try:
            endereco = usuario.endereco
        except EnderecoCidadao.DoesNotExist:
            endereco = None

        if endereco:
            endereco.cep = ""
            endereco.logradouro = ""
            endereco.numero = ""
            endereco.complemento = ""
            endereco.bairro = ""
            endereco.cidade = ""
            endereco.estado = ""
            endereco.localizacao = None
            endereco.save(
                update_fields=[
                    "cep",
                    "logradouro",
                    "numero",
                    "complemento",
                    "bairro",
                    "cidade",
                    "estado",
                    "localizacao",
                    "updated_at",
                ]
            )

        usuario._anonimizado_em = timezone.now()  # type: ignore[attr-defined]
