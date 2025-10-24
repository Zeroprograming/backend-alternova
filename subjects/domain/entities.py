"""
Entidades del dominio para subjects.
Contiene las entidades principales del dominio académico.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from enum import Enum


class SubjectStatus(Enum):
    """Estado de una materia."""

    ACTIVE = "active"
    INACTIVE = "inactive"
    FINISHED = "finished"


class EnrollmentStatus(Enum):
    """Estado de una inscripción."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    COMPLETED = "completed"


@dataclass
class Subject:
    """Entidad Subject - Materia/Asignatura."""

    id: str
    code: str
    name: str
    credits: int
    description: Optional[str] = None
    status: SubjectStatus = SubjectStatus.ACTIVE
    created_at: datetime = None
    updated_at: datetime = None

    def is_active(self) -> bool:
        """Verifica si la materia está activa."""
        return self.status == SubjectStatus.ACTIVE

    def can_be_enrolled(self) -> bool:
        """Verifica si la materia puede ser inscrita."""
        return self.is_active()

    def finish_subject(self) -> None:
        """Finaliza la materia."""
        self.status = SubjectStatus.FINISHED
        self.updated_at = datetime.now()


@dataclass
class Enrollment:
    """Entidad Enrollment - Inscripción."""

    id: str
    student_id: str
    subject_id: str
    enrollment_date: datetime
    status: EnrollmentStatus = EnrollmentStatus.PENDING
    final_grade: Optional[float] = None
    created_at: datetime = None
    updated_at: datetime = None

    def approve(self) -> None:
        """Aprueba la inscripción."""
        self.status = EnrollmentStatus.APPROVED
        self.updated_at = datetime.now()

    def reject(self) -> None:
        """Rechaza la inscripción."""
        self.status = EnrollmentStatus.REJECTED
        self.updated_at = datetime.now()

    def complete(self) -> None:
        """Completa la inscripción."""
        self.status = EnrollmentStatus.COMPLETED
        self.updated_at = datetime.now()

    def assign_grade(self, grade: float) -> None:
        """Asigna una calificación."""
        if not 0.0 <= grade <= 5.0:
            raise ValueError("Grade must be between 0.0 and 5.0")
        self.final_grade = grade
        self.updated_at = datetime.now()


@dataclass
class Prerequisite:
    """Entidad Prerequisite - Prerrequisito."""

    id: str
    subject_id: str
    prerequisite_subject_id: str
    created_at: datetime = None

    def is_satisfied(self, completed_subjects: List[str]) -> bool:
        """Verifica si el prerrequisito está satisfecho."""
        return self.prerequisite_subject_id in completed_subjects
