"""
Servicios de dominio para subjects.
Contiene la lógica de negocio específica del dominio académico.
"""

from typing import List, Optional
from .entities import Subject, Enrollment, Prerequisite
from .value_objects import SubjectId, StudentId, Grade
from .repositories import (
    SubjectRepository,
    EnrollmentRepository,
    PrerequisiteRepository,
)


class SubjectDomainService:
    """Servicio de dominio para materias."""

    def __init__(
        self,
        subject_repository: SubjectRepository,
        prerequisite_repository: PrerequisiteRepository,
    ):
        self.subject_repository = subject_repository
        self.prerequisite_repository = prerequisite_repository

    def can_student_enroll(self, student_id: StudentId, subject_id: SubjectId) -> bool:
        """Verifica si un estudiante puede inscribirse en una materia."""
        subject = self.subject_repository.find_by_id(subject_id)
        if not subject or not subject.can_be_enrolled():
            return False

        # Verificar prerrequisitos
        prerequisites = self.prerequisite_repository.find_by_subject(subject_id)
        if not prerequisites:
            return True

        # Obtener materias completadas por el estudiante
        completed_subjects = self._get_completed_subjects(student_id)

        # Verificar que todos los prerrequisitos estén satisfechos
        return all(prereq.is_satisfied(completed_subjects) for prereq in prerequisites)

    def _get_completed_subjects(self, student_id: StudentId) -> List[str]:
        """Obtiene las materias completadas por un estudiante."""
        # Esta lógica debería implementarse en el repositorio de inscripciones
        # Por ahora retornamos una lista vacía como placeholder
        return []


class EnrollmentDomainService:
    """Servicio de dominio para inscripciones."""

    def __init__(
        self,
        enrollment_repository: EnrollmentRepository,
        subject_repository: SubjectRepository,
    ):
        self.enrollment_repository = enrollment_repository
        self.subject_repository = subject_repository

    def calculate_final_grade(self, enrollment: Enrollment) -> Optional[float]:
        """Calcula la calificación final de una inscripción."""
        if enrollment.final_grade is not None:
            return enrollment.final_grade

        # Aquí se implementaría la lógica para calcular la calificación final
        # basada en evaluaciones parciales, tareas, etc.
        return None

    def is_enrollment_complete(self, enrollment: Enrollment) -> bool:
        """Verifica si una inscripción está completa."""
        return enrollment.status.value == "completed"

    def can_assign_grade(self, enrollment: Enrollment) -> bool:
        """Verifica si se puede asignar calificación a una inscripción."""
        return enrollment.status.value == "approved"
