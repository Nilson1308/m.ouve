"""Constantes — modo de abertura híbrida no PWA (Sprint 4.9)."""

MODO_ABERTURA_HIBRIDO = "hibrido"
MODO_ABERTURA_CHAT_IA = "chat_ia"
MODO_ABERTURA_CATALOGO_GUIADO = "catalogo_guiado"

MODO_ABERTURA_PWA_CHOICES = (
    (MODO_ABERTURA_HIBRIDO, "Híbrido (Assistente IA + Catálogo)"),
    (MODO_ABERTURA_CHAT_IA, "Somente Assistente IA"),
    (MODO_ABERTURA_CATALOGO_GUIADO, "Catálogo Guiado"),
)

ORIGEM_ABERTURA_CHAT_IA = "chat_ia"
ORIGEM_ABERTURA_CATALOGO_GUIADO = "catalogo_guiado"

ORIGEM_ABERTURA_CHOICES = (
    (ORIGEM_ABERTURA_CHAT_IA, "Assistente IA"),
    (ORIGEM_ABERTURA_CATALOGO_GUIADO, "Catálogo Guiado"),
)

CODE_SERVICO_OBRIGATORIO_GUIADO = "servico_obrigatorio_modo_guiado"