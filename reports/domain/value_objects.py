"""
Value Objects para el dominio de reports.
Objetos inmutables que representan conceptos del dominio de reportes.
"""

from dataclasses import dataclass
from typing import Optional
import re
from datetime import datetime


@dataclass(frozen=True)
class ReportName:
    """Value Object para nombres de reporte."""

    value: str

    def __post_init__(self):
        if not self.value or len(self.value) < 3:
            raise ValueError("Report name must be at least 3 characters long")
        if len(self.value) > 100:
            raise ValueError("Report name must not exceed 100 characters")
        if not re.match(r"^[a-zA-Z0-9\s\-_]+$", self.value):
            raise ValueError("Report name contains invalid characters")


@dataclass(frozen=True)
class FilePath:
    """Value Object para rutas de archivo."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("File path cannot be empty")
        if not self.value.startswith("/") and not self.value.startswith("C:"):
            raise ValueError("File path must be absolute")


@dataclass(frozen=True)
class CronExpression:
    """Value Object para expresiones cron."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Cron expression cannot be empty")
        # Validación básica de formato cron
        parts = self.value.split()
        if len(parts) != 5:
            raise ValueError("Cron expression must have 5 parts")


@dataclass(frozen=True)
class ReportId:
    """Value Object para ID de reporte."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Report ID cannot be empty")


@dataclass(frozen=True)
class TemplateId:
    """Value Object para ID de plantilla."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Template ID cannot be empty")


@dataclass(frozen=True)
class ScheduleId:
    """Value Object para ID de programación."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Schedule ID cannot be empty")


@dataclass(frozen=True)
class UserId:
    """Value Object para ID de usuario."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("User ID cannot be empty")


@dataclass(frozen=True)
class QueryTemplate:
    """Value Object para plantilla de consulta."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Query template cannot be empty")
        if len(self.value) < 10:
            raise ValueError("Query template must be at least 10 characters long")
