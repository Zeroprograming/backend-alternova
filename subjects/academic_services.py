"""
Servicios académicos avanzados con reglas de negocio complejas.
"""

from django.db import transaction
from django.core.exceptions import ValidationError
from .models import Subject, Enrollment, Prerequisite
from users.models import User
from common.audit_services import AuditService
import logging

logger = logging.getLogger(__name__)


class AcademicService:
    """Servicio para reglas académicas complejas."""

    @staticmethod
    def can_student_enroll(student, subject):
        """
        Verifica si un estudiante puede inscribirse a una materia.

        Args:
            student: Usuario estudiante
            subject: Materia a inscribir

        Returns:
            tuple: (puede_inscribirse: bool, mensaje: str)
        """
        if not student.is_student:
            return False, "Solo estudiantes pueden inscribirse"

        # 1. Verificar créditos disponibles
        can_enroll, credit_msg = student.can_enroll_subject(subject)
        if not can_enroll:
            return False, credit_msg

        # 2. Verificar si ya está inscrito en el año académico actual
        existing_enrollment = Enrollment.objects.filter(
            student=student,
            subject=subject,
            academic_year=student.academic_year,
            is_active=True,
        ).exists()

        if existing_enrollment:
            return False, "Ya estás inscrito en esta materia este semestre"

        # 3. Verificar si ya aprobó la materia
        approved_enrollment = Enrollment.objects.filter(
            student=student, subject=subject, final_grade__gte=3.0, is_active=True
        ).exists()

        if approved_enrollment:
            return False, "Ya aprobaste esta materia anteriormente"

        # 4. Verificar prerrequisitos
        prerequisites = Prerequisite.objects.filter(subject=subject)
        for prereq in prerequisites:
            prerequisite_subject = prereq.prerequisite_subject

            # Verificar si aprobó el prerrequisito
            prerequisite_approved = Enrollment.objects.filter(
                student=student,
                subject=prerequisite_subject,
                final_grade__gte=3.0,
                is_active=True,
            ).exists()

            if not prerequisite_approved:
                return (
                    False,
                    f"Debes aprobar {prerequisite_subject.code} antes de inscribirte en {subject.code}",
                )

        # 5. Verificar límite de estudiantes
        current_enrollments = Enrollment.objects.filter(
            subject=subject, academic_year=student.academic_year, is_active=True
        ).count()

        if current_enrollments >= subject.max_students:
            return (
                False,
                f"La materia {subject.code} ya tiene el máximo de estudiantes ({subject.max_students})",
            )

        return True, "Puede inscribirse"

    @staticmethod
    @transaction.atomic
    def enroll_student_with_validation(student, subject, requesting_user):
        """
        Inscribe un estudiante con todas las validaciones académicas.

        Args:
            student: Estudiante a inscribir
            subject: Materia a inscribir
            requesting_user: Usuario que hace la petición

        Returns:
            Enrollment: Nueva inscripción

        Raises:
            ValueError: Si no puede inscribirse
            PermissionError: Si no tiene permisos
        """
        # Validar permisos
        if student != requesting_user and not requesting_user.is_staff:
            raise PermissionError("Solo puedes inscribirte a ti mismo")

        # Validar reglas académicas
        can_enroll, message = AcademicService.can_student_enroll(student, subject)
        if not can_enroll:
            raise ValueError(message)

        # Crear inscripción
        enrollment = Enrollment.objects.create(
            student=student,
            subject=subject,
            semester=subject.semester,
            academic_year=student.academic_year,
            created_by=requesting_user,
            updated_by=requesting_user,
        )

        # Actualizar créditos del estudiante
        student.current_semester_credits += subject.credits
        student.save()

        # Log de auditoría
        AuditService.log_enrollment(student, subject)

        logger.info(
            f"Estudiante {student.username} inscrito en {subject.code} "
            f"({subject.credits} créditos) por {requesting_user.username}"
        )

        return enrollment

    @staticmethod
    @transaction.atomic
    def assign_grade_with_validation(enrollment, grade, requesting_user):
        """
        Asigna una nota con validaciones académicas.

        Args:
            enrollment: Inscripción a calificar
            grade: Nota a asignar (0.0 - 5.0)
            requesting_user: Usuario que asigna la nota

        Returns:
            Enrollment: Inscripción actualizada

        Raises:
            ValueError: Si la nota no es válida
            PermissionError: Si no tiene permisos
        """
        # Validar permisos
        if (
            not requesting_user.is_staff
            and enrollment.subject.teacher != requesting_user
        ):
            raise PermissionError("Solo el profesor de la materia puede asignar notas")

        # Validar rango de nota
        if not (0.0 <= grade <= 5.0):
            raise ValueError("La nota debe estar entre 0.0 y 5.0")

        # Verificar que la materia no esté finalizada
        if enrollment.subject.is_finished:
            raise ValueError("No se pueden asignar notas a materias finalizadas")

        # Guardar nota anterior para auditoría
        old_grade = enrollment.final_grade

        # Asignar nueva nota
        enrollment.final_grade = grade
        enrollment.updated_by = requesting_user
        enrollment.save()

        # Agregar información para el signal de notificación
        enrollment._graded_by = requesting_user

        # Log de auditoría
        AuditService.log_grade_change(requesting_user, enrollment, old_grade, grade)

        logger.info(
            f"Nota {grade} asignada a {enrollment.student.username} "
            f"en {enrollment.subject.code} por {requesting_user.username}"
        )

        return enrollment

    @staticmethod
    def can_finish_subject(subject, requesting_user):
        """
        Verifica si un profesor puede finalizar una materia.

        Args:
            subject: Materia a finalizar
            requesting_user: Usuario que solicita finalizar

        Returns:
            tuple: (puede_finalizar: bool, mensaje: str)
        """
        # Solo el profesor de la materia o admin
        if not requesting_user.is_staff and subject.teacher != requesting_user:
            return False, "Solo el profesor de la materia puede finalizarla"

        # Verificar que todos los estudiantes estén calificados
        ungraded_enrollments = Enrollment.objects.filter(
            subject=subject,
            academic_year=(
                subject.academic_year if hasattr(subject, "academic_year") else "2024-1"
            ),
            is_active=True,
            final_grade__isnull=True,
        ).exists()

        if ungraded_enrollments:
            return False, "No se puede finalizar: hay estudiantes sin calificar"

        return True, "Puede finalizar la materia"

    @staticmethod
    @transaction.atomic
    def finish_subject(subject, requesting_user):
        """
        Finaliza una materia con todas las validaciones.

        Args:
            subject: Materia a finalizar
            requesting_user: Usuario que finaliza

        Returns:
            Subject: Materia finalizada

        Raises:
            ValueError: Si no puede finalizar
            PermissionError: Si no tiene permisos
        """
        can_finish, message = AcademicService.can_finish_subject(
            subject, requesting_user
        )
        if not can_finish:
            raise ValueError(message)

        # Marcar como finalizada
        subject.is_finished = True
        subject.updated_by = requesting_user
        subject.save()

        # Agregar información para el signal de notificación
        subject._finalized_by = requesting_user

        logger.info(f"Materia {subject.code} finalizada por {requesting_user.username}")

        return subject

    @staticmethod
    def get_student_academic_summary(student):
        """
        Obtiene resumen académico completo del estudiante.

        Args:
            student: Usuario estudiante

        Returns:
            dict: Resumen académico
        """
        if not student.is_student:
            return {"error": "Solo estudiantes tienen resumen académico"}

        enrollments = student.get_academic_history()

        # Estadísticas generales
        total_subjects = enrollments.count()
        approved_subjects = enrollments.filter(final_grade__gte=3.0).count()
        failed_subjects = enrollments.filter(final_grade__lt=3.0).count()
        current_subjects = enrollments.filter(final_grade__isnull=True).count()

        # Promedio acumulado
        cumulative_average = student.get_cumulative_average()

        # Créditos
        total_credits_approved = sum(
            e.subject.credits for e in enrollments.filter(final_grade__gte=3.0)
        )
        current_semester_credits = student.current_semester_credits

        return {
            "student": {
                "id": student.id,
                "name": student.full_name,
                "username": student.username,
                "academic_year": student.academic_year,
            },
            "statistics": {
                "total_subjects": total_subjects,
                "approved_subjects": approved_subjects,
                "failed_subjects": failed_subjects,
                "current_subjects": current_subjects,
                "cumulative_average": cumulative_average,
                "total_credits_approved": total_credits_approved,
                "current_semester_credits": current_semester_credits,
                "max_credits_per_semester": student.max_credits_per_semester,
                "available_credits": student.available_credits,
            },
            "academic_history": [
                {
                    "subject_code": e.subject.code,
                    "subject_name": e.subject.name,
                    "credits": e.subject.credits,
                    "grade": float(e.final_grade) if e.final_grade else None,
                    "status": e.status,
                    "academic_year": e.academic_year,
                    "semester": e.semester,
                }
                for e in enrollments
            ],
        }

    @staticmethod
    def get_teacher_subjects_summary(teacher):
        """
        Obtiene resumen de materias del profesor.

        Args:
            teacher: Usuario profesor

        Returns:
            dict: Resumen de materias
        """
        if not teacher.is_teacher:
            return {"error": "Solo profesores tienen resumen de materias"}

        subjects = Subject.objects.filter(teacher=teacher, is_active=True)

        summary = {
            "teacher": {
                "id": teacher.id,
                "name": teacher.full_name,
                "username": teacher.username,
            },
            "subjects": [],
            "statistics": {
                "total_subjects": subjects.count(),
                "finished_subjects": subjects.filter(is_finished=True).count(),
                "active_subjects": subjects.filter(is_finished=False).count(),
            },
        }

        for subject in subjects:
            enrollments = Enrollment.objects.filter(subject=subject, is_active=True)

            subject_summary = {
                "subject_code": subject.code,
                "subject_name": subject.name,
                "credits": subject.credits,
                "semester": subject.semester,
                "is_finished": subject.is_finished,
                "total_students": enrollments.count(),
                "graded_students": enrollments.filter(
                    final_grade__isnull=False
                ).count(),
                "ungraded_students": enrollments.filter(
                    final_grade__isnull=True
                ).count(),
                "average_grade": None,
            }

            # Calcular promedio de la materia
            graded_enrollments = enrollments.filter(final_grade__isnull=False)
            if graded_enrollments.exists():
                avg_grade = (
                    sum(e.final_grade for e in graded_enrollments)
                    / graded_enrollments.count()
                )
                subject_summary["average_grade"] = round(float(avg_grade), 2)

            summary["subjects"].append(subject_summary)

        return summary
