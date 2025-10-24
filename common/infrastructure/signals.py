"""
Signals personalizados y handlers comunes.
"""

from django.db.models.signals import pre_save, post_save, pre_delete
from django.dispatch import receiver, Signal
import logging

logger = logging.getLogger(__name__)

# Definir signals personalizados
object_viewed = Signal()  # Signal cuando un objeto es visto
export_completed = Signal()  # Signal cuando una exportación termina
task_completed = Signal()  # Signal cuando una tarea se completa


@receiver(pre_save)
def audit_pre_save(sender, instance, **kwargs):
    """
    Signal que se ejecuta antes de guardar cualquier modelo.
    Útil para auditoría y validaciones de último momento.
    """
    # Solo aplicar a modelos que tengan el campo updated_by
    if hasattr(instance, "updated_by"):
        # Aquí podrías agregar lógica para auto-asignar el usuario
        # que está actualizando el registro
        pass

    if hasattr(instance, "__class__"):
        logger.debug(f"Pre-save: {instance.__class__.__name__} - {instance.pk}")


@receiver(post_save)
def audit_post_save(sender, instance, created, **kwargs):
    """
    Signal que se ejecuta después de guardar cualquier modelo.
    """
    if hasattr(instance, "__class__"):
        action = "created" if created else "updated"
        logger.info(
            f"Post-save: {instance.__class__.__name__} - {instance.pk} ({action})"
        )


@receiver(pre_delete)
def audit_pre_delete(sender, instance, **kwargs):
    """
    Signal que se ejecuta antes de eliminar un modelo.
    """
    if hasattr(instance, "__class__"):
        logger.warning(f"Pre-delete: {instance.__class__.__name__} - {instance.pk}")


# Handlers para signals personalizados
@receiver(object_viewed)
def handle_object_viewed(sender, instance, user, **kwargs):
    """
    Handler cuando un objeto es visto.
    Útil para analytics y tracking.
    """
    logger.info(f"Object viewed: {instance.__class__.__name__}:{instance.pk} by {user}")


@receiver(export_completed)
def handle_export_completed(sender, file_path, user, **kwargs):
    """
    Handler cuando se completa una exportación.
    """
    logger.info(f"Export completed: {file_path} by {user}")


@receiver(task_completed)
def handle_task_completed(sender, task_name, status, **kwargs):
    """
    Handler cuando se completa una tarea.
    """
    logger.info(f"Task completed: {task_name} with status {status}")
