"""
Entidades del dominio para common.
Contiene las entidades principales del dominio común.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class AuditAction(Enum):
    """Acciones de auditoría."""

    CREATE = "create"
    UPDATE = "update"
    DELETE = "delete"
    READ = "read"
    LOGIN = "login"
    LOGOUT = "logout"


class QueryType(Enum):
    """Tipos de consulta ORM."""

    SELECT = "select"
    INSERT = "insert"
    UPDATE = "update"
    DELETE = "delete"
    RAW = "raw"


@dataclass
class AuditLog:
    """Entidad AuditLog - Log de auditoría."""

    id: str
    user_id: str
    action: AuditAction
    model_name: str
    object_id: str
    changes: Optional[Dict[str, Any]] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    timestamp: datetime = None

    def add_change(self, field: str, old_value: Any, new_value: Any) -> None:
        """Agrega un cambio al log."""
        if self.changes is None:
            self.changes = {}
        self.changes[field] = {"old": old_value, "new": new_value}


@dataclass
class QueryMetrics:
    """Entidad QueryMetrics - Métricas de consulta."""

    id: str
    query_type: QueryType
    model_name: str
    execution_time: float
    query_count: int
    cache_hits: int = 0
    cache_misses: int = 0
    timestamp: datetime = None

    def calculate_efficiency(self) -> float:
        """Calcula la eficiencia de la consulta."""
        total_queries = self.query_count + self.cache_hits + self.cache_misses
        if total_queries == 0:
            return 0.0
        return (self.cache_hits / total_queries) * 100


@dataclass
class CacheEntry:
    """Entidad CacheEntry - Entrada de caché."""

    key: str
    value: Any
    expires_at: datetime
    created_at: datetime = None
    access_count: int = 0

    def is_expired(self) -> bool:
        """Verifica si la entrada ha expirado."""
        return datetime.now() > self.expires_at

    def increment_access(self) -> None:
        """Incrementa el contador de accesos."""
        self.access_count += 1


@dataclass
class MiddlewareContext:
    """Entidad MiddlewareContext - Contexto de middleware."""

    request_id: str
    user_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    start_time: datetime = None
    end_time: Optional[datetime] = None

    def calculate_duration(self) -> float:
        """Calcula la duración de la request."""
        if self.start_time and self.end_time:
            return (self.end_time - self.start_time).total_seconds()
        return 0.0
