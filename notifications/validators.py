"""Validadores para notificaciones."""

from django.core.exceptions import ValidationError


def validate_notification_type(value):
    """Valida que el tipo de notificación sea válido."""
    valid_types = ["info", "warning", "success", "error"]
    if value not in valid_types:
        raise ValidationError(f'Tipo inválido. Use: {", ".join(valid_types)}')
