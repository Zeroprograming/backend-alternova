"""
Servicios de lógica de negocio para materias.
"""

from django.db import transaction
from ...infrastructure.models import Subject, Enrollment
import logging

logger = logging.getLogger(__name__)


class SubjectService:
    """Servicio para gestión de materias."""

    @staticmethod
    @transaction.atomic
    def enroll_student(student, subject):
        """
        Inscribe un estudiante en una materia.

        Args:
            student: Usuario estudiante
            subject: Materia

        Returns:
            Enrollment: Inscripción creada

        Raises:
            ValueError: Si ya está inscrito o hay errores
        """
        if not student.is_student:
            raise ValueError("El usuario debe ser un estudiante")

        if Enrollment.objects.filter(
            student=student, subject=subject, is_active=True
        ).exists():
            raise ValueError("El estudiante ya está inscrito en esta materia")

        # Validar que la materia está activa
        if not subject.is_active:
            raise ValueError("La materia no está disponible")

        enrollment = Enrollment.objects.create(
            student=student, subject=subject, created_by=student
        )

        logger.info(f"Estudiante {student.username} inscrito en {subject.code}")

        # Registrar en auditoría
        from common.audit_services import AuditService

        AuditService.log_enrollment(student, subject)

        # Enviar notificación
        # from notifications.services import NotificationService
        # NotificationService.create_notification(
        #     student, "Inscripción exitosa", f"Te has inscrito en {subject.name}"
        # )

        return enrollment

    @staticmethod
    @transaction.atomic
    def assign_grade(enrollment, grade, requesting_user):
        """
        Asigna nota a una inscripción con validaciones académicas.

        Args:
            enrollment: Inscripción a calificar
            grade: Nota a asignar
            requesting_user: Usuario que asigna la nota

        Returns:
            Enrollment: Inscripción actualizada

        Raises:
            PermissionError: Si no tiene permisos
            ValueError: Si la nota no es válida
        """
        from .academic_services import AcademicService

        # Usar el servicio académico para validaciones completas
        return AcademicService.assign_grade_with_validation(
            enrollment, grade, requesting_user
        )

    @staticmethod
    def get_student_subjects(student):
        """Obtiene todas las materias de un estudiante."""
        return Subject.objects.filter(
            enrollments__student=student, enrollments__is_active=True
        ).distinct()

    @staticmethod
    def get_teacher_subjects(teacher):
        """Obtiene todas las materias de un profesor."""
        return Subject.objects.filter(teacher=teacher, is_active=True)

    @staticmethod
    def list_subjects(requesting_user, semester=None, teacher_id=None):
        """
        Lista materias con filtros según permisos.

        Args:
            requesting_user: Usuario que hace la petición
            semester: Filtro opcional por semestre
            teacher_id: Filtro opcional por profesor

        Returns:
            QuerySet: Materias filtradas
        """
        # Base: solo materias activas
        queryset = Subject.objects.filter(is_active=True)

        # Si es estudiante, ver solo sus materias
        if requesting_user.is_student:
            queryset = queryset.filter(enrollments__student=requesting_user)

        # Si es profesor, ver sus materias
        elif requesting_user.is_teacher:
            queryset = queryset.filter(teacher=requesting_user)

        # Admin ve todas

        # Filtros adicionales
        if semester:
            queryset = queryset.filter(semester=semester)

        if teacher_id:
            queryset = queryset.filter(teacher_id=teacher_id)

        return queryset.distinct()

    @staticmethod
    def retrieve_subject(subject_id, requesting_user):
        """
        Obtiene una materia con validaciones.

        Args:
            subject_id: ID de la materia
            requesting_user: Usuario que hace la petición

        Returns:
            Subject: Materia encontrada

        Raises:
            ValueError: Si no existe o no tiene permisos
        """
        try:
            subject = Subject.objects.get(id=subject_id, is_active=True)

            # Validar acceso
            if requesting_user.is_student:
                # Estudiante solo ve materias en las que está inscrito
                if not subject.enrollments.filter(
                    student=requesting_user, is_active=True
                ).exists():
                    raise ValueError("No estás inscrito en esta materia")

            elif requesting_user.is_teacher:
                # Profesor solo ve sus materias
                if subject.teacher != requesting_user:
                    raise ValueError("No eres el profesor de esta materia")

            # Admin puede ver todas

            return subject

        except Subject.DoesNotExist:
            raise ValueError("Materia no encontrada")

    @staticmethod
    @transaction.atomic
    def create_subject(code, name, teacher, requesting_user, **extra_data):
        """
        Crea una nueva materia.

        Args:
            code: Código de la materia
            name: Nombre
            teacher: Profesor asignado
            requesting_user: Usuario que crea
            **extra_data: Datos adicionales

        Returns:
            Subject: Materia creada

        Raises:
            ValueError: Si hay errores
            PermissionError: Si no tiene permisos
        """
        # Solo admin puede crear materias
        if not requesting_user.is_staff:
            raise PermissionError("Solo administradores pueden crear materias")

        # Validar que el código no existe
        if Subject.objects.filter(code=code).exists():
            raise ValueError(f"Ya existe una materia con el código {code}")

        # Validar que el profesor es profesor
        if not teacher.is_teacher:
            raise ValueError("El usuario asignado debe ser un profesor")

        # Crear materia
        subject = Subject.objects.create(
            code=code,
            name=name,
            teacher=teacher,
            created_by=requesting_user,
            **extra_data,
        )

        logger.info(f"Materia creada: {code} - {name} por {requesting_user.username}")

        return subject

    @staticmethod
    @transaction.atomic
    def update_subject(subject, data, requesting_user):
        """
        Actualiza una materia.

        Args:
            subject: Materia a actualizar
            data: Nuevos datos
            requesting_user: Usuario que actualiza

        Returns:
            Subject: Materia actualizada

        Raises:
            PermissionError: Si no tiene permisos
        """
        # Solo admin o el profesor de la materia pueden actualizar
        if not requesting_user.is_staff and subject.teacher != requesting_user:
            raise PermissionError(
                "Solo el profesor de la materia o un administrador pueden modificarla"
            )

        # Actualizar campos
        for key, value in data.items():
            setattr(subject, key, value)

        subject.updated_by = requesting_user
        subject.save()

        logger.info(
            f"Materia {subject.code} actualizada por {requesting_user.username}"
        )

        return subject

    @staticmethod
    @transaction.atomic
    def delete_subject(subject, requesting_user):
        """
        Elimina (desactiva) una materia.

        Args:
            subject: Materia a eliminar
            requesting_user: Usuario que elimina

        Returns:
            Subject: Materia desactivada

        Raises:
            ValueError: Si tiene inscripciones activas
            PermissionError: Si no tiene permisos
        """
        # Solo admin puede eliminar
        if not requesting_user.is_staff:
            raise PermissionError("Solo administradores pueden eliminar materias")

        # Validar que no tiene inscripciones activas
        if subject.enrollments.filter(is_active=True).exists():
            raise ValueError(
                "No se puede eliminar: la materia tiene estudiantes inscritos actualmente"
            )

        # Soft delete
        subject.soft_delete()

        logger.warning(
            f"Materia {subject.code} eliminada por {requesting_user.username}"
        )

        return subject

    @staticmethod
    def unenroll_student(enrollment, requesting_user):
        """
        Des-inscribe un estudiante de una materia.

        Args:
            enrollment: Inscripción a eliminar
            requesting_user: Usuario que des-inscribe

        Returns:
            Enrollment: Inscripción desactivada

        Raises:
            PermissionError: Si no tiene permisos
            ValueError: Si ya tiene nota asignada
        """
        # El estudiante puede des-inscribirse o admin
        if enrollment.student != requesting_user and not requesting_user.is_staff:
            raise PermissionError(
                "No tienes permiso para des-inscribirte de esta materia"
            )

        # No permitir des-inscripción si ya tiene nota
        if enrollment.final_grade is not None:
            raise ValueError("No puedes des-inscribirte: ya tienes una nota asignada")

        # Soft delete
        enrollment.soft_delete()

        logger.info(
            f"Estudiante {enrollment.student.username} des-inscrito de {enrollment.subject.code}"
        )

        return enrollment
