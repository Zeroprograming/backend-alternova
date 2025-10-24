"""
Modelos para la gestión de usuarios.
"""

from django.contrib.auth.models import AbstractUser
from django.db import models
from common.models import TimeStampedModel
from common.validators import validate_phone_number


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
