"""
Entidades del dominio para reports.
Contiene las entidades principales del dominio de reportes.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ReportType(Enum):
    """Tipo de reporte."""

    CSV = "csv"
    PDF = "pdf"
    EXCEL = "excel"
    JSON = "json"


class ReportStatus(Enum):
    """Estado de un reporte."""

    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"


@dataclass
class Report:
    """Entidad Report - Reporte."""

    id: str
    name: str
    report_type: ReportType
    status: ReportStatus = ReportStatus.PENDING
    parameters: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    created_by: str = ""
    created_at: datetime = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    def start_processing(self) -> None:
        """Inicia el procesamiento del reporte."""
        self.status = ReportStatus.PROCESSING
        self.created_at = datetime.now()

    def complete(self, file_path: str) -> None:
        """Completa el reporte exitosamente."""
        self.status = ReportStatus.COMPLETED
        self.file_path = file_path
        self.completed_at = datetime.now()

    def fail(self, error_message: str) -> None:
        """Marca el reporte como fallido."""
        self.status = ReportStatus.FAILED
        self.error_message = error_message
        self.completed_at = datetime.now()

    def is_completed(self) -> bool:
        """Verifica si el reporte está completado."""
        return self.status == ReportStatus.COMPLETED

    def is_failed(self) -> bool:
        """Verifica si el reporte falló."""
        return self.status == ReportStatus.FAILED


@dataclass
class ReportTemplate:
    """Entidad ReportTemplate - Plantilla de reporte."""

    id: str
    name: str
    description: str
    report_type: ReportType
    query_template: str
    parameters_schema: Dict[str, Any]
    is_active: bool = True
    created_at: datetime = None
    updated_at: datetime = None

    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        """Valida los parámetros según el esquema."""
        # Implementar validación según el esquema
        return True

    def render_query(self, parameters: Dict[str, Any]) -> str:
        """Renderiza la consulta con los parámetros."""
        # Implementar renderizado de consulta
        return self.query_template


@dataclass
class ReportSchedule:
    """Entidad ReportSchedule - Programación de reportes."""

    id: str
    template_id: str
    name: str
    cron_expression: str
    parameters: Dict[str, Any]
    is_active: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: datetime = None

    def calculate_next_run(self) -> None:
        """Calcula la próxima ejecución."""
        # Implementar cálculo de próxima ejecución
        pass

    def should_run_now(self) -> bool:
        """Verifica si debe ejecutarse ahora."""
        if not self.is_active:
            return False
        # Implementar lógica de verificación
        return True
