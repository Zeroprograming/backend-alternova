"""Signals para reportes."""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Report
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Report)
def report_status_changed(sender, instance, **kwargs):
    """Signal cuando cambia el estado de un reporte."""
    if instance.status == "completed":
        logger.info(f"Reporte completado: {instance.title}")
        # Aquí podrías enviar una notificación al usuario
