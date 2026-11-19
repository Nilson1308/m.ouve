# Catálogo — Form Builder e unidade responsável

import uuid

from django.db import migrations, models
import django.db.models.deletion


def _schema_exemplo():
    return [
        {
            "name": "foto_local",
            "type": "image",
            "label": "Foto do Local",
            "required": True,
        },
        {
            "name": "ponto_referencia",
            "type": "text",
            "label": "Ponto de Referência",
            "required": False,
        },
    ]


class Migration(migrations.Migration):

    dependencies = [
        ("catalogo", "0005_unidade_descricao_ativo"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicocatalogo",
            name="icone",
            field=models.CharField(
                blank=True,
                help_text="Nome lógico do ícone ou URL para o app do cidadão.",
                max_length=120,
            ),
        ),
        migrations.AddField(
            model_name="servicocatalogo",
            name="unidade_responsavel",
            field=models.ForeignKey(
                blank=True,
                help_text="Secretaria/unidade padrão de encaminhamento ao abrir protocolo.",
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="servicos_catalogo",
                to="catalogo.unidadeadministrativa",
            ),
        ),
        migrations.AddField(
            model_name="servicocatalogo",
            name="formulario_schema",
            field=models.JSONField(
                blank=True,
                default=list,
                help_text="Lista de campos do Form Builder (app cidadão).",
            ),
        ),
        migrations.AlterField(
            model_name="servicocatalogo",
            name="schema_formulario",
            field=models.JSONField(
                default=dict,
                help_text="JSON Schema legado (chat/validação). Mantido por compatibilidade.",
            ),
        ),
    ]