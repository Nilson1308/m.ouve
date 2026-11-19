"""Backend de autenticação por CPF."""

from django.contrib.auth.backends import ModelBackend

from core_auth.models import Usuario
from core_auth.utils import normalizar_cpf


class CpfAuthBackend(ModelBackend):
    """Aceita `cpf=` (API) ou `username=` (Django Admin) com ou sem máscara."""

    def authenticate(self, request, cpf=None, password=None, **kwargs):
        cpf = cpf or kwargs.get(Usuario.USERNAME_FIELD) or kwargs.get("username")
        if not cpf:
            return None
        cpf_norm = normalizar_cpf(cpf)
        if not cpf_norm:
            return None
        try:
            user = Usuario.objects.get(cpf=cpf_norm)
        except Usuario.DoesNotExist:
            return None
        if user.check_password(password) and self.user_can_authenticate(user):
            return user
        return None
