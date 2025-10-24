"""
DTOs para la capa de aplicación de reports.
Data Transfer Objects para transferir datos entre capas.
"""

from dataclasses import dataclass
from typing import List, Optional, Dict, Any
from datetime import datetime
from ..domain.value_objects import (
    ReportId,
    TemplateId,
    ScheduleId,
    UserId,
    ReportName,
    FilePath,
    CronExpression,
)


@dataclass
class ReportDTO:
    """DTO para entidad Report."""

    id: str
    name: str
    report_type: str
    status: str = "pending"
    parameters: Optional[Dict[str, Any]] = None
    file_path: Optional[str] = None
    created_by: str = ""
    created_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None


@dataclass
class CreateReportDTO:
    """DTO para crear un reporte."""

    name: str
    report_type: str
    template_id: str
    parameters: Optional[Dict[str, Any]] = None
    created_by: str = ""


@dataclass
class UpdateReportDTO:
    """DTO para actualizar un reporte."""

    id: str
    status: Optional[str] = None
    file_path: Optional[str] = None
    error_message: Optional[str] = None


@dataclass
class ReportTemplateDTO:
    """DTO para entidad ReportTemplate."""

    id: str
    name: str
    description: str
    report_type: str
    query_template: str
    parameters_schema: Dict[str, Any]
    is_active: bool = True
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class CreateReportTemplateDTO:
    """DTO para crear una plantilla de reporte."""

    name: str
    description: str
    report_type: str
    query_template: str
    parameters_schema: Dict[str, Any]


@dataclass
class UpdateReportTemplateDTO:
    """DTO para actualizar una plantilla de reporte."""

    id: str
    name: Optional[str] = None
    description: Optional[str] = None
    query_template: Optional[str] = None
    parameters_schema: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


@dataclass
class ReportScheduleDTO:
    """DTO para entidad ReportSchedule."""

    id: str
    template_id: str
    name: str
    cron_expression: str
    parameters: Dict[str, Any]
    is_active: bool = True
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: Optional[datetime] = None


@dataclass
class CreateReportScheduleDTO:
    """DTO para crear una programación de reporte."""

    template_id: str
    name: str
    cron_expression: str
    parameters: Dict[str, Any]


@dataclass
class UpdateReportScheduleDTO:
    """DTO para actualizar una programación de reporte."""

    id: str
    name: Optional[str] = None
    cron_expression: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    is_active: Optional[bool] = None


@dataclass
class ReportGenerationRequestDTO:
    """DTO para solicitud de generación de reporte."""

    template_id: str
    parameters: Dict[str, Any]
    report_type: str
    user_id: str


@dataclass
class ReportGenerationResponseDTO:
    """DTO para respuesta de generación de reporte."""

    report_id: str
    status: str
    message: str
    estimated_completion_time: Optional[datetime] = None


@dataclass
class ReportStatisticsDTO:
    """DTO para estadísticas de reportes."""

    total_reports: int
    completed_reports: int
    failed_reports: int
    pending_reports: int
    processing_reports: int
    average_generation_time: Optional[float] = None
