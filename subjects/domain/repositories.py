"""
Interfaces de repositorio para el dominio de subjects.
Define los contratos que deben implementar los repositorios.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from .entities import Subject, Enrollment, Prerequisite
from .value_objects import SubjectId, EnrollmentId, StudentId, SubjectCode


class SubjectRepository(ABC):
    """Repositorio para entidades Subject."""

    @abstractmethod
    def save(self, subject: Subject) -> Subject:
        """Guarda una materia."""
        pass

    @abstractmethod
    def find_by_id(self, subject_id: SubjectId) -> Optional[Subject]:
        """Busca una materia por ID."""
        pass

    @abstractmethod
    def find_by_code(self, code: SubjectCode) -> Optional[Subject]:
        """Busca una materia por código."""
        pass

    @abstractmethod
    def find_all(self) -> List[Subject]:
        """Obtiene todas las materias."""
        pass

    @abstractmethod
    def find_active(self) -> List[Subject]:
        """Obtiene todas las materias activas."""
        pass

    @abstractmethod
    def delete(self, subject_id: SubjectId) -> bool:
        """Elimina una materia."""
        pass


class EnrollmentRepository(ABC):
    """Repositorio para entidades Enrollment."""

    @abstractmethod
    def save(self, enrollment: Enrollment) -> Enrollment:
        """Guarda una inscripción."""
        pass

    @abstractmethod
    def find_by_id(self, enrollment_id: EnrollmentId) -> Optional[Enrollment]:
        """Busca una inscripción por ID."""
        pass

    @abstractmethod
    def find_by_student(self, student_id: StudentId) -> List[Enrollment]:
        """Busca inscripciones por estudiante."""
        pass

    @abstractmethod
    def find_by_subject(self, subject_id: SubjectId) -> List[Enrollment]:
        """Busca inscripciones por materia."""
        pass

    @abstractmethod
    def find_pending(self) -> List[Enrollment]:
        """Obtiene todas las inscripciones pendientes."""
        pass

    @abstractmethod
    def delete(self, enrollment_id: EnrollmentId) -> bool:
        """Elimina una inscripción."""
        pass


class PrerequisiteRepository(ABC):
    """Repositorio para entidades Prerequisite."""

    @abstractmethod
    def save(self, prerequisite: Prerequisite) -> Prerequisite:
        """Guarda un prerrequisito."""
        pass

    @abstractmethod
    def find_by_subject(self, subject_id: SubjectId) -> List[Prerequisite]:
        """Busca prerrequisitos por materia."""
        pass

    @abstractmethod
    def find_by_prerequisite(
        self, prerequisite_subject_id: SubjectId
    ) -> List[Prerequisite]:
        """Busca materias que requieren un prerrequisito."""
        pass

    @abstractmethod
    def delete(self, prerequisite_id: str) -> bool:
        """Elimina un prerrequisito."""
        pass
