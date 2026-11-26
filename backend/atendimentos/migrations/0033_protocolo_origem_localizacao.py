from django.db import migrations, models


def _backfill_origem(apps, schema_editor):
    Protocolo = apps.get_model("atendimentos", "Protocolo")
    gps = "ocorrencia_gps"
    equip = "equipamento_publico"
    endereco = "ocorrencia_endereco"
    nenhuma = "nenhuma"
    for p in Protocolo.objects.filter(localizacao__isnull=False).iterator(chunk_size=500):
        origem = nenhuma
        if p.equipamento_id:
            origem = equip
        elif (p.endereco_texto or "").strip():
            origem = gps
        else:
            origem = gps
        Protocolo.objects.filter(pk=p.pk).update(origem_localizacao=origem)
    for p in Protocolo.objects.filter(
        localizacao__isnull=True, endereco_texto__gt=""
    ).iterator(chunk_size=500):
        Protocolo.objects.filter(pk=p.pk).update(origem_localizacao=endereco)


class Migration(migrations.Migration):

    dependencies = [
        ("atendimentos", "0032_sprint47a_agente_gestao"),
    ]

    operations = [
        migrations.AddField(
            model_name="protocolo",
            name="origem_localizacao",
            field=models.CharField(
                choices=[
                    ("nenhuma", "Sem localização da ocorrência"),
                    ("ocorrencia_gps", "GPS/endereço da ocorrência (chat/formulário)"),
                    ("ocorrencia_endereco", "Endereço textual da ocorrência"),
                    ("equipamento_publico", "Equipamento público vinculado"),
                    ("residencia_confirmada", "Residência confirmada pelo cidadão"),
                ],
                db_index=True,
                default="nenhuma",
                max_length=32,
            ),
        ),
        migrations.RunPython(_backfill_origem, migrations.RunPython.noop),
    ]