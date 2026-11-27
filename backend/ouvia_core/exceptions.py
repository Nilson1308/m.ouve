"""Tratamento de erros alinhado ao contrato da API."""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler


def contract_exception_handler(exc, context):
    """Formata erros de validação como `{ error: { code, message, details } }`."""
    response = exception_handler(exc, context)
    if response is None:
        return response

    details = response.data
    if (
        isinstance(details, dict)
        and "code" in details
        and "detail" in details
        and set(details.keys()) <= {"code", "detail"}
    ):
        code = str(details["code"])
        message = str(details["detail"])
        details = None
    elif isinstance(details, dict) and "detail" in details:
        message = str(details["detail"])
        details = None
        code = "API_ERROR"
    elif isinstance(details, dict):
        message = "Dados inválidos"
        code = "VALIDATION_ERROR"
        if "cpf" in details:
            cpf_err = details["cpf"]
            text = cpf_err[0] if isinstance(cpf_err, list) else str(cpf_err)
            texto = text.lower()
            if "já está cadastrado" in texto or "já cadastrado" in texto:
                code = "CPF_ALREADY_REGISTERED"
                message = text
                details = {
                    **details,
                    "acao_sugerida": ["login", "recuperar_senha"],
                }
                response.status_code = status.HTTP_409_CONFLICT
            elif "inválido" in texto:
                code = "CPF_INVALID"
                message = text
    elif isinstance(details, list):
        message = details[0] if details else "Erro na requisição"
        code = "API_ERROR"
        details = None
    else:
        message = str(details)
        code = "API_ERROR"
        details = None

    response.data = {
        "error": {
            "code": code,
            "message": message,
            "details": details,
        }
    }
    if response.status_code == status.HTTP_401_UNAUTHORIZED:
        response.data["error"]["code"] = "UNAUTHORIZED"
    return response
