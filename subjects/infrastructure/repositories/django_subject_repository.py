"""
Implementación de repositorios usando Django ORM para subjects.
Conecta la capa de dominio con la capa de infraestructura.
"""

from typing import List, Optional
from django.db import models
from ...domain.entities import Subject, Enrollment, Prerequisite
from ...domain.value_objects import SubjectId, StudentId, EnrollmentId, SubjectCode
from ...domain.repositories import (
    SubjectRepository,
    EnrollmentRepository,
    PrerequisiteRepository,
)


class DjangoSubjectRepository(SubjectRepository):
    """Implementación de SubjectRepository usando Django ORM."""

    def __init__(self, model_class):
        self.model_class = model_class

    def save(self, subject: Subject) -> Subject:
        """Guarda una materia."""
        if subject.id:
            # Actualizar
            django_subject = self.model_class.objects.get(id=subject.id)
            django_subject.code = subject.code
            django_subject.name = subject.name
            django_subject.credits = subject.credits
            django_subject.description = subject.description
            django_subject.status = subject.status.value
            django_subject.save()
        else:
            # Crear
            django_subject = self.model_class.objects.create(
                code=subject.code,
                name=subject.name,
                credits=subject.credits,
                description=subject.description,
                status=subject.status.value,
            )

        return self._django_to_domain(django_subject)

    def find_by_id(self, subject_id: SubjectId) -> Optional[Subject]:
        """Busca una materia por ID."""
        try:
            django_subject = self.model_class.objects.get(id=subject_id.value)
            return self._django_to_domain(django_subject)
        except self.model_class.DoesNotExist:
            return None

    def find_by_code(self, code: SubjectCode) -> Optional[Subject]:
        """Busca una materia por código."""
        try:
            django_subject = self.model_class.objects.get(code=code.value)
            return self._django_to_domain(django_subject)
        except self.model_class.DoesNotExist:
            return None

    def find_all(self) -> List[Subject]:
        """Obtiene todas las materias."""
        django_subjects = self.model_class.objects.all()
        return [self._django_to_domain(subject) for subject in django_subjects]

    def find_active(self) -> List[Subject]:
        """Obtiene todas las materias activas."""
        django_subjects = self.model_class.objects.filter(status="active")
        return [self._django_to_domain(subject) for subject in django_subjects]

    def delete(self, subject_id: SubjectId) -> bool:
        """Elimina una materia."""
        try:
            django_subject = self.model_class.objects.get(id=subject_id.value)
            django_subject.delete()
            return True
        except self.model_class.DoesNotExist:
            return False

    def _django_to_domain(self, django_subject) -> Subject:
        """Convierte modelo Django a entidad de dominio."""
        from ...domain.entities import SubjectStatus

        return Subject(
            id=str(django_subject.id),
            code=django_subject.code,
            name=django_subject.name,
            credits=django_subject.credits,
            description=django_subject.description,
            status=SubjectStatus(django_subject.status),
            created_at=django_subject.created_at,
            updated_at=django_subject.updated_at,
        )


