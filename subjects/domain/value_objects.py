"""
Value Objects para el dominio de subjects.
Objetos inmutables que representan conceptos del dominio académico.
"""

from dataclasses import dataclass
from typing import Optional
import re
from datetime import date


@dataclass(frozen=True)
class SubjectCode:
    """Value Object para códigos de materia."""

    value: str

    def __post_init__(self):
        if not self.value or len(self.value) < 3:
            raise ValueError("Subject code must be at least 3 characters long")
        if not re.match(r"^[A-Z0-9]+$", self.value):
            raise ValueError(
                "Subject code must contain only uppercase letters and numbers"
            )


@dataclass(frozen=True)
class SubjectName:
    """Value Object para nombres de materia."""

    value: str

    def __post_init__(self):
        if not self.value or len(self.value) < 3:
            raise ValueError("Subject name must be at least 3 characters long")
        if len(self.value) > 200:
            raise ValueError("Subject name must not exceed 200 characters")


@dataclass(frozen=True)
class Credits:
    """Value Object para créditos."""

    value: int

    def __post_init__(self):
        if not isinstance(self.value, int) or self.value <= 0:
            raise ValueError("Credits must be a positive integer")
        if self.value > 10:
            raise ValueError("Credits must not exceed 10")


@dataclass(frozen=True)
class Grade:
    """Value Object para calificaciones."""

    value: float

    def __post_init__(self):
        if not isinstance(self.value, (int, float)):
            raise ValueError("Grade must be a number")
        if not 0.0 <= self.value <= 5.0:
            raise ValueError("Grade must be between 0.0 and 5.0")


@dataclass(frozen=True)
class AcademicYear:
    """Value Object para año académico."""

    value: int

    def __post_init__(self):
        current_year = date.today().year
        if not isinstance(self.value, int):
            raise ValueError("Academic year must be an integer")
        if self.value < 2020 or self.value > current_year + 5:
            raise ValueError(
                f"Academic year must be between 2020 and {current_year + 5}"
            )


@dataclass(frozen=True)
class Semester:
    """Value Object para semestre."""

    value: int

    def __post_init__(self):
        if not isinstance(self.value, int):
            raise ValueError("Semester must be an integer")
        if self.value not in [1, 2]:
            raise ValueError("Semester must be 1 or 2")


@dataclass(frozen=True)
class SubjectId:
    """Value Object para ID de materia."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Subject ID cannot be empty")


@dataclass(frozen=True)
class EnrollmentId:
    """Value Object para ID de inscripción."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Enrollment ID cannot be empty")


@dataclass(frozen=True)
class StudentId:
    """Value Object para ID de estudiante."""

    value: str

    def __post_init__(self):
        if not self.value:
            raise ValueError("Student ID cannot be empty")
