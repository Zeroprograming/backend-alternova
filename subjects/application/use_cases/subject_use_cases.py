"""
Use Cases para la capa de aplicación de subjects.
Implementa los casos de uso específicos del dominio académico.
"""

from typing import List, Optional
from ..domain.entities import Subject, Enrollment, Prerequisite
from ..domain.value_objects import (
    SubjectId,
    StudentId,
    EnrollmentId,
    SubjectCode,
    Grade,
)
from ..domain.repositories import (
    SubjectRepository,
    EnrollmentRepository,
    PrerequisiteRepository,
)
from ..domain.services import SubjectDomainService, EnrollmentDomainService
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


class SubjectUseCases:
    """Use Cases para gestión de materias."""

    def __init__(
        self,
        subject_repository: SubjectRepository,
        prerequisite_repository: PrerequisiteRepository,
        subject_domain_service: SubjectDomainService,
    ):
        self.subject_repository = subject_repository
        self.prerequisite_repository = prerequisite_repository
        self.subject_domain_service = subject_domain_service

    def create_subject(self, dto: CreateSubjectDTO) -> SubjectDTO:
        """Crea una nueva materia."""
        # Validar que el código no exista
        existing_subject = self.subject_repository.find_by_code(SubjectCode(dto.code))
        if existing_subject:
            raise ValueError("Subject code already exists")

        # Crear entidad
        subject = Subject(
            id="",  # Se asignará en el repositorio
            code=dto.code,
            name=dto.name,
            credits=dto.credits,
            description=dto.description,
        )

        # Guardar
        saved_subject = self.subject_repository.save(subject)

        # Convertir a DTO
        return SubjectDTO(
            id=saved_subject.id,
            code=saved_subject.code,
            name=saved_subject.name,
            credits=saved_subject.credits,
            description=saved_subject.description,
            status=saved_subject.status.value,
            created_at=saved_subject.created_at,
            updated_at=saved_subject.updated_at,
        )

    def get_subject(self, subject_id: str) -> Optional[SubjectDTO]:
        """Obtiene una materia por ID."""
        subject = self.subject_repository.find_by_id(SubjectId(subject_id))
        if not subject:
            return None

        return SubjectDTO(
            id=subject.id,
            code=subject.code,
            name=subject.name,
            credits=subject.credits,
            description=subject.description,
            status=subject.status.value,
            created_at=subject.created_at,
            updated_at=subject.updated_at,
        )

    def list_subjects(self) -> List[SubjectDTO]:
        """Lista todas las materias."""
        subjects = self.subject_repository.find_all()
        return [
            SubjectDTO(
                id=subject.id,
                code=subject.code,
                name=subject.name,
                credits=subject.credits,
                description=subject.description,
                status=subject.status.value,
                created_at=subject.created_at,
                updated_at=subject.updated_at,
            )
            for subject in subjects
        ]

    def update_subject(self, dto: UpdateSubjectDTO) -> Optional[SubjectDTO]:
        """Actualiza una materia."""
        subject = self.subject_repository.find_by_id(SubjectId(dto.id))
        if not subject:
            return None

        # Actualizar campos
        if dto.name:
            subject.name = dto.name
        if dto.credits:
            subject.credits = dto.credits
        if dto.description is not None:
            subject.description = dto.description
        if dto.status:
            from ..domain.entities import SubjectStatus

            subject.status = SubjectStatus(dto.status)

        # Guardar
        saved_subject = self.subject_repository.save(subject)

        return SubjectDTO(
            id=saved_subject.id,
            code=saved_subject.code,
            name=saved_subject.name,
            credits=saved_subject.credits,
            description=saved_subject.description,
            status=saved_subject.status.value,
            created_at=saved_subject.created_at,
            updated_at=saved_subject.updated_at,
        )

    def delete_subject(self, subject_id: str) -> bool:
        """Elimina una materia."""
        return self.subject_repository.delete(SubjectId(subject_id))


class EnrollmentUseCases:
    """Use Cases para gestión de inscripciones."""

    def __init__(
        self,
        enrollment_repository: EnrollmentRepository,
        subject_repository: SubjectRepository,
        enrollment_domain_service: EnrollmentDomainService,
        subject_domain_service: SubjectDomainService,
    ):
        self.enrollment_repository = enrollment_repository
        self.subject_repository = subject_repository
        self.enrollment_domain_service = enrollment_domain_service
        self.subject_domain_service = subject_domain_service

    def create_enrollment(self, dto: CreateEnrollmentDTO) -> EnrollmentDTO:
        """Crea una nueva inscripción."""
        # Verificar que el estudiante puede inscribirse
        can_enroll = self.subject_domain_service.can_student_enroll(
            StudentId(dto.student_id), SubjectId(dto.subject_id)
        )
        if not can_enroll:
            raise ValueError("Student cannot enroll in this subject")

        # Crear entidad
        from datetime import datetime

        enrollment = Enrollment(
            id="",  # Se asignará en el repositorio
            student_id=dto.student_id,
            subject_id=dto.subject_id,
            enrollment_date=datetime.now(),
        )

        # Guardar
        saved_enrollment = self.enrollment_repository.save(enrollment)

        # Convertir a DTO
        return EnrollmentDTO(
            id=saved_enrollment.id,
            student_id=saved_enrollment.student_id,
            subject_id=saved_enrollment.subject_id,
            enrollment_date=saved_enrollment.enrollment_date,
            status=saved_enrollment.status.value,
            final_grade=saved_enrollment.final_grade,
            created_at=saved_enrollment.created_at,
            updated_at=saved_enrollment.updated_at,
        )

    def approve_enrollment(self, enrollment_id: str) -> Optional[EnrollmentDTO]:
        """Aprueba una inscripción."""
        enrollment = self.enrollment_repository.find_by_id(EnrollmentId(enrollment_id))
        if not enrollment:
            return None

        enrollment.approve()
        saved_enrollment = self.enrollment_repository.save(enrollment)

        return EnrollmentDTO(
            id=saved_enrollment.id,
            student_id=saved_enrollment.student_id,
            subject_id=saved_enrollment.subject_id,
            enrollment_date=saved_enrollment.enrollment_date,
            status=saved_enrollment.status.value,
            final_grade=saved_enrollment.final_grade,
            created_at=saved_enrollment.created_at,
            updated_at=saved_enrollment.updated_at,
        )

    def assign_grade(self, enrollment_id: str, grade: float) -> Optional[EnrollmentDTO]:
        """Asigna una calificación a una inscripción."""
        enrollment = self.enrollment_repository.find_by_id(EnrollmentId(enrollment_id))
        if not enrollment:
            return None

        if not self.enrollment_domain_service.can_assign_grade(enrollment):
            raise ValueError("Cannot assign grade to this enrollment")

        enrollment.assign_grade(grade)
        saved_enrollment = self.enrollment_repository.save(enrollment)

        return EnrollmentDTO(
            id=saved_enrollment.id,
            student_id=saved_enrollment.student_id,
            subject_id=saved_enrollment.subject_id,
            enrollment_date=saved_enrollment.enrollment_date,
            status=saved_enrollment.status.value,
            final_grade=saved_enrollment.final_grade,
            created_at=saved_enrollment.created_at,
            updated_at=saved_enrollment.updated_at,
        )
