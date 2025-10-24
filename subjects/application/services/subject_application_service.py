"""
Servicios de aplicación para subjects.
Orquesta los use cases y coordina entre capas.
"""

from typing import List, Optional
from ..domain.repositories import (
    SubjectRepository,
    EnrollmentRepository,
    PrerequisiteRepository,
)
from ..domain.services import SubjectDomainService, EnrollmentDomainService
from .use_cases.subject_use_cases import SubjectUseCases, EnrollmentUseCases
from .dto.subject_dto import (
    SubjectDTO,
    CreateSubjectDTO,
    UpdateSubjectDTO,
    EnrollmentDTO,
    CreateEnrollmentDTO,
    UpdateEnrollmentDTO,
    PrerequisiteDTO,
    CreatePrerequisiteDTO,
    AcademicSummaryDTO,
    SubjectStatisticsDTO,
)


class SubjectApplicationService:
    """Servicio de aplicación para materias."""

    def __init__(
        self,
        subject_repository: SubjectRepository,
        prerequisite_repository: PrerequisiteRepository,
        enrollment_repository: EnrollmentRepository,
    ):
        self.subject_repository = subject_repository
        self.prerequisite_repository = prerequisite_repository
        self.enrollment_repository = enrollment_repository

        # Inicializar servicios de dominio
        self.subject_domain_service = SubjectDomainService(
            subject_repository, prerequisite_repository
        )
        self.enrollment_domain_service = EnrollmentDomainService(
            enrollment_repository, subject_repository
        )

        # Inicializar use cases
        self.subject_use_cases = SubjectUseCases(
            subject_repository, prerequisite_repository, self.subject_domain_service
        )
        self.enrollment_use_cases = EnrollmentUseCases(
            enrollment_repository,
            subject_repository,
            self.enrollment_domain_service,
            self.subject_domain_service,
        )

    def create_subject(self, dto: CreateSubjectDTO) -> SubjectDTO:
        """Crea una nueva materia."""
        return self.subject_use_cases.create_subject(dto)

    def get_subject(self, subject_id: str) -> Optional[SubjectDTO]:
        """Obtiene una materia por ID."""
        return self.subject_use_cases.get_subject(subject_id)

    def list_subjects(self) -> List[SubjectDTO]:
        """Lista todas las materias."""
        return self.subject_use_cases.list_subjects()

    def update_subject(self, dto: UpdateSubjectDTO) -> Optional[SubjectDTO]:
        """Actualiza una materia."""
        return self.subject_use_cases.update_subject(dto)

    def delete_subject(self, subject_id: str) -> bool:
        """Elimina una materia."""
        return self.subject_use_cases.delete_subject(subject_id)

    def create_enrollment(self, dto: CreateEnrollmentDTO) -> EnrollmentDTO:
        """Crea una nueva inscripción."""
        return self.enrollment_use_cases.create_enrollment(dto)

    def approve_enrollment(self, enrollment_id: str) -> Optional[EnrollmentDTO]:
        """Aprueba una inscripción."""
        return self.enrollment_use_cases.approve_enrollment(enrollment_id)

    def assign_grade(self, enrollment_id: str, grade: float) -> Optional[EnrollmentDTO]:
        """Asigna una calificación a una inscripción."""
        return self.enrollment_use_cases.assign_grade(enrollment_id, grade)

    def get_academic_summary(self, student_id: str) -> AcademicSummaryDTO:
        """Obtiene el resumen académico de un estudiante."""
        enrollments = self.enrollment_repository.find_by_student(student_id)

        total_subjects = len(enrollments)
        completed_subjects = len(
            [e for e in enrollments if e.status.value == "completed"]
        )
        pending_subjects = len([e for e in enrollments if e.status.value == "pending"])

        # Calcular promedio de calificaciones
        grades = [e.final_grade for e in enrollments if e.final_grade is not None]
        average_grade = sum(grades) / len(grades) if grades else None

        # Calcular total de créditos
        total_credits = 0
        for enrollment in enrollments:
            if enrollment.status.value == "completed":
                subject = self.subject_repository.find_by_id(enrollment.subject_id)
                if subject:
                    total_credits += subject.credits

        return AcademicSummaryDTO(
            student_id=student_id,
            total_subjects=total_subjects,
            completed_subjects=completed_subjects,
            pending_subjects=pending_subjects,
            average_grade=average_grade,
            total_credits=total_credits,
        )

    def get_subject_statistics(self, subject_id: str) -> SubjectStatisticsDTO:
        """Obtiene estadísticas de una materia."""
        enrollments = self.enrollment_repository.find_by_subject(subject_id)

        total_enrollments = len(enrollments)
        approved_enrollments = len(
            [e for e in enrollments if e.status.value == "approved"]
        )
        rejected_enrollments = len(
            [e for e in enrollments if e.status.value == "rejected"]
        )

        # Calcular promedio de calificaciones
        grades = [e.final_grade for e in enrollments if e.final_grade is not None]
        average_grade = sum(grades) / len(grades) if grades else None

        return SubjectStatisticsDTO(
            subject_id=subject_id,
            total_enrollments=total_enrollments,
            approved_enrollments=approved_enrollments,
            rejected_enrollments=rejected_enrollments,
            average_grade=average_grade,
        )
