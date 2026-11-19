"""
pgvector: extensão `vector` deve existir antes do migrate (criada pelo DBA).

Substitui VectorExtension(), que exige superusuário na conexão da aplicação.
"""

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("core_auth", "0001_initial"),
    ]

    operations = []
