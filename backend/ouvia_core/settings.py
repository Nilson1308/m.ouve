"""
Configurações do projeto M.Ouve (ouvia_core).
"""

from datetime import timedelta
from pathlib import Path

from decouple import Csv, config

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = config("SECRET_KEY", default="django-insecure-dev-only-change-in-production")
DEBUG = config("DEBUG", default=True, cast=bool)
ALLOWED_HOSTS = config("ALLOWED_HOSTS", default="localhost,127.0.0.1", cast=Csv())

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "django.contrib.gis",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "corsheaders",
    "django_filters",
    "pgvector.django",
    "core_auth",
    "catalogo",
    "atendimentos.apps.AtendimentosConfig",
    "ia_orchestrator.apps.IaOrchestratorConfig",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "ouvia_core.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "ouvia_core.wsgi.application"

_db_name = config("POSTGRES_DB", default="ouvia")
DATABASES = {
    "default": {
        "ENGINE": "ouvia_core.db.backends.postgis",
        "NAME": _db_name,
        "USER": config("POSTGRES_USER", default="ouvia"),
        "PASSWORD": config("POSTGRES_PASSWORD", default="ouvia"),
        "HOST": config("POSTGRES_HOST", default="127.0.0.1"),
        "PORT": config("POSTGRES_PORT", default="5434"),
        "TEST": {
            # Banco dedicado (criar uma vez: CREATE DATABASE ... OWNER ouvia;)
            "NAME": config("POSTGRES_TEST_DB", default=f"{_db_name}_test"),
        },
    }
}

AUTH_USER_MODEL = "core_auth.Usuario"

AUTHENTICATION_BACKENDS = [
    "core_auth.backends.CpfAuthBackend",
    "django.contrib.auth.backends.ModelBackend",
]

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "pt-br"
TIME_ZONE = "America/Sao_Paulo"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "/media/"
MEDIA_ROOT = BASE_DIR / "media"

# Fotos do celular costumam passar de 2,5 MB (limite padrão do Django).
DATA_UPLOAD_MAX_MEMORY_SIZE = config("DATA_UPLOAD_MAX_MEMORY_SIZE", default=26_214_400, cast=int)
FILE_UPLOAD_MAX_MEMORY_SIZE = config("FILE_UPLOAD_MAX_MEMORY_SIZE", default=10_485_760, cast=int)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": (
        "rest_framework_simplejwt.authentication.JWTAuthentication",
    ),
    "DEFAULT_PERMISSION_CLASSES": ("rest_framework.permissions.IsAuthenticated",),
    "DEFAULT_FILTER_BACKENDS": (
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
    ),
    "DEFAULT_PAGINATION_CLASS": "ouvia_core.pagination.ContractPagination",
    "PAGE_SIZE": 20,
    "EXCEPTION_HANDLER": "ouvia_core.exceptions.contract_exception_handler",
    "DATETIME_FORMAT": "%Y-%m-%dT%H:%M:%SZ",
    "DATETIME_INPUT_FORMATS": [
        "%Y-%m-%dT%H:%M:%SZ",
        "%Y-%m-%dT%H:%M:%S.%fZ",
        "iso-8601",
    ],
}

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(hours=12),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "AUTH_HEADER_TYPES": ("Bearer",),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": False,
}

CORS_ALLOWED_ORIGINS = config(
    "CORS_ALLOWED_ORIGINS",
    default="http://localhost:5173,http://127.0.0.1:5173",
    cast=Csv(),
)
CORS_ALLOW_CREDENTIALS = True

CSRF_TRUSTED_ORIGINS = config(
    "CSRF_TRUSTED_ORIGINS",
    default="",
    cast=Csv(),
)

if not DEBUG:
    # Proxy municipal envia X-Forwarded-Host do servidor de origem (ex.: gabinete.*);
    # com USE_X_FORWARDED_HOST o Django rejeita com 400. O Apache usa ProxyPreserveHost.
    SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")

# Em dev o Vite pode subir em outra porta (3001, 3002, …)
if DEBUG:
    CORS_ALLOWED_ORIGIN_REGEXES = [
        r"^http://localhost(:\d+)?$",
        r"^http://127\.0\.0\.1(:\d+)?$",
    ]

