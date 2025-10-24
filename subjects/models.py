"""
Modelos para gestión de materias/asignaturas.
"""

from django.db import models
from django.contrib.auth import get_user_model
from common.models import BaseModel
from common.validators import code_validator, validate_grade

User = get_user_model()


class Subject(BaseModel):
    """Modelo para materias/asignaturas."""

    code = models.CharField(
        max_length=20, unique=True, validators=[code_validator], verbose_name="Código"
    )
    name = models.CharField(max_length=200, verbose_name="Nombre")
    description = models.TextField(blank=True, verbose_name="Descripción")
    credits = models.PositiveIntegerField(default=3, verbose_name="Créditos")
    teacher = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name="subjects_teaching",
        limit_choices_to={"user_type": "teacher"},
        verbose_name="Profesor",
    )
    semester = models.PositiveIntegerField(default=1, verbose_name="Semestre")

    class Meta:
        verbose_name = "Materia"
        verbose_name_plural = "Materias"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"


class Enrollment(BaseModel):
    """Modelo para inscripción de estudiantes en materias."""

    student = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="enrollments",
        limit_choices_to={"user_type": "student"},
        verbose_name="Estudiante",
    )
    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="enrollments",
        verbose_name="Materia",
    )
    enrolled_at = models.DateTimeField(
        auto_now_add=True, verbose_name="Fecha de inscripción"
    )
    final_grade = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[validate_grade],
        verbose_name="Nota final",
    )

    class Meta:
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"
        unique_together = ["student", "subject"]
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.student.full_name} - {self.subject.name}"