class DjangoEnrollmentRepository(EnrollmentRepository):
    """Implementación de EnrollmentRepository usando Django ORM."""

    def __init__(self, model_class):
        self.model_class = model_class

    def save(self, enrollment: Enrollment) -> Enrollment:
        """Guarda una inscripción."""
        if enrollment.id:
            # Actualizar
            django_enrollment = self.model_class.objects.get(id=enrollment.id)
            django_enrollment.student_id = enrollment.student_id
            django_enrollment.subject_id = enrollment.subject_id
            django_enrollment.enrollment_date = enrollment.enrollment_date
            django_enrollment.status = enrollment.status.value
            django_enrollment.final_grade = enrollment.final_grade
            django_enrollment.save()
        else:
            # Crear
            django_enrollment = self.model_class.objects.create(
                student_id=enrollment.student_id,
                subject_id=enrollment.subject_id,
                enrollment_date=enrollment.enrollment_date,
                status=enrollment.status.value,
                final_grade=enrollment.final_grade,
            )

        return self._django_to_domain(django_enrollment)

    def find_by_id(self, enrollment_id: EnrollmentId) -> Optional[Enrollment]:
        """Busca una inscripción por ID."""
        try:
            django_enrollment = self.model_class.objects.get(id=enrollment_id.value)
            return self._django_to_domain(django_enrollment)
        except self.model_class.DoesNotExist:
            return None

    def find_by_student(self, student_id: StudentId) -> List[Enrollment]:
        """Busca inscripciones por estudiante."""
        django_enrollments = self.model_class.objects.filter(
            student_id=student_id.value
        )
        return [self._django_to_domain(enrollment) for enrollment in django_enrollments]

    def find_by_subject(self, subject_id: SubjectId) -> List[Enrollment]:
        """Busca inscripciones por materia."""
        django_enrollments = self.model_class.objects.filter(
            subject_id=subject_id.value
        )
        return [self._django_to_domain(enrollment) for enrollment in django_enrollments]

    def find_pending(self) -> List[Enrollment]:
        """Obtiene todas las inscripciones pendientes."""
        django_enrollments = self.model_class.objects.filter(status="pending")
        return [self._django_to_domain(enrollment) for enrollment in django_enrollments]

    def delete(self, enrollment_id: EnrollmentId) -> bool:
        """Elimina una inscripción."""
        try:
            django_enrollment = self.model_class.objects.get(id=enrollment_id.value)
            django_enrollment.delete()
            return True
        except self.model_class.DoesNotExist:
            return False

    def _django_to_domain(self, django_enrollment) -> Enrollment:
        """Convierte modelo Django a entidad de dominio."""
        from ...domain.entities import EnrollmentStatus

        return Enrollment(
            id=str(django_enrollment.id),
            student_id=django_enrollment.student_id,
            subject_id=django_enrollment.subject_id,
            enrollment_date=django_enrollment.enrollment_date,
            status=EnrollmentStatus(django_enrollment.status),
            final_grade=django_enrollment.final_grade,
            created_at=django_enrollment.created_at,
            updated_at=django_enrollment.updated_at,
        )


class DjangoPrerequisiteRepository(PrerequisiteRepository):
    """Implementación de PrerequisiteRepository usando Django ORM."""

    def __init__(self, model_class):
        self.model_class = model_class

    def save(self, prerequisite: Prerequisite) -> Prerequisite:
        """Guarda un prerrequisito."""
        if prerequisite.id:
            # Actualizar
            django_prerequisite = self.model_class.objects.get(id=prerequisite.id)
            django_prerequisite.subject_id = prerequisite.subject_id
            django_prerequisite.prerequisite_subject_id = (
                prerequisite.prerequisite_subject_id
            )
            django_prerequisite.save()
        else:
            # Crear
            django_prerequisite = self.model_class.objects.create(
                subject_id=prerequisite.subject_id,
                prerequisite_subject_id=prerequisite.prerequisite_subject_id,
            )

        return self._django_to_domain(django_prerequisite)

    def find_by_subject(self, subject_id: SubjectId) -> List[Prerequisite]:
        """Busca prerrequisitos por materia."""
        django_prerequisites = self.model_class.objects.filter(
            subject_id=subject_id.value
        )
        return [
            self._django_to_domain(prerequisite)
            for prerequisite in django_prerequisites
        ]

    def find_by_prerequisite(
        self, prerequisite_subject_id: SubjectId
    ) -> List[Prerequisite]:
        """Busca materias que requieren un prerrequisito."""
        django_prerequisites = self.model_class.objects.filter(
            prerequisite_subject_id=prerequisite_subject_id.value
        )
        return [
            self._django_to_domain(prerequisite)
            for prerequisite in django_prerequisites
        ]

    def delete(self, prerequisite_id: str) -> bool:
        """Elimina un prerrequisito."""
        try:
            django_prerequisite = self.model_class.objects.get(id=prerequisite_id)
            django_prerequisite.delete()
            return True
        except self.model_class.DoesNotExist:
            return False

    def _django_to_domain(self, django_prerequisite) -> Prerequisite:
        """Convierte modelo Django a entidad de dominio."""
        return Prerequisite(
            id=str(django_prerequisite.id),
            subject_id=django_prerequisite.subject_id,
            prerequisite_subject_id=django_prerequisite.prerequisite_subject_id,
            created_at=django_prerequisite.created_at,
        )
