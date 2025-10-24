"""Validadores específicos para materias."""

from django.core.exceptions import ValidationError


def validate_credits(value):
    """Valida que los créditos sean válidos (1-6)."""
    if value < 1 or value > 6:
        raise ValidationError("Los créditos deben estar entre 1 y 6.")


def validate_semester(value):
    """Valida que el semestre sea válido (1-10)."""
    if value < 1 or value > 10:
        raise ValidationError("El semestre debe estar entre 1 y 10.")
