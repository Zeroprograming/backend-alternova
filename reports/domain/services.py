"""
Servicios de dominio para reports.
Contiene la lógica de negocio específica del dominio de reportes.
"""

from typing import List, Optional, Dict, Any
from .entities import Report, ReportTemplate, ReportSchedule
from .value_objects import ReportId, TemplateId, ScheduleId, UserId, ReportName
from .repositories import (
    ReportRepository,
    ReportTemplateRepository,
    ReportScheduleRepository,
)


class ReportDomainService:
    """Servicio de dominio para reportes."""

    def __init__(
        self,
        report_repository: ReportRepository,
        template_repository: ReportTemplateRepository,
    ):
        self.report_repository = report_repository
        self.template_repository = template_repository

    def can_generate_report(self, template_id: TemplateId, user_id: UserId) -> bool:
        """Verifica si un usuario puede generar un reporte."""
        template = self.template_repository.find_by_id(template_id)
        if not template or not template.is_active:
            return False

        # Aquí se implementaría la lógica de permisos específica
        # Por ejemplo, verificar roles, permisos, etc.
        return True

    def validate_report_parameters(
        self, template_id: TemplateId, parameters: Dict[str, Any]
    ) -> bool:
        """Valida los parámetros de un reporte."""
        template = self.template_repository.find_by_id(template_id)
        if not template:
            return False

        return template.validate_parameters(parameters)

    def calculate_report_priority(self, report: Report) -> int:
        """Calcula la prioridad de un reporte."""
        # Lógica para calcular prioridad basada en tipo, usuario, etc.
        priority_map = {
            "csv": 1,
            "excel": 2,
            "pdf": 3,
            "json": 1,
        }
        return priority_map.get(report.report_type.value, 1)


class ReportTemplateDomainService:
    """Servicio de dominio para plantillas de reporte."""

    def __init__(self, template_repository: ReportTemplateRepository):
        self.template_repository = template_repository

    def can_modify_template(self, template_id: TemplateId, user_id: UserId) -> bool:
        """Verifica si un usuario puede modificar una plantilla."""
        template = self.template_repository.find_by_id(template_id)
        if not template:
            return False

        # Implementar lógica de permisos
        return True

    def validate_query_template(self, query: str) -> bool:
        """Valida una plantilla de consulta."""
        if not query or len(query.strip()) < 10:
            return False

        # Validaciones adicionales de SQL/consulta
        dangerous_keywords = ["DROP", "DELETE", "TRUNCATE", "ALTER"]
        query_upper = query.upper()

        for keyword in dangerous_keywords:
            if keyword in query_upper:
                return False

        return True


class ReportScheduleDomainService:
    """Servicio de dominio para programaciones de reportes."""

    def __init__(
        self,
        schedule_repository: ReportScheduleRepository,
        template_repository: ReportTemplateRepository,
    ):
        self.schedule_repository = schedule_repository
        self.template_repository = template_repository

    def can_schedule_report(self, template_id: TemplateId, user_id: UserId) -> bool:
        """Verifica si un usuario puede programar un reporte."""
        template = self.template_repository.find_by_id(template_id)
        if not template or not template.is_active:
            return False

        # Implementar lógica de permisos
        return True

    def should_execute_schedule(self, schedule: ReportSchedule) -> bool:
        """Verifica si una programación debe ejecutarse."""
        if not schedule.is_active:
            return False

        return schedule.should_run_now()
