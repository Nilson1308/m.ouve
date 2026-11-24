"""Sprint 2.5 — dois fluxos, executor_padrao, exigir_validacao_ouvidoria; migra híbrido."""

from django.db import migrations, models
import django.db.models.deletion


def migrar_fluxos_hibrido(apps, schema_editor):
    ServicoCatalogo = apps.get_model("catalogo", "ServicoCatalogo")
    for servico in ServicoCatalogo.objects.filter(fluxo_tramitacao="hibrido"):
        servico.fluxo_tramitacao = "ouvidoria_encaminha"
        servico.exigir_validacao_ouvidoria = True
        servico.save(update_fields=["fluxo_tramitacao", "exigir_validacao_ouvidoria"])

    ServicoCatalogo.objects.filter(fluxo_tramitacao="direto_secretaria").update(
        exigir_validacao_ouvidoria=False
    )
    ServicoCatalogo.objects.filter(fluxo_tramitacao="ouvidoria_encaminha").update(
        exigir_validacao_ouvidoria=True
    )


class Migration(migrations.Migration):

    dependencies = [
        ("catalogo", "0013_equipamentos_publicos"),
    ]

    operations = [
        migrations.AddField(
            model_name="servicocatalogo",
            name="exigir_validacao_ouvidoria",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Na saída: se True, o protocolo só encerra ao cidadão após homologação da "
                    "Ouvidoria. Em ouvidoria_encaminha é sempre True. Em direto_secretaria "
                    "pode ser False para encerramento direto pelo executor."
                ),
            ),
        ),
        migrations.AddField(
            model_name="servicocatalogo",
            name="executor_padrao",
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    "Unidade executora sugerida na triagem (fluxo ouvidoria_encaminha). "
                    "Não usar em direto_secretaria."
                ),
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="servicos_como_executor_padrao",
                to="catalogo.unidadeadministrativa",
            ),
        ),
        migrations.RunPython(migrar_fluxos_hibrido, migrations.RunPython.noop),
        migrations.AlterField(
            model_name="servicocatalogo",
            name="fluxo_tramitacao",
            field=models.CharField(
                choices=[
                    ("direto_secretaria", "Direto à secretaria"),
                    ("ouvidoria_encaminha", "Ouvidoria encaminha"),
                ],
                db_index=True,
                default="direto_secretaria",
                help_text=(
                    "Define como o protocolo é titulado e encaminhado. "
                    "Em ouvidoria_encaminha, unidade_responsavel é a unidade do canal."
                ),
                max_length=32,
            ),
        ),
        migrations.AlterField(
            model_name="servicocatalogo",
            name="triagem_ia_ativa",
            field=models.BooleanField(
                default=True,
                help_text=(
                    "Quando ativo, enfileira triagem semântica (LLM) após a triagem "
                    "determinística em fluxos ouvidoria_encaminha."
                ),
            ),
        ),
        migrations.AlterField(
            model_name="servicocatalogo",
            name="unidade_responsavel",
            field=models.ForeignKey(
                blank=True,
                help_text=(
                    "direto_secretaria: secretaria executora (recebe OS automática); "
                    "ouvidoria_encaminha: unidade do canal (Ouvidoria)."
                ),
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="servicos_catalogo",
                to="catalogo.unidadeadministrativa",
            ),
        ),
    ]