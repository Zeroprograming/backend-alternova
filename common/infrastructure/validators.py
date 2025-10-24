"""
Validadores personalizados reutilizables.
"""

from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import re


def validate_phone_number(value):
    """
    Valida que el número de teléfono tenga un formato correcto.
    Acepta formatos: +57 3001234567, 3001234567, (300) 123-4567
    """
    phone_regex = r"^\+?1?\d{9,15}$"
    if not re.match(
        phone_regex,
        value.replace(" ", "").replace("(", "").replace(")", "").replace("-", ""),
    ):
        raise ValidationError("El número de teléfono debe tener entre 9 y 15 dígitos.")


def validate_file_size(value, max_size_mb=5):
    """
    Valida que el tamaño del archivo no exceda el límite.

    Args:
        value: El archivo a validar
        max_size_mb: Tamaño máximo en MB (default: 5MB)
    """
    filesize = value.size
    if filesize > max_size_mb * 1024 * 1024:
        raise ValidationError(
            f"El archivo no puede ser mayor a {max_size_mb}MB. Tu archivo pesa {filesize/(1024*1024):.2f}MB"
        )


def validate_image_extension(value):
    """
    Valida que el archivo sea una imagen con extensión permitida.
    """
    import os

    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
    if ext not in valid_extensions:
        raise ValidationError(
            f'Extensión de archivo no permitida. Use: {", ".join(valid_extensions)}'
        )


def validate_document_extension(value):
    """
    Valida que el archivo sea un documento con extensión permitida.
    """
    import os

    ext = os.path.splitext(value.name)[1].lower()
    valid_extensions = [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx"]
    if ext not in valid_extensions:
        raise ValidationError(
            f'Extensión de archivo no permitida. Use: {", ".join(valid_extensions)}'
        )


def validate_positive_number(value):
    """
    Valida que el número sea positivo.
    """
    if value < 0:
        raise ValidationError("El valor debe ser positivo.")


def validate_percentage(value):
    """
    Valida que el valor esté entre 0 y 100 (porcentaje).
    """
    if value < 0 or value > 100:
        raise ValidationError("El porcentaje debe estar entre 0 y 100.")


def validate_grade(value):
    """
    Valida que la calificación esté entre 0 y 5 (sistema colombiano).
    """
    if value < 0 or value > 5:
        raise ValidationError("La calificación debe estar entre 0.0 y 5.0.")


# Validadores de expresiones regulares comunes
alphanumeric_validator = RegexValidator(
    r"^[a-zA-Z0-9]*$", "Solo se permiten caracteres alfanuméricos."
)

code_validator = RegexValidator(
    r"^[A-Z0-9-]+$", "Solo se permiten letras mayúsculas, números y guiones."
)

slug_validator = RegexValidator(
    r"^[-a-zA-Z0-9_]+$", "Solo se permiten letras, números, guiones y guiones bajos."
)
