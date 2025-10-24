"""
Modelos para auditoría y tracking de acciones.
"""

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType


class AuditLog(models.Model):
    """
    Registro de auditoría para todas las acciones importantes del sistema.
    """

    ACTION_TYPES = (
        ("login", "Inicio de sesión"),
        ("logout", "Cierre de sesión"),
        ("create", "Creación"),
        ("update", "Actualización"),
        ("delete", "Eliminación"),
        ("grade_assigned", "Nota asignada"),
        ("enrollment", "Inscripción"),
        ("unenrollment", "Des-inscripción"),
        ("password_change", "Cambio de contraseña"),
        ("permission_change", "Cambio de permisos"),
        ("other", "Otra acción"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="audit_logs",
        verbose_name="Usuario",
    )
    action_type = models.CharField(
        max_length=50, choices=ACTION_TYPES, verbose_name="Tipo de acción"
    )
    description = models.TextField(verbose_name="Descripción")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")

    # Información del objeto afectado (opcional)
    content_type = models.ForeignKey(
        ContentType, on_delete=models.CASCADE, null=True, blank=True
    )
    object_id = models.PositiveIntegerField(null=True, blank=True)
    content_object = GenericForeignKey("content_type", "object_id")

    # Metadata adicional
    extra_data = models.JSONField(
        default=dict, blank=True, verbose_name="Datos adicionales"
    )

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha")

    class Meta:
        verbose_name = "Registro de Auditoría"
        verbose_name_plural = "Registros de Auditoría"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["user", "action_type"]),
            models.Index(fields=["created_at"]),
        ]

    def __str__(self):
        user_str = self.user.username if self.user else "Sistema"
        return f"{user_str} - {self.get_action_type_display()} - {self.created_at}"


class UserSession(models.Model):
    """
    Gestión de sesiones de usuario con tokens JWT.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="sessions",
        verbose_name="Usuario",
    )
    access_token = models.TextField(verbose_name="Access Token")
    refresh_token = models.TextField(verbose_name="Refresh Token")
    ip_address = models.GenericIPAddressField(null=True, blank=True, verbose_name="IP")
    user_agent = models.TextField(blank=True, verbose_name="User Agent")
    is_active = models.BooleanField(default=True, verbose_name="Activa")

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Inicio de sesión"
    )
    last_activity = models.DateTimeField(auto_now=True, verbose_name="Última actividad")
    expires_at = models.DateTimeField(verbose_name="Expira el")

    class Meta:
        verbose_name = "Sesión de Usuario"
        verbose_name_plural = "Sesiones de Usuario"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.user.username} - {self.created_at}"

    def deactivate(self):
        """Desactiva la sesión (logout)."""
        self.is_active = False
        self.save()
