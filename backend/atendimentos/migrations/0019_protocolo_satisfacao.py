# Generated manually — Matriz de Qualidade (Sprint 5)

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("atendimentos", "0018_configuracao_gatilhos_notificacao"),
    ]

    operations = [
        migrations.AddField(
            model_name="protocolo",
            name="comentario_satisfacao",
            field=models.TextField(
                blank=True,
                help_text="Comentário opcional do cidadão na pesquisa de satisfação.",
                null=True,
            ),
        ),
        migrations.AddField(
            model_name="protocolo",
            name="nota_satisfacao",
            field=models.PositiveSmallIntegerField(
                blank=True,
                choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")],
                help_text="Nota da pesquisa de satisfação (1 a 5), preenchida na conclusão.",
                null=True,
            ),
        ),
        migrations.AddIndex(
            model_name="protocolo",
            index=models.Index(
                fields=["nota_satisfacao"], name="atendimento_nota_sa_idx"
            ),
        ),
    ]