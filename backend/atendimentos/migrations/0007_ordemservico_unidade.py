import uuid

from django.db import migrations, models
import django.db.models.deletion


def migrar_secretaria_para_unidade(apps, schema_editor):
    OrdemServico = apps.get_model("atendimentos", "OrdemServico")
    Unidade = apps.get_model("catalogo", "UnidadeAdministrativa")
    fallback, _ = Unidade.objects.get_or_create(
        sigla="GEN",
        defaults={"id": uuid.uuid4(), "nome": "Unidade Geral", "ativa": True},
    )
    for ordem in OrdemServico.objects.all():
        nome = (getattr(ordem, "secretaria", None) or "").strip()
        if nome:
            unidade, _ = Unidade.objects.get_or_create(
                nome=nome,
                defaults={"id": uuid.uuid4(), "sigla": "", "ativa": True},
            )
        else:
            unidade = fallback
        ordem.unidade_id = unidade.id
        ordem.save(update_fields=["unidade_id"])


class Migration(migrations.Migration):

    dependencies = [
        ("catalogo", "0004_unidadeadministrativa"),
        ("atendimentos", "0006_mensagemchat_payload_ui"),
    ]

    operations = [
        migrations.AddField(
            model_name="ordemservico",
            name="prazo_horas",
            field=models.PositiveIntegerField(
                blank=True,
                help_text="Prazo operacional da ordem em horas (scatter-gather).",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="ordemservico",
            name="unidade",
            field=models.ForeignKey(
                blank=True,
                null=True,
                on_delete=django.db.models.deletion.PROTECT,
                related_name="ordens_servico",
                to="catalogo.unidadeadministrativa",
            ),
        ),
        migrations.RunPython(migrar_secretaria_para_unidade, migrations.RunPython.noop),
        migrations.RemoveField(
            model_name="ordemservico",
            name="secretaria",
        ),
        migrations.AlterField(
            model_name="ordemservico",
            name="unidade",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.PROTECT,
                related_name="ordens_servico",
                to="catalogo.unidadeadministrativa",
            ),
        ),
    ]
