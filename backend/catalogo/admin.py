from django.contrib import admin

from catalogo.models import (
    CategoriaCatalogo,
    EquipamentoPublico,
    MatrizRoteamentoTematico,
    ServicoCatalogo,
    ServicoCatalogoVersao,
    UnidadeAdministrativa,
)


class MatrizRoteamentoTematicoInline(admin.TabularInline):
    model = MatrizRoteamentoTematico
    extra = 0
    autocomplete_fields = ("unidade_sugerida",)


@admin.register(EquipamentoPublico)
class EquipamentoPublicoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "tipo",
        "unidade_responsavel",
        "bairro",
        "ativo",
        "atualizado_em",
    )
    list_filter = ("ativo", "tipo", "unidade_responsavel")
    search_fields = ("nome", "bairro", "endereco")
    autocomplete_fields = ("unidade_responsavel",)
    ordering = ("nome",)


@admin.register(UnidadeAdministrativa)
class UnidadeAdministrativaAdmin(admin.ModelAdmin):
    list_display = ("nome", "sigla", "tom_ia", "ativo", "atualizado_em")
    list_filter = ("ativo", "tom_ia")
    search_fields = ("nome", "sigla")
    ordering = ("nome",)


@admin.register(CategoriaCatalogo)
class CategoriaCatalogoAdmin(admin.ModelAdmin):
    list_display = ("nome", "slug", "ordem", "tipo_legado", "ativo")
    list_filter = ("ativo", "tipo_legado")
    search_fields = ("nome", "slug")
    prepopulated_fields = {"slug": ("nome",)}
    ordering = ("ordem", "nome")


@admin.register(ServicoCatalogo)
class ServicoCatalogoAdmin(admin.ModelAdmin):
    list_display = (
        "nome",
        "categoria",
        "fluxo_tramitacao",
        "unidade_responsavel",
        "sla_horas",
        "is_template",
        "visivel_catalogo_pwa",
        "ordem_exibicao_pwa",
        "ativo",
    )
    inlines = (MatrizRoteamentoTematicoInline,)
    autocomplete_fields = ("categoria", "unidade_responsavel")
    list_filter = ("ativo", "visivel_catalogo_pwa", "is_template", "categoria")
    search_fields = ("nome",)
    readonly_fields = ("id", "criado_em", "atualizado_em")
    fieldsets = (
        (
            None,
            {
                "fields": (
                    "categoria",
                    "nome",
                    "descricao",
                    "icone",
                    "sla_horas",
                    "fluxo_tramitacao",
                    "unidade_responsavel",
                    "visivel_catalogo_pwa",
                    "ordem_exibicao_pwa",
                    "is_template",
                    "ativo",
                )
            },
        ),
        ("Form Builder (app cidadão)", {"fields": ("formulario_schema",)}),
        (
            "JSON Schema legado",
            {
                "fields": ("schema_formulario",),
                "description": (
                    "JSON Schema dos campos em dados_dinamicos. "
                    "Use $metadata.exige_localizacao para exigir GPS no protocolo."
                ),
            },
        ),
        (
            "Versionamento",
            {
                "fields": (
                    "versao_publicada",
                    "publicado_em",
                    "formulario_schema_rascunho",
                    "schema_formulario_rascunho",
                ),
            },
        ),
        ("Auditoria", {"fields": ("id", "criado_em", "atualizado_em")}),
    )


@admin.register(ServicoCatalogoVersao)
class ServicoCatalogoVersaoAdmin(admin.ModelAdmin):
    list_display = ("servico", "numero_versao", "nota_versao", "publicado_por", "publicado_em")
    list_filter = ("publicado_em",)
    search_fields = ("servico__nome", "nota_versao")
    readonly_fields = (
        "servico",
        "numero_versao",
        "formulario_schema",
        "schema_formulario",
        "nota_versao",
        "publicado_por",
        "publicado_em",
    )


@admin.register(MatrizRoteamentoTematico)
class MatrizRoteamentoTematicoAdmin(admin.ModelAdmin):
    list_display = (
        "servico",
        "chave_schema",
        "valor_condicao",
        "unidade_sugerida",
        "ativo",
    )
    list_filter = ("ativo", "chave_schema")
    search_fields = ("servico__nome", "chave_schema", "valor_condicao")
    autocomplete_fields = ("servico", "unidade_sugerida")
