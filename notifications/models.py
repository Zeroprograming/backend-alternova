"""Modelos para notificaciones."""

from django.db import models
from django.contrib.auth import get_user_model
from common.models import BaseModel

User = get_user_model()


class Notification(BaseModel):
    """Modelo para notificaciones a usuarios."""

    NOTIFICATION_TYPES = (
        ("info", "Información"),
        ("warning", "Advertencia"),
        ("success", "Éxito"),
        ("error", "Error"),
    )

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="notifications",
        verbose_name="Usuario",
    )
    title = models.CharField(max_length=200, verbose_name="Título")
    message = models.TextField(verbose_name="Mensaje")
    notification_type = models.CharField(
        max_length=20, choices=NOTIFICATION_TYPES, default="info", verbose_name="Tipo"
    )
    is_read = models.BooleanField(default=False, verbose_name="Leída")
    read_at = models.DateTimeField(null=True, blank=True, verbose_name="Leída el")

    class Meta:
        verbose_name = "Notificación"
        verbose_name_plural = "Notificaciones"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.user.username}"

    def mark_as_read(self):
        """Marca la notificación como leída."""
        from django.utils import timezone

        self.is_read = True
        self.read_at = timezone.now()
        self.save()
