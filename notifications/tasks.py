"""Tareas asíncronas para notificaciones."""

import logging

logger = logging.getLogger(__name__)


# @shared_task
def cleanup_old_notifications_task():
    """Limpia notificaciones antiguas leídas (más de 30 días)."""
    from django.utils import timezone
    from datetime import timedelta
    from .models import Notification

    cutoff_date = timezone.now() - timedelta(days=30)
    count = Notification.objects.filter(is_read=True, read_at__lt=cutoff_date).delete()[
        0
    ]

    logger.info(f"Eliminadas {count} notificaciones antiguas")
    return count
