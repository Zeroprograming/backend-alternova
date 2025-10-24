"""
Value Objects para el dominio de common.
Objetos inmutables que representan conceptos del dominio común.
"""

from dataclasses import dataclass
from typing import Optional
import re
from datetime import datetime


@dataclass(frozen=True)
class RequestId:
    """Value Object para ID de request."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Request ID cannot be empty")
        if len(self.value) < 8:
            raise ValueError("Request ID must be at least 8 characters long")


@dataclass(frozen=True)
class ModelName:
    """Value Object para nombre de modelo."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Model name cannot be empty")
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", self.value):
            raise ValueError(
                "Model name must start with letter and contain only letters, numbers, and underscores"
            )


@dataclass(frozen=True)
class ObjectId:
    """Value Object para ID de objeto."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Object ID cannot be empty")


@dataclass(frozen=True)
class CacheKey:
    """Value Object para clave de caché."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Cache key cannot be empty")
        if len(self.value) > 250:
            raise ValueError("Cache key must not exceed 250 characters")


@dataclass(frozen=True)
class IPAddress:
    """Value Object para dirección IP."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("IP address cannot be empty")
        # Validación básica de IP
        ip_pattern = r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$"
        if not re.match(ip_pattern, self.value):
            raise ValueError("Invalid IP address format")


@dataclass(frozen=True)
class ExecutionTime:
    """Value Object para tiempo de ejecución."""

    value: float

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Execution time cannot be negative")
        if self.value > 3600:  # 1 hora
            raise ValueError("Execution time seems too high (over 1 hour)")


@dataclass(frozen=True)
class QueryCount:
    """Value Object para conteo de consultas."""

    value: int

    def __post_init__(self):
        if self.value < 0:
            raise ValueError("Query count cannot be negative")
        if self.value > 10000:
            raise ValueError("Query count seems too high (over 10,000)")


@dataclass(frozen=True)
class UserAgent:
    """Value Object para User Agent."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("User agent cannot be empty")
        if len(self.value) > 500:
            raise ValueError("User agent must not exceed 500 characters")


@dataclass(frozen=True)
class FieldName:
    """Value Object para nombre de campo."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Field name cannot be empty")
        if not re.match(r"^[a-zA-Z][a-zA-Z0-9_]*$", self.value):
            raise ValueError(
                "Field name must start with letter and contain only letters, numbers, and underscores"
            )
