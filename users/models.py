"""
Modelos para la gestión de usuarios.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from common.models import TimeStampedModel
from common.validators import validate_phone_number
from common.managers import UserManager


class User(AbstractUser):
    """
    Modelo de usuario personalizado extendiendo AbstractUser de Django.
    """

    USER_TYPE_CHOICES = (
        ("student", "Estudiante"),
        ("teacher", "Profesor"),
        ("admin", "Administrador"),
    )

    user_type = models.CharField(
        max_length=20,
        choices=USER_TYPE_CHOICES,
        default="student",
        verbose_name="Tipo de usuario",
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[validate_phone_number],
        verbose_name="Teléfono",
    )
    avatar = models.ImageField(
        upload_to="avatars/", null=True, blank=True, verbose_name="Avatar"
    )
    bio = models.TextField(blank=True, verbose_name="Biografía")
    birth_date = models.DateField(
        null=True, blank=True, verbose_name="Fecha de nacimiento"
    )

    # Campos académicos
    max_credits_per_semester = models.PositiveIntegerField(
        default=18, verbose_name="Máximo Créditos por Semestre"
    )
    current_semester_credits = models.PositiveIntegerField(
        default=0, verbose_name="Créditos Actuales del Semestre"
    )
    academic_year = models.CharField(
        max_length=9, default="2024-1", verbose_name="Año Académico"
    )

    # Manager personalizado
    objects = UserManager()

    # Propiedades calculadas
    @property
    def is_student(self):
        return self.user_type == "student"

    @property
    def is_teacher(self):
        return self.user_type == "teacher"

    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip() or self.username

    @property
    def available_credits(self):
        """Créditos disponibles para el semestre actual."""
        return self.max_credits_per_semester - self.current_semester_credits

    def can_enroll_subject(self, subject):
        """Verifica si puede inscribirse a una materia."""
        if not self.is_student:
            return False, "Solo estudiantes pueden inscribirse"

        if (
            self.current_semester_credits + subject.credits
            > self.max_credits_per_semester
        ):
            return (
                False,
                f"No hay suficientes créditos disponibles. Necesitas {subject.credits}, tienes {self.available_credits}",
            )

        return True, "Puede inscribirse"

    def get_academic_history(self):
        """Obtiene el histórico académico del estudiante."""
        if not self.is_student:
            return []

        from subjects.models import Enrollment

        return (
            Enrollment.objects.filter(student=self, is_active=True)
            .select_related("subject")
            .order_by("-academic_year", "subject__code")
        )

    def get_cumulative_average(self):
        """Calcula el promedio acumulado del estudiante."""
        if not self.is_student:
            return 0.0

        enrollments = self.enrollments.filter(is_active=True, final_grade__isnull=False)

        if not enrollments.exists():
            return 0.0

        total_credits = sum(enrollment.subject.credits for enrollment in enrollments)
        weighted_sum = sum(
            enrollment.final_grade * enrollment.subject.credits
            for enrollment in enrollments
        )

        return round(weighted_sum / total_credits, 2) if total_credits > 0 else 0.0

    class Meta:
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        ordering = ["-date_joined"]

    def __str__(self):
        return self.full_name


class UserProfile(TimeStampedModel):
    """
    Perfil extendido del usuario con información adicional.
    """

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="profile", verbose_name="Usuario"
    )
    address = models.TextField(blank=True, verbose_name="Dirección")
    city = models.CharField(max_length=100, blank=True, verbose_name="Ciudad")
    country = models.CharField(max_length=100, default="Colombia", verbose_name="País")
    emergency_contact_name = models.CharField(
        max_length=200, blank=True, verbose_name="Contacto de emergencia"
    )
    emergency_contact_phone = models.CharField(
        max_length=20,
        blank=True,
        validators=[validate_phone_number],
        verbose_name="Teléfono de emergencia",
    )

    class Meta:
        verbose_name = "Perfil de Usuario"
        verbose_name_plural = "Perfiles de Usuario"

    def __str__(self):
        return f"Perfil de {self.user.full_name}"