CELERY_BROKER_URL = config("CELERY_BROKER_URL", default="redis://127.0.0.1:6379/0")
CELERY_RESULT_BACKEND = config("CELERY_RESULT_BACKEND", default="redis://127.0.0.1:6379/0")
CELERY_ACCEPT_CONTENT = ["json"]
CELERY_TASK_SERIALIZER = "json"
CELERY_RESULT_SERIALIZER = "json"
CELERY_TIMEZONE = TIME_ZONE
CELERY_TASK_ALWAYS_EAGER = config("CELERY_TASK_ALWAYS_EAGER", default=False, cast=bool)
CELERY_TASK_EAGER_PROPAGATES = True
# Fila dedicada: evita workers de outros projetos (SIGA/eventos) consumirem tasks do M.Ouve.
CELERY_TASK_DEFAULT_QUEUE = "ouve"
CELERY_TASK_ROUTES = {
    "atendimentos.tasks.*": {"queue": "ouve"},
    "ia_orchestrator.*": {"queue": "ouve"},
}

GOVBR_AUTHORIZE_URL = config(
    "GOVBR_AUTHORIZE_URL",
    default="https://sso.staging.acesso.gov.br/authorize",
)

# Dimensão padrão de embeddings (ex.: OpenAI text-embedding-3-small)
EMBEDDING_DIMENSIONS = 1536

# LLM — chat conversacional (Fase 3; padrão Groq, compatível OpenAI SDK)
CHAT_LLM_PROVIDER = config("CHAT_LLM_PROVIDER", default="groq")
GROQ_API_KEY = config("GROQ_API_KEY", default="")
GROQ_BASE_URL = config("GROQ_BASE_URL", default="https://api.groq.com/openai/v1")
GROQ_CHAT_MODEL = config("GROQ_CHAT_MODEL", default="openai/gpt-oss-20b")
# Legado / override (OPENAI_* ainda aceito se GROQ_API_KEY vazio)
OPENAI_API_KEY = config("OPENAI_API_KEY", default="")
OPENAI_BASE_URL = config("OPENAI_BASE_URL", default="")
OPENAI_CHAT_MODEL = config("OPENAI_CHAT_MODEL", default="gpt-4o-mini")


def _resolver_llm_chat():
    """Retorna (api_key, base_url opcional, model, provider)."""
    if CHAT_LLM_PROVIDER == "groq":
        key = GROQ_API_KEY or OPENAI_API_KEY
        return key, GROQ_BASE_URL or None, GROQ_CHAT_MODEL or OPENAI_CHAT_MODEL, "groq"
    key = OPENAI_API_KEY or GROQ_API_KEY
    base = OPENAI_BASE_URL or None
    return key, base, OPENAI_CHAT_MODEL or GROQ_CHAT_MODEL, "openai"


LLM_CHAT_API_KEY, LLM_CHAT_BASE_URL, LLM_CHAT_MODEL, LLM_CHAT_PROVIDER = _resolver_llm_chat()
# Groq on_demand: OTPM ~1000 — manter max_tokens abaixo disso (resposta JSON é curta).
LLM_CHAT_MAX_TOKENS = config("LLM_CHAT_MAX_TOKENS", default=768, cast=int)
LLM_CHAT_HISTORICO_LIMITE = config("LLM_CHAT_HISTORICO_LIMITE", default=14, cast=int)

# Link do frontend para redefinição de senha (query ?token=...)
PASSWORD_RESET_FRONTEND_URL = config(
    "PASSWORD_RESET_FRONTEND_URL",
    default="http://127.0.0.1:5173/login",
)
PASSWORD_RESET_TOKEN_TTL_HOURS = config("PASSWORD_RESET_TOKEN_TTL_HOURS", default=1, cast=int)

# Web Push (VAPID) — PWA cidadão (Onda 4)
VAPID_PUBLIC_KEY = config("VAPID_PUBLIC_KEY", default="")
VAPID_PRIVATE_KEY = config("VAPID_PRIVATE_KEY", default="")
VAPID_ADMIN_EMAIL = config("VAPID_ADMIN_EMAIL", default="mailto:admin@ouve.local")
PWA_FRONTEND_BASE_URL = config("PWA_FRONTEND_BASE_URL", default="")
