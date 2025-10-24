"""
Modelos base para todas las aplicaciones.
Contiene modelos abstractos que otras apps pueden heredar.
"""

from django.db import models
from django.contrib.auth import get_user_model


class TimeStampedModel(models.Model):
    """
    Modelo abstracto que proporciona campos de auditoría de tiempo.
    Todas las entidades deben heredar de este modelo.
    """

    created_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True, verbose_name="Fecha de actualización"
    )

    class Meta:
        abstract = True
        ordering = ["-created_at"]


class SoftDeleteModel(models.Model):
    """
    Modelo abstracto que proporciona soft delete.
    Los registros no se eliminan físicamente, solo se marcan como inactivos.
    """

    is_active = models.BooleanField(default=True, verbose_name="Activo")
    deleted_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Fecha de eliminación"
    )

    class Meta:
        abstract = True

    def soft_delete(self):
        """Marca el registro como eliminado"""
        from django.utils import timezone

        self.is_active = False
        self.deleted_at = timezone.now()
        self.save()

    def restore(self):
        """Restaura un registro eliminado"""
        self.is_active = True
        self.deleted_at = None
        self.save()


class AuditModel(models.Model):
    """
    Modelo abstracto que registra quién creó y modificó el registro.
    """

    created_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_created",
        verbose_name="Creado por",
    )
    updated_by = models.ForeignKey(
        get_user_model(),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="%(class)s_updated",
        verbose_name="Actualizado por",
    )

    class Meta:
        abstract = True


class BaseModel(TimeStampedModel, SoftDeleteModel, AuditModel):
    """
    Modelo base que combina timestamp, soft delete y auditoría.
    La mayoría de los modelos deben heredar de este.
    """

    class Meta:
        abstract = True
