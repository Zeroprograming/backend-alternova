"""
Configuración de Celery para el proyecto Alternova.
"""

import os
from celery import Celery
from django.conf import settings

# Configurar Django settings para Celery
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("alternova")

# Usar configuración de Django
app.config_from_object("django.conf:settings", namespace="CELERY")

# Auto-descubrir tareas en todas las apps
app.autodiscover_tasks()

# Configuración adicional
app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_time_limit=30 * 60,  # 30 minutos
    task_soft_time_limit=25 * 60,  # 25 minutos
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=1000,
)


@app.task(bind=True)
def debug_task(self):
    """Tarea de debug para probar Celery."""
    print(f"Request: {self.request!r}")
    return "Celery está funcionando correctamente"
