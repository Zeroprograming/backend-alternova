"""Validadores para reportes."""

from django.core.exceptions import ValidationError


def validate_report_filters(value):
    """Valida que los filtros sean un diccionario válido."""
    if not isinstance(value, dict):
        raise ValidationError("Los filtros deben ser un diccionario.")
