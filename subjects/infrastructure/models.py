"""
Modelos para gestión de materias/asignaturas.
"""

from django.db import models
from django.contrib.auth import get_user_model
from common.models import BaseModel
from common.infrastructure.validators import code_validator, validate_grade
from common.infrastructure.repositories.managers import (
    SubjectManager,
    EnrollmentManager,
)

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
    is_finished = models.BooleanField(default=False, verbose_name="Materia Finalizada")
    max_students = models.PositiveIntegerField(
        default=30, verbose_name="Máximo Estudiantes"
    )

    # Manager personalizado
    objects = SubjectManager()

    class Meta:
        verbose_name = "Materia"
        verbose_name_plural = "Materias"
        ordering = ["code"]

    def __str__(self):
        return f"{self.code} - {self.name}"

    @property
    def is_approved_grade(self, grade):
        """Verifica si una nota es aprobatoria (>= 3.0)."""
        return grade >= 3.0

    def can_enroll_student(self, student):
        """Verifica si un estudiante puede inscribirse."""
        from .services import SubjectService

        return SubjectService.can_student_enroll(student, self)


class Prerequisite(BaseModel):
    """Modelo para prerrequisitos entre materias."""

    subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="prerequisites",
        verbose_name="Materia",
    )
    prerequisite_subject = models.ForeignKey(
        Subject,
        on_delete=models.CASCADE,
        related_name="required_for",
        verbose_name="Prerrequisito",
    )

    class Meta:
        verbose_name = "Prerrequisito"
        verbose_name_plural = "Prerrequisitos"
        unique_together = ["subject", "prerequisite_subject"]

    def __str__(self):
        return f"{self.subject.code} requiere {self.prerequisite_subject.code}"


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
    semester = models.PositiveIntegerField(default=1, verbose_name="Semestre")
    academic_year = models.CharField(
        max_length=9, default="2024-1", verbose_name="Año Académico"
    )

    # Manager personalizado
    objects = EnrollmentManager()

    class Meta:
        verbose_name = "Inscripción"
        verbose_name_plural = "Inscripciones"
        unique_together = ["student", "subject", "academic_year"]
        ordering = ["-enrolled_at"]

    def __str__(self):
        return f"{self.student.full_name} - {self.subject.name}"

    @property
    def is_approved(self):
        """Verifica si la materia está aprobada."""
        return self.final_grade is not None and self.final_grade >= 3.0

    @property
    def status(self):
        """Retorna el estado de la inscripción."""
        if self.final_grade is None:
            return "En curso"
        elif self.is_approved:
            return "Aprobada"
        else:
            return "Reprobada"
