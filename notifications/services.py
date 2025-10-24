"""Servicios para notificaciones."""

from django.db import transaction
from .models import Notification
import logging

logger = logging.getLogger(__name__)


class NotificationService:
    """Servicio para gestión de notificaciones."""

    @staticmethod
    def list_notifications(requesting_user, is_read=None):
        """
        Lista notificaciones del usuario.

        Args:
            requesting_user: Usuario que hace la petición
            is_read: Filtro opcional por leídas/no leídas

        Returns:
            QuerySet: Notificaciones filtradas
        """
        queryset = Notification.objects.filter(user=requesting_user, is_active=True)

        if is_read is not None:
            queryset = queryset.filter(is_read=is_read)

        return queryset.order_by("-created_at")

    @staticmethod
    def retrieve_notification(notification_id, requesting_user):
        """
        Obtiene una notificación con validaciones.

        Args:
            notification_id: ID de la notificación
            requesting_user: Usuario que hace la petición

        Returns:
            Notification: Notificación encontrada

        Raises:
            ValueError: Si no existe
            PermissionError: Si no tiene acceso
        """
        try:
            notification = Notification.objects.get(id=notification_id, is_active=True)

            # Solo el dueño puede ver la notificación
            if notification.user != requesting_user:
                raise PermissionError("No puedes ver notificaciones de otros usuarios")

            return notification

        except Notification.DoesNotExist:
            raise ValueError("Notificación no encontrada")

    @staticmethod
    def create_notification(user, title, message, notification_type="info"):
        """Crea una notificación para un usuario."""
        notification = Notification.objects.create(
            user=user, title=title, message=message, notification_type=notification_type
        )
        logger.info(f"Notificación creada para {user.username}: {title}")
        return notification

    @staticmethod
    @transaction.atomic
    def delete_notification(notification, requesting_user):
        """
        Elimina una notificación.

        Args:
            notification: Notificación a eliminar
            requesting_user: Usuario que elimina

        Returns:
            Notification: Notificación eliminada

        Raises:
            PermissionError: Si no tiene permisos
        """
        # Solo el dueño puede eliminar
        if notification.user != requesting_user:
            raise PermissionError("No puedes eliminar notificaciones de otros usuarios")

        notification.soft_delete()

        logger.info(
            f"Notificación {notification.id} eliminada por {requesting_user.username}"
        )

        return notification

    @staticmethod
    def mark_all_as_read(user):
        """Marca todas las notificaciones de un usuario como leídas."""
        from django.utils import timezone

        count = Notification.objects.filter(user=user, is_read=False).update(
            is_read=True, read_at=timezone.now()
        )
        logger.info(f"{count} notificaciones marcadas como leídas para {user.username}")
        return count

    @staticmethod
    def get_unread_count(user):
        """Obtiene el conteo de notificaciones no leídas."""
        return Notification.objects.filter(user=user, is_read=False).count()
