"""
DTOs para la capa de aplicación de subjects.
Data Transfer Objects para transferir datos entre capas.
"""

from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from ..domain.value_objects import (
    SubjectCode,
    SubjectName,
    Credits,
    Grade,
    SubjectId,
    StudentId,
    EnrollmentId,
)


@dataclass
class SubjectDTO:
    """DTO para entidad Subject."""

    id: str
    code: str
    name: str
    credits: int
    description: Optional[str] = None
    status: str = "active"
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class CreateSubjectDTO:
    """DTO para crear una materia."""

    code: str
    name: str
    credits: int
    description: Optional[str] = None


@dataclass
class UpdateSubjectDTO:
    """DTO para actualizar una materia."""

    id: str
    name: Optional[str] = None
    credits: Optional[int] = None
    description: Optional[str] = None
    status: Optional[str] = None


@dataclass
class EnrollmentDTO:
    """DTO para entidad Enrollment."""

    id: str
    student_id: str
    subject_id: str
    enrollment_date: datetime
    status: str = "pending"
    final_grade: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None


@dataclass
class CreateEnrollmentDTO:
    """DTO para crear una inscripción."""

    student_id: str
    subject_id: str


@dataclass
class UpdateEnrollmentDTO:
    """DTO para actualizar una inscripción."""

    id: str
    status: Optional[str] = None
    final_grade: Optional[float] = None


@dataclass
class PrerequisiteDTO:
    """DTO para entidad Prerequisite."""

    id: str
    subject_id: str
    prerequisite_subject_id: str
    created_at: Optional[datetime] = None


@dataclass
class CreatePrerequisiteDTO:
    """DTO para crear un prerrequisito."""

    subject_id: str
    prerequisite_subject_id: str


@dataclass
class AcademicSummaryDTO:
    """DTO para resumen académico."""

    student_id: str
    total_subjects: int
    completed_subjects: int
    pending_subjects: int
    average_grade: Optional[float] = None
    total_credits: int = 0


@dataclass
class SubjectStatisticsDTO:
    """DTO para estadísticas de materia."""

    subject_id: str
    total_enrollments: int
    approved_enrollments: int
    rejected_enrollments: int
    average_grade: Optional[float] = None
