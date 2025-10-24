"""
Interfaces de repositorio para el dominio de reports.
Define los contratos que deben implementar los repositorios.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Report, ReportTemplate, ReportSchedule
from .value_objects import ReportId, TemplateId, ScheduleId, UserId


class ReportRepository(ABC):
    """Repositorio para entidades Report."""

    @abstractmethod
    def save(self, report: Report) -> Report:
        """Guarda un reporte."""
        pass

    @abstractmethod
    def find_by_id(self, report_id: ReportId) -> Optional[Report]:
        """Busca un reporte por ID."""
        pass

    @abstractmethod
    def find_by_user(self, user_id: UserId) -> List[Report]:
        """Busca reportes por usuario."""
        pass

    @abstractmethod
    def find_pending(self) -> List[Report]:
        """Obtiene todos los reportes pendientes."""
        pass

    @abstractmethod
    def find_processing(self) -> List[Report]:
        """Obtiene todos los reportes en procesamiento."""
        pass

    @abstractmethod
    def delete(self, report_id: ReportId) -> bool:
        """Elimina un reporte."""
        pass


class ReportTemplateRepository(ABC):
    """Repositorio para entidades ReportTemplate."""

    @abstractmethod
    def save(self, template: ReportTemplate) -> ReportTemplate:
        """Guarda una plantilla de reporte."""
        pass

    @abstractmethod
    def find_by_id(self, template_id: TemplateId) -> Optional[ReportTemplate]:
        """Busca una plantilla por ID."""
        pass

    @abstractmethod
    def find_by_name(self, name: str) -> Optional[ReportTemplate]:
        """Busca una plantilla por nombre."""
        pass

    @abstractmethod
    def find_active(self) -> List[ReportTemplate]:
        """Obtiene todas las plantillas activas."""
        pass

    @abstractmethod
    def delete(self, template_id: TemplateId) -> bool:
        """Elimina una plantilla."""
        pass


class ReportScheduleRepository(ABC):
    """Repositorio para entidades ReportSchedule."""

    @abstractmethod
    def save(self, schedule: ReportSchedule) -> ReportSchedule:
        """Guarda una programación de reporte."""
        pass

    @abstractmethod
    def find_by_id(self, schedule_id: ScheduleId) -> Optional[ReportSchedule]:
        """Busca una programación por ID."""
        pass

    @abstractmethod
    def find_active(self) -> List[ReportSchedule]:
        """Obtiene todas las programaciones activas."""
        pass

    @abstractmethod
    def find_due_for_execution(self) -> List[ReportSchedule]:
        """Obtiene programaciones que deben ejecutarse."""
        pass

    @abstractmethod
    def delete(self, schedule_id: ScheduleId) -> bool:
        """Elimina una programación."""
        pass
