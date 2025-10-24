"""Modelos para reportes."""

from django.db import models
from django.contrib.auth import get_user_model
from common.models import BaseModel

User = get_user_model()


class Report(BaseModel):
    """Modelo para reportes generados."""

    REPORT_TYPES = (
        ("grades", "Notas"),
        ("attendance", "Asistencia"),
        ("enrollments", "Inscripciones"),
        ("users", "Usuarios"),
        ("custom", "Personalizado"),
    )

    STATUS_CHOICES = (
        ("pending", "Pendiente"),
        ("processing", "Procesando"),
        ("completed", "Completado"),
        ("failed", "Fallido"),
    )

    title = models.CharField(max_length=200, verbose_name="Título")
    report_type = models.CharField(
        max_length=50, choices=REPORT_TYPES, verbose_name="Tipo"
    )
    status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default="pending", verbose_name="Estado"
    )
    filters = models.JSONField(default=dict, blank=True, verbose_name="Filtros")
    file = models.FileField(
        upload_to="reports/", null=True, blank=True, verbose_name="Archivo"
    )
    generated_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="reports_generated",
        verbose_name="Generado por",
    )
    completed_at = models.DateTimeField(
        null=True, blank=True, verbose_name="Completado el"
    )

    class Meta:
        verbose_name = "Reporte"
        verbose_name_plural = "Reportes"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.title} - {self.status}"
