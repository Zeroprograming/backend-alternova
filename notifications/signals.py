"""Signals para notificaciones."""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Notification
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Notification)
def notification_created(sender, instance, created, **kwargs):
    """Signal cuando se crea una notificación."""
    if created:
        logger.info(
            f"Nueva notificación para {instance.user.username}: {instance.title}"
        )
