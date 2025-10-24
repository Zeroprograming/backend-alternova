"""
Validadores específicos para usuarios.
"""

from django.core.exceptions import ValidationError
from django.contrib.auth.password_validation import validate_password
import re


def validate_username_format(value):
    """
    Valida que el username tenga un formato válido.
    Solo letras, números, guiones y guiones bajos.
    """
    if not re.match(r"^[a-zA-Z0-9_-]+$", value):
        raise ValidationError(
            "El nombre de usuario solo puede contener letras, números, guiones y guiones bajos."
        )


def validate_age(birth_date):
    """
    Valida que el usuario tenga al menos 13 años.
    """
    from datetime import date

    today = date.today()
    age = (
        today.year
        - birth_date.year
        - ((today.month, today.day) < (birth_date.month, birth_date.day))
    )

    if age < 13:
        raise ValidationError("Debes tener al menos 13 años para registrarte.")


def validate_strong_password(password):
    """
    Valida que la contraseña sea fuerte.
    """
    # Usar el validador de Django
    validate_password(password)

    # Validaciones adicionales
    if len(password) < 8:
        raise ValidationError("La contraseña debe tener al menos 8 caracteres.")

    if not any(char.isdigit() for char in password):
        raise ValidationError("La contraseña debe contener al menos un número.")

    if not any(char.isupper() for char in password):
        raise ValidationError(
            "La contraseña debe contener al menos una letra mayúscula."
        )
