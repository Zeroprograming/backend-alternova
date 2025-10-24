"""
Servicios para generación de reportes en formato CSV.
"""

import csv
import io
import logging
from django.http import HttpResponse
from django.contrib.auth import get_user_model
from django.db.models import Q
from subjects.models import Subject, Enrollment
from common.application.services.audit_services import AuditService
from datetime import datetime

User = get_user_model()
logger = logging.getLogger(__name__)


class CSVReportService:
    """Servicio para generar reportes en formato CSV."""

    @staticmethod
    def generate_student_report(student_id, requesting_user):
        """
        Genera un reporte CSV completo para un estudiante específico.

        Args:
            student_id: ID del estudiante
            requesting_user: Usuario que solicita el reporte

        Returns:
            HttpResponse: Respuesta HTTP con archivo CSV

        Raises:
            PermissionError: Si no tiene permisos
            ValueError: Si el estudiante no existe
        """
        # Validar permisos
        if not requesting_user.is_staff and requesting_user.id != student_id:
            raise PermissionError("No tienes permisos para generar este reporte")

        try:
            student = User.objects.get(
                id=student_id, user_type="student", is_active=True
            )
        except User.DoesNotExist:
            raise ValueError("Estudiante no encontrado")

        # Crear buffer para CSV
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="reporte_estudiante_{student.username}_{datetime.now().strftime("%Y%m%d")}.csv"'
        )

        # Crear writer CSV
        writer = csv.writer(response)

        # Escribir encabezados
        writer.writerow(["REPORTE ACADÉMICO - ESTUDIANTE"])
        writer.writerow([""])
        writer.writerow(["INFORMACIÓN GENERAL"])
        writer.writerow(["Nombre:", student.full_name])
        writer.writerow(["Username:", student.username])
        writer.writerow(["Email:", student.email])
        writer.writerow(["Año Académico:", student.academic_year])
        writer.writerow(
            ["Máximo Créditos por Semestre:", student.max_credits_per_semester]
        )
        writer.writerow(["Créditos Actuales:", student.current_semester_credits])
        writer.writerow(["Créditos Disponibles:", student.available_credits])
        writer.writerow(["Promedio Acumulado:", student.get_cumulative_average()])
        writer.writerow([""])

        # Obtener inscripciones del estudiante
        enrollments = (
            Enrollment.objects.filter(student=student, is_active=True)
            .select_related("subject")
            .order_by("-academic_year", "subject__code")
        )

        if enrollments.exists():
            writer.writerow(["HISTÓRICO ACADÉMICO"])
            writer.writerow(
                [
                    "Materia",
                    "Código",
                    "Créditos",
                    "Año Académico",
                    "Semestre",
                    "Nota Final",
                    "Estado",
                    "Fecha Inscripción",
                ]
            )

            for enrollment in enrollments:
                writer.writerow(
                    [
                        enrollment.subject.name,
                        enrollment.subject.code,
                        enrollment.subject.credits,
                        enrollment.academic_year,
                        enrollment.semester,
                        enrollment.final_grade or "Pendiente",
                        enrollment.status,
                        enrollment.enrolled_at.strftime("%Y-%m-%d %H:%M"),
                    ]
                )
        else:
            writer.writerow(["HISTÓRICO ACADÉMICO"])
            writer.writerow(["No hay inscripciones registradas"])

        writer.writerow([""])

        # Estadísticas adicionales
        approved_count = enrollments.filter(final_grade__gte=3.0).count()
        failed_count = enrollments.filter(final_grade__lt=3.0).count()
        pending_count = enrollments.filter(final_grade__isnull=True).count()

        writer.writerow(["ESTADÍSTICAS"])
        writer.writerow(["Materias Aprobadas:", approved_count])
        writer.writerow(["Materias Reprobadas:", failed_count])
        writer.writerow(["Materias en Curso:", pending_count])
        writer.writerow(["Total Materias:", enrollments.count()])

        # Log de auditoría
        AuditService.log_action(
            user=requesting_user,
            action_type="csv_report_generated",
            description=f"Reporte CSV generado para estudiante {student.username}",
            content_object=student,
            extra_data={
                "student_id": student_id,
                "report_type": "student_academic",
                "enrollments_count": enrollments.count(),
            },
        )

        logger.info(
            f"Reporte CSV generado para estudiante {student.username} por {requesting_user.username}"
        )

        return response

    @staticmethod
    def generate_teacher_report(teacher_id, requesting_user):
        """
        Genera un reporte CSV completo para un profesor específico.

        Args:
            teacher_id: ID del profesor
            requesting_user: Usuario que solicita el reporte

        Returns:
            HttpResponse: Respuesta HTTP con archivo CSV

        Raises:
            PermissionError: Si no tiene permisos
            ValueError: Si el profesor no existe
        """
        # Validar permisos
        if not requesting_user.is_staff and requesting_user.id != teacher_id:
            raise PermissionError("No tienes permisos para generar este reporte")

        try:
            teacher = User.objects.get(
                id=teacher_id, user_type="teacher", is_active=True
            )
        except User.DoesNotExist:
            raise ValueError("Profesor no encontrado")

        # Crear buffer para CSV
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="reporte_profesor_{teacher.username}_{datetime.now().strftime("%Y%m%d")}.csv"'
        )

        # Crear writer CSV
        writer = csv.writer(response)

        # Escribir encabezados
        writer.writerow(["REPORTE ACADÉMICO - PROFESOR"])
        writer.writerow([""])
        writer.writerow(["INFORMACIÓN GENERAL"])
        writer.writerow(["Nombre:", teacher.full_name])
        writer.writerow(["Username:", teacher.username])
        writer.writerow(["Email:", teacher.email])
        writer.writerow(["Año Académico:", teacher.academic_year])
        writer.writerow([""])

        # Obtener materias del profesor
        subjects = Subject.objects.filter(teacher=teacher, is_active=True).order_by(
            "-academic_year", "code"
        )

        if subjects.exists():
            writer.writerow(["MATERIAS ASIGNADAS"])
            writer.writerow(
                [
                    "Materia",
                    "Código",
                    "Créditos",
                    "Semestre",
                    "Estado",
                    "Máx. Estudiantes",
                    "Estudiantes Inscritos",
                ]
            )

            for subject in subjects:
                enrolled_count = Enrollment.objects.filter(
                    subject=subject, is_active=True
                ).count()

                writer.writerow(
                    [
                        subject.name,
                        subject.code,
                        subject.credits,
                        subject.semester,
                        "Finalizada" if subject.is_finished else "En curso",
                        subject.max_students,
                        enrolled_count,
                    ]
                )
        else:
            writer.writerow(["MATERIAS ASIGNADAS"])
            writer.writerow(["No hay materias asignadas"])

        writer.writerow([""])

        # Detalle de estudiantes por materia
        writer.writerow(["DETALLE DE ESTUDIANTES POR MATERIA"])
        writer.writerow(
            [
                "Materia",
                "Código",
                "Estudiante",
                "Email",
                "Nota Final",
                "Estado",
                "Fecha Inscripción",
            ]
        )

        for subject in subjects:
            enrollments = (
                Enrollment.objects.filter(subject=subject, is_active=True)
                .select_related("student")
                .order_by("student__last_name", "student__first_name")
            )

            for enrollment in enrollments:
                writer.writerow(
                    [
                        subject.name,
                        subject.code,
                        enrollment.student.full_name,
                        enrollment.student.email,
                        enrollment.final_grade or "Pendiente",
                        enrollment.status,
                        enrollment.enrolled_at.strftime("%Y-%m-%d %H:%M"),
                    ]
                )

        writer.writerow([""])

        # Estadísticas del profesor
        total_students = Enrollment.objects.filter(
            subject__teacher=teacher, is_active=True
        ).count()

        graded_students = Enrollment.objects.filter(
            subject__teacher=teacher, is_active=True, final_grade__isnull=False
        ).count()

        pending_grades = total_students - graded_students

        writer.writerow(["ESTADÍSTICAS DEL PROFESOR"])
        writer.writerow(["Total Materias:", subjects.count()])
        writer.writerow(["Total Estudiantes:", total_students])
        writer.writerow(["Estudiantes Calificados:", graded_students])
        writer.writerow(["Calificaciones Pendientes:", pending_grades])

        # Log de auditoría
        AuditService.log_action(
            user=requesting_user,
            action_type="csv_report_generated",
            description=f"Reporte CSV generado para profesor {teacher.username}",
            content_object=teacher,
            extra_data={
                "teacher_id": teacher_id,
                "report_type": "teacher_academic",
                "subjects_count": subjects.count(),
                "total_students": total_students,
            },
        )

        logger.info(
            f"Reporte CSV generado para profesor {teacher.username} por {requesting_user.username}"
        )

        return response

    @staticmethod
    def generate_general_report(requesting_user):
        """
        Genera un reporte CSV general del sistema (solo administradores).

        Args:
            requesting_user: Usuario que solicita el reporte

        Returns:
            HttpResponse: Respuesta HTTP con archivo CSV

        Raises:
            PermissionError: Si no es administrador
        """
        # Solo administradores pueden generar reportes generales
        if not requesting_user.is_staff:
            raise PermissionError(
                "Solo administradores pueden generar reportes generales"
            )

        # Crear buffer para CSV
        response = HttpResponse(content_type="text/csv")
        response["Content-Disposition"] = (
            f'attachment; filename="reporte_general_{datetime.now().strftime("%Y%m%d")}.csv"'
        )

        # Crear writer CSV
        writer = csv.writer(response)

        # Escribir encabezados
        writer.writerow(["REPORTE GENERAL DEL SISTEMA"])
        writer.writerow(["Fecha:", datetime.now().strftime("%Y-%m-%d %H:%M:%S")])
        writer.writerow(["Generado por:", requesting_user.full_name])
        writer.writerow([""])

        # Estadísticas de usuarios
        total_users = User.objects.filter(is_active=True).count()
        admin_count = User.objects.filter(user_type="admin", is_active=True).count()
        teacher_count = User.objects.filter(user_type="teacher", is_active=True).count()
        student_count = User.objects.filter(user_type="student", is_active=True).count()

        writer.writerow(["ESTADÍSTICAS DE USUARIOS"])
        writer.writerow(["Total Usuarios:", total_users])
        writer.writerow(["Administradores:", admin_count])
        writer.writerow(["Profesores:", teacher_count])
        writer.writerow(["Estudiantes:", student_count])
        writer.writerow([""])

        # Estadísticas de materias
        total_subjects = Subject.objects.filter(is_active=True).count()
        finished_subjects = Subject.objects.filter(
            is_active=True, is_finished=True
        ).count()
        active_subjects = total_subjects - finished_subjects

        writer.writerow(["ESTADÍSTICAS DE MATERIAS"])
        writer.writerow(["Total Materias:", total_subjects])
        writer.writerow(["Materias Finalizadas:", finished_subjects])
        writer.writerow(["Materias Activas:", active_subjects])
        writer.writerow([""])

        # Estadísticas de inscripciones
        total_enrollments = Enrollment.objects.filter(is_active=True).count()
        approved_enrollments = Enrollment.objects.filter(
            is_active=True, final_grade__gte=3.0
        ).count()
        failed_enrollments = Enrollment.objects.filter(
            is_active=True, final_grade__lt=3.0
        ).count()
        pending_enrollments = Enrollment.objects.filter(
            is_active=True, final_grade__isnull=True
        ).count()

        writer.writerow(["ESTADÍSTICAS DE INSCRIPCIONES"])
        writer.writerow(["Total Inscripciones:", total_enrollments])
        writer.writerow(["Inscripciones Aprobadas:", approved_enrollments])
        writer.writerow(["Inscripciones Reprobadas:", failed_enrollments])
        writer.writerow(["Inscripciones Pendientes:", pending_enrollments])
        writer.writerow([""])

        # Lista de materias con detalles
        writer.writerow(["DETALLE DE MATERIAS"])
        writer.writerow(
            [
                "Código",
                "Nombre",
                "Profesor",
                "Créditos",
                "Semestre",
                "Estado",
                "Estudiantes Inscritos",
            ]
        )

        subjects = (
            Subject.objects.filter(is_active=True)
            .select_related("teacher")
            .order_by("code")
        )
        for subject in subjects:
            enrolled_count = Enrollment.objects.filter(
                subject=subject, is_active=True
            ).count()
            writer.writerow(
                [
                    subject.code,
                    subject.name,
                    subject.teacher.full_name if subject.teacher else "Sin asignar",
                    subject.credits,
                    subject.semester,
                    "Finalizada" if subject.is_finished else "En curso",
                    enrolled_count,
                ]
            )

        # Log de auditoría
        AuditService.log_action(
            user=requesting_user,
            action_type="csv_report_generated",
            description="Reporte CSV general del sistema generado",
            extra_data={
                "report_type": "general_system",
                "total_users": total_users,
                "total_subjects": total_subjects,
                "total_enrollments": total_enrollments,
            },
        )

        logger.info(f"Reporte CSV general generado por {requesting_user.username}")

        return response
