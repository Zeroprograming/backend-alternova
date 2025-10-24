"""
Value Objects para el dominio de notifications.
Objetos inmutables que representan conceptos del dominio de notificaciones.
"""

from dataclasses import dataclass
from typing import Optional
import re
from datetime import datetime


@dataclass(frozen=True)
class NotificationTitle:
    """Value Object para títulos de notificación."""

    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) < 1:
            raise ValueError("Notification title cannot be empty")
        if len(self.value) > 200:
            raise ValueError("Notification title must not exceed 200 characters")


@dataclass(frozen=True)
class NotificationMessage:
    """Value Object para mensajes de notificación."""

    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) < 1:
            raise ValueError("Notification message cannot be empty")
        if len(self.value) > 1000:
            raise ValueError("Notification message must not exceed 1000 characters")


@dataclass(frozen=True)
class EmailAddress:
    """Value Object para direcciones de email."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Email address cannot be empty")
        email_pattern = r"^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$"
        if not re.match(email_pattern, self.value):
            raise ValueError("Invalid email address format")


@dataclass(frozen=True)
class PhoneNumber:
    """Value Object para números de teléfono."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Phone number cannot be empty")
        # Validación básica de número de teléfono
        phone_pattern = r"^\+?[\d\s\-\(\)]{10,15}$"
        if not re.match(phone_pattern, self.value):
            raise ValueError("Invalid phone number format")


@dataclass(frozen=True)
class NotificationId:
    """Value Object para ID de notificación."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Notification ID cannot be empty")


@dataclass(frozen=True)
class TemplateId:
    """Value Object para ID de plantilla."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Template ID cannot be empty")


@dataclass(frozen=True)
class UserId:
    """Value Object para ID de usuario."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("User ID cannot be empty")


@dataclass(frozen=True)
class TemplateName:
    """Value Object para nombre de plantilla."""

    value: str

    def __post_init__(self):
        if not self.value or len(self.value.strip()) < 3:
            raise ValueError("Template name must be at least 3 characters long")
        if len(self.value) > 100:
            raise ValueError("Template name must not exceed 100 characters")
        if not re.match(r"^[a-zA-Z0-9\s\-_]+$", self.value):
            raise ValueError("Template name contains invalid characters")


@dataclass(frozen=True)
class QuietHours:
    """Value Object para horas silenciosas."""

    start_time: str
    end_time: str

    def __post_init__(self):
        if not self.start_time or not self.end_time:
            raise ValueError("Quiet hours must have both start and end times")

        # Validar formato HH:MM
        time_pattern = r"^([01]?[0-9]|2[0-3]):[0-5][0-9]$"
        if not re.match(time_pattern, self.start_time) or not re.match(
            time_pattern, self.end_time
        ):
            raise ValueError("Time must be in HH:MM format")
