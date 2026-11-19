"""Configuração do Celery para tarefas assíncronas do M.Ouve."""

import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "ouvia_core.settings")

app = Celery("ouvia_core")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()
