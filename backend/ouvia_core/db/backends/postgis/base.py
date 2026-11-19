"""
Backend PostGIS que não executa CREATE EXTENSION (exige superusuário).

Em produção/homolog as extensões `postgis` e `vector` são provisionadas
pelo DBA no servidor 192.168.10.49 antes do `manage.py migrate`.
"""

from django.contrib.gis.db.backends.postgis.base import (
    DatabaseWrapper as PostGISDatabaseWrapper,
)
from django.core.exceptions import ImproperlyConfigured

_REQUIRED_EXTENSIONS = ("postgis", "vector")


class DatabaseWrapper(PostGISDatabaseWrapper):
    """Valida extensões GIS já instaladas; não tenta criá-las."""

    def prepare_database(self):
        with self.cursor() as cursor:
            cursor.execute(
                "SELECT extname FROM pg_extension WHERE extname = ANY(%s)",
                [list(_REQUIRED_EXTENSIONS)],
            )
            found = {row[0] for row in cursor.fetchall()}

        missing = set(_REQUIRED_EXTENSIONS) - found
        if missing:
            raise ImproperlyConfigured(
                "Extensão(ões) ausente(s) no banco da aplicação "
                f"({self.settings_dict['NAME']}): {', '.join(sorted(missing))}. "
                "Extensões são por banco — não basta instalá-las em `postgres`. "
                "Como superusuário: \\c ouvia → CREATE EXTENSION postgis; "
                "CREATE EXTENSION vector;"
            )
