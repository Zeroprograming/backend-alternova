"""
Servicios específicos para inscripciones.
Separado de subjects/services.py para mejor organización.
"""

from django.db import transaction
from .models import Enrollment, Subject
from users.models import User
from common.audit_services import AuditService
import logging

logger = logging.getLogger(__name__)


class EnrollmentService:
    """Servicio para gestión de inscripciones."""

    @staticmethod
    @transaction.atomic
    def create_enrollment(student, subject, requesting_user):
        """
        Crea una nueva inscripción.

        Args:
            student: Estudiante a inscribir
            subject: Materia a inscribir
            requesting_user: Usuario que hace la petición

        Returns:
            Enrollment: Nueva inscripción

        Raises:
            PermissionError: Si no tiene permisos
            ValueError: Si ya está inscrito o materia no disponible
        """
        # Solo el estudiante puede inscribirse a sí mismo, o admin puede inscribir a cualquiera
        if student != requesting_user and not requesting_user.is_staff:
            raise PermissionError("Solo puedes inscribirte a ti mismo")

        # Verificar que el estudiante existe y está activo
        if not student.is_active or not student.is_student:
            raise ValueError("Estudiante no válido")

        # Verificar que la materia existe y está activa
        if not subject.is_active:
            raise ValueError("Materia no disponible")

        # Verificar que no esté ya inscrito
        existing = Enrollment.objects.filter(
            student=student, subject=subject, is_active=True
        ).exists()
        if existing:
            raise ValueError("Ya estás inscrito en esta materia")

        # Crear inscripción
        enrollment = Enrollment.objects.create(
            student=student,
            subject=subject,
            created_by=requesting_user,
            updated_by=requesting_user,
        )

        # Log de auditoría
        AuditService.log_enrollment(student, subject)

        logger.info(
            f"Estudiante {student.username} inscrito en {subject.code} por {requesting_user.username}"
        )

        return enrollment

    @staticmethod
    def list_enrollments(requesting_user, subject_id=None, student_id=None):
        """
        Lista inscripciones según permisos.

        Args:
            requesting_user: Usuario que hace la petición
            subject_id: Filtro opcional por materia
            student_id: Filtro opcional por estudiante

        Returns:
            QuerySet: Inscripciones filtradas
        """
        queryset = Enrollment.objects.filter(is_active=True)

        # Filtrar según rol
        if requesting_user.is_student:
            queryset = queryset.filter(student=requesting_user)
        elif requesting_user.is_teacher:
            queryset = queryset.filter(subject__teacher=requesting_user)
        # Admin ve todas

        # Filtros adicionales
        if subject_id:
            queryset = queryset.filter(subject_id=subject_id)

        if student_id:
            queryset = queryset.filter(student_id=student_id)

        return queryset

    @staticmethod
    def retrieve_enrollment(enrollment_id, requesting_user):
        """
        Obtiene una inscripción con validaciones.

        Args:
            enrollment_id: ID de la inscripción
            requesting_user: Usuario que hace la petición

        Returns:
            Enrollment: Inscripción encontrada

        Raises:
            ValueError: Si no existe o no tiene permisos
            PermissionError: Si no tiene acceso
        """
        try:
            enrollment = Enrollment.objects.get(id=enrollment_id, is_active=True)

            # Validar acceso
            if requesting_user.is_student and enrollment.student != requesting_user:
                raise PermissionError("Solo puedes ver tus propias inscripciones")

            if (
                requesting_user.is_teacher
                and enrollment.subject.teacher != requesting_user
            ):
                raise PermissionError("Solo puedes ver inscripciones de tus materias")

            # Admin puede ver todas

            return enrollment

        except Enrollment.DoesNotExist:
            raise ValueError("Inscripción no encontrada")

    @staticmethod
    @transaction.atomic
    def update_enrollment(enrollment, data, requesting_user):
        """
        Actualiza una inscripción (solo nota generalmente).

        Args:
            enrollment: Inscripción a actualizar
            data: Nuevos datos
            requesting_user: Usuario que actualiza

        Returns:
            Enrollment: Inscripción actualizada

        Raises:
            PermissionError: Si no tiene permisos
        """
        # Solo profesor de la materia o admin
        if (
            not requesting_user.is_staff
            and enrollment.subject.teacher != requesting_user
        ):
            raise PermissionError(
                "Solo el profesor de la materia puede modificar inscripciones"
            )

        # Actualizar
        for key, value in data.items():
            setattr(enrollment, key, value)

        enrollment.updated_by = requesting_user
        enrollment.save()

        logger.info(
            f"Inscripción {enrollment.id} actualizada por {requesting_user.username}"
        )

        return enrollment

    @staticmethod
    @transaction.atomic
    def delete_enrollment(enrollment, requesting_user):
        """
        Elimina (desactiva) una inscripción.

        Args:
            enrollment: Inscripción a eliminar
            requesting_user: Usuario que elimina

        Returns:
            Enrollment: Inscripción desactivada

        Raises:
            ValueError: Si ya tiene nota
            PermissionError: Si no tiene permisos
        """
        # Estudiante puede des-inscribirse o admin
        if enrollment.student != requesting_user and not requesting_user.is_staff:
            raise PermissionError("No puedes eliminar esta inscripción")

        # No permitir si ya tiene nota
        if enrollment.final_grade is not None:
            raise ValueError("No puedes eliminar: ya tiene nota asignada")

        # Soft delete
        enrollment.soft_delete()

        logger.info(
            f"Inscripción {enrollment.id} eliminada por {requesting_user.username}"
        )

        return enrollment
