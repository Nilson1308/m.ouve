from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ("atendimentos", "0020_sessaochat_motivo_inelegibilidade"),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name="avaliacaoprotocolo",
            name="uq_avaliacao_protocolo_usuario",
        ),
        migrations.RemoveField(
            model_name="avaliacaoprotocolo",
            name="usuario",
        ),
        migrations.RenameField(
            model_name="avaliacaoprotocolo",
            old_name="criado_em",
            new_name="criada_em",
        ),
        migrations.AlterField(
            model_name="avaliacaoprotocolo",
            name="comentario",
            field=models.TextField(blank=True, max_length=500),
        ),
        migrations.AlterField(
            model_name="avaliacaoprotocolo",
            name="nota",
            field=models.PositiveSmallIntegerField(
                choices=[(1, "1"), (2, "2"), (3, "3"), (4, "4"), (5, "5")]
            ),
        ),
        migrations.AlterField(
            model_name="avaliacaoprotocolo",
            name="protocolo",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="avaliacao",
                to="atendimentos.protocolo",
            ),
        ),
    ]