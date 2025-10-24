"""Signals para materias."""

from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Enrollment
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Enrollment)
def enrollment_created(sender, instance, created, **kwargs):
    """Signal cuando se crea una inscripción."""
    if created:
        logger.info(
            f"Nueva inscripción: {instance.student.username} en {instance.subject.code}"
        )
