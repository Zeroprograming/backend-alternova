"""
Servicios con consultas ORM avanzadas usando Subquery, Exists y validaciones de negocio.
"""

from django.db import models
from django.db.models import (
    Q,
    Count,
    Avg,
    Sum,
    Exists,
    OuterRef,
    Subquery,
    Case,
    When,
    F,
)
from django.contrib.auth import get_user_model
from common.audit_services import AuditService
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class AdvancedORMService:
    """Servicio con consultas ORM avanzadas para validaciones de negocio."""

    @staticmethod
    def validate_student_enrollment_eligibility(student, subject):
        """
        Validación avanzada de elegibilidad de inscripción usando Subquery y Exists.

        Args:
            student: Usuario estudiante
            subject: Materia a inscribir

        Returns:
            tuple: (is_eligible, message, details)
        """
        from subjects.models import Enrollment, Prerequisite

        # 1. Verificar si ya está inscrito usando Exists
        already_enrolled = Exists(
            Enrollment.objects.filter(student=student, subject=subject, is_active=True)
        )

        if Enrollment.objects.filter(
            student=student, subject=subject, is_active=True
        ).exists():
            return (
                False,
                "Ya estás inscrito en esta materia",
                {
                    "already_enrolled": True,
                    "enrollment_date": Enrollment.objects.filter(
                        student=student, subject=subject, is_active=True
                    )
                    .first()
                    .enrolled_at,
                },
            )

        # 2. Verificar créditos disponibles usando annotate
        student_stats = (
            User.objects.filter(id=student.id)
            .annotate(
                current_credits=F("current_semester_credits"),
                max_credits=F("max_credits_per_semester"),
                available_credits=F("max_credits_per_semester")
                - F("current_semester_credits"),
            )
            .first()
        )

        if subject.credits > student_stats.available_credits:
            return (
                False,
                f"No tienes suficientes créditos disponibles",
                {
                    "required_credits": subject.credits,
                    "available_credits": student_stats.available_credits,
                    "current_credits": student_stats.current_credits,
                    "max_credits": student_stats.max_credits,
                },
            )

        # 3. Verificar prerrequisitos usando Subquery
        prerequisite_subjects = Subquery(
            Prerequisite.objects.filter(subject=subject).values(
                "prerequisite_subject_id"
            )
        )

        # Verificar si aprobó todos los prerrequisitos usando Exists
        prerequisites_met = Exists(
            Enrollment.objects.filter(
                student=student,
                subject__in=prerequisite_subjects,
                final_grade__gte=3.0,
                is_active=True,
            )
        )

        # Obtener prerrequisitos faltantes
        missing_prerequisites = (
            Prerequisite.objects.filter(subject=subject)
            .exclude(
                prerequisite_subject__in=Subquery(
                    Enrollment.objects.filter(
                        student=student, final_grade__gte=3.0, is_active=True
                    ).values("subject_id")
                )
            )
            .select_related("prerequisite_subject")
        )

        if missing_prerequisites.exists():
            missing_list = [
                {
                    "code": prereq.prerequisite_subject.code,
                    "name": prereq.prerequisite_subject.name,
                    "credits": prereq.prerequisite_subject.credits,
                }
                for prereq in missing_prerequisites
            ]
            return (
                False,
                "No cumples con los prerrequisitos requeridos",
                {
                    "missing_prerequisites": missing_list,
                    "prerequisites_count": missing_prerequisites.count(),
                },
            )

        # 4. Verificar capacidad de la materia usando annotate
        subject_stats = subject.enrollments.filter(is_active=True).aggregate(
            enrolled_count=Count("id"), available_spots=F("max_students") - Count("id")
        )

        if subject_stats["enrolled_count"] >= subject.max_students:
            return (
                False,
                "La materia ha alcanzado su capacidad máxima",
                {
                    "max_students": subject.max_students,
                    "enrolled_count": subject_stats["enrolled_count"],
                    "available_spots": 0,
                },
            )

        # 5. Verificar límite de materias por semestre usando Subquery
        current_semester_enrollments = Subquery(
            Enrollment.objects.filter(
                student=student, academic_year=student.academic_year, is_active=True
            ).values("subject_id")
        )

        current_subjects_count = Enrollment.objects.filter(
            student=student, academic_year=student.academic_year, is_active=True
        ).count()

        # Límite de materias por semestre (configurable)
        max_subjects_per_semester = 8  # Puede ser configurado

        if current_subjects_count >= max_subjects_per_semester:
            return (
                False,
                f"Has alcanzado el límite de materias por semestre",
                {
                    "current_subjects": current_subjects_count,
                    "max_subjects_per_semester": max_subjects_per_semester,
                },
            )

        return (
            True,
            "Elegible para inscripción",
            {
                "available_credits": student_stats.available_credits,
                "subject_credits": subject.credits,
                "available_spots": subject.max_students
                - subject_stats["enrolled_count"],
                "current_subjects": current_subjects_count,
                "prerequisites_met": True,
            },
        )

    @staticmethod
    def get_teacher_performance_metrics(teacher):
        """
        Métricas de rendimiento del profesor usando consultas ORM avanzadas.

        Args:
            teacher: Usuario profesor

        Returns:
            dict: Métricas de rendimiento
        """
        from subjects.models import Subject, Enrollment

        # Consulta avanzada con múltiples annotate
        performance_data = (
            Subject.objects.filter(teacher=teacher, is_active=True)
            .annotate(
                # Estadísticas por materia
                enrolled_students=Count("enrollment", distinct=True),
                graded_students=Count(
                    "enrollment",
                    filter=Q(enrollment__final_grade__isnull=False),
                    distinct=True,
                ),
                approved_students=Count(
                    "enrollment",
                    filter=Q(enrollment__final_grade__gte=3.0),
                    distinct=True,
                ),
                failed_students=Count(
                    "enrollment",
                    filter=Q(enrollment__final_grade__lt=3.0),
                    distinct=True,
                ),
                pending_grades=Count(
                    "enrollment",
                    filter=Q(enrollment__final_grade__isnull=True),
                    distinct=True,
                ),
                average_grade=Avg("enrollment__final_grade"),
                # Métricas calculadas
                approval_rate=Case(
                    When(enrolled_students=0, then=0),
                    default=F("approved_students") * 100.0 / F("enrolled_students"),
                    output_field=models.FloatField(),
                ),
                grading_completion_rate=Case(
                    When(enrolled_students=0, then=0),
                    default=F("graded_students") * 100.0 / F("enrolled_students"),
                    output_field=models.FloatField(),
                ),
                # Estado de la materia
                is_completed=Case(
                    When(enrolled_students=0, then=True),
                    When(pending_grades=0, then=True),
                    default=False,
                    output_field=models.BooleanField(),
                ),
            )
            .order_by("-average_grade")
        )

        # Estadísticas generales del profesor
        general_stats = performance_data.aggregate(
            total_subjects=Count("id"),
            active_subjects=Count("id", filter=Q(is_finished=False)),
            finished_subjects=Count("id", filter=Q(is_finished=True)),
            total_students=Sum("enrolled_students"),
            total_graded=Sum("graded_students"),
            total_approved=Sum("approved_students"),
            overall_average=Avg("average_grade"),
            overall_approval_rate=Avg("approval_rate"),
            overall_completion_rate=Avg("grading_completion_rate"),
        )

        return {
            "teacher_id": teacher.id,
            "teacher_name": teacher.full_name,
            "general_stats": general_stats,
            "subject_details": list(
                performance_data.values(
                    "id",
                    "code",
                    "name",
                    "enrolled_students",
                    "graded_students",
                    "approved_students",
                    "failed_students",
                    "pending_grades",
                    "average_grade",
                    "approval_rate",
                    "grading_completion_rate",
                    "is_completed",
                    "is_finished",
                )
            ),
        }

    @staticmethod
    def get_student_academic_progress(student):
        """
        Progreso académico del estudiante usando consultas ORM avanzadas.

        Args:
            student: Usuario estudiante

        Returns:
            dict: Progreso académico detallado
        """
        from subjects.models import Enrollment

        # Consulta avanzada con múltiples annotate y Subquery
        academic_progress = (
            Enrollment.objects.filter(student=student, is_active=True)
            .select_related("subject", "subject__teacher")
            .annotate(
                # Estado de la materia
                is_approved=Case(
                    When(final_grade__gte=3.0, then=True),
                    default=False,
                    output_field=models.BooleanField(),
                ),
                grade_status=Case(
                    When(final_grade__isnull=True, then="Pendiente"),
                    When(final_grade__gte=3.0, then="Aprobada"),
                    default="Reprobada",
                    output_field=models.CharField(),
                ),
                grade_category=Case(
                    When(final_grade__gte=4.5, then="Excelente"),
                    When(final_grade__gte=4.0, then="Muy Bueno"),
                    When(final_grade__gte=3.5, then="Bueno"),
                    When(final_grade__gte=3.0, then="Aprobado"),
                    When(final_grade__isnull=True, then="Sin Calificar"),
                    default="Reprobado",
                    output_field=models.CharField(),
                ),
                # Créditos ganados
                credits_earned=Case(
                    When(final_grade__gte=3.0, then=F("subject__credits")),
                    default=0,
                    output_field=models.PositiveIntegerField(),
                ),
                # Puntos ponderados
                weighted_points=Case(
                    When(final_grade__isnull=True, then=0),
                    default=F("final_grade") * F("subject__credits"),
                    output_field=models.FloatField(),
                ),
            )
            .order_by("-academic_year", "subject__code")
        )

        # Estadísticas por año académico usando Subquery
        yearly_stats = {}
        academic_years = (
            Enrollment.objects.filter(student=student, is_active=True)
            .values_list("academic_year", flat=True)
            .distinct()
        )

        for year in academic_years:
            year_enrollments = academic_progress.filter(academic_year=year)
            year_stats = year_enrollments.aggregate(
                total_subjects=Count("id"),
                approved_subjects=Count("id", filter=Q(is_approved=True)),
                failed_subjects=Count(
                    "id", filter=Q(is_approved=False, final_grade__isnull=False)
                ),
                pending_subjects=Count("id", filter=Q(final_grade__isnull=True)),
                total_credits=Sum("subject__credits"),
                earned_credits=Sum("credits_earned"),
                average_grade=Avg("final_grade"),
                weighted_sum=Sum("weighted_points"),
            )

            yearly_stats[year] = year_stats

        # Estadísticas generales
        general_stats = academic_progress.aggregate(
            total_enrollments=Count("id"),
            approved_enrollments=Count("id", filter=Q(is_approved=True)),
            failed_enrollments=Count(
                "id", filter=Q(is_approved=False, final_grade__isnull=False)
            ),
            pending_enrollments=Count("id", filter=Q(final_grade__isnull=True)),
            total_credits=Sum("subject__credits"),
            earned_credits=Sum("credits_earned"),
            cumulative_average=Avg("final_grade"),
            weighted_sum=Sum("weighted_points"),
        )

        # Calcular promedio acumulado ponderado
        if general_stats["total_credits"] and general_stats["total_credits"] > 0:
            cumulative_average = (
                general_stats["weighted_sum"] / general_stats["total_credits"]
            )
        else:
            cumulative_average = 0.0

        return {
            "student_id": student.id,
            "student_name": student.full_name,
            "general_stats": {
                **general_stats,
                "cumulative_average": round(cumulative_average, 2),
                "approval_rate": (
                    general_stats["approved_enrollments"]
                    * 100.0
                    / general_stats["total_enrollments"]
                    if general_stats["total_enrollments"] > 0
                    else 0
                ),
            },
            "yearly_stats": yearly_stats,
            "enrollment_details": list(
                academic_progress.values(
                    "id",
                    "subject__code",
                    "subject__name",
                    "subject__credits",
                    "academic_year",
                    "semester",
                    "final_grade",
                    "grade_status",
                    "grade_category",
                    "credits_earned",
                    "enrolled_at",
                )
            ),
        }

    @staticmethod
    def get_subject_enrollment_analytics(subject):
        """
        Análisis de inscripciones de una materia usando consultas ORM avanzadas.

        Args:
            subject: Materia a analizar

        Returns:
            dict: Análisis de inscripciones
        """
        from subjects.models import Enrollment

        # Consulta avanzada con múltiples annotate
        enrollment_analytics = (
            Enrollment.objects.filter(subject=subject, is_active=True)
            .select_related("student")
            .annotate(
                # Estado de la inscripción
                is_approved=Case(
                    When(final_grade__gte=3.0, then=True),
                    default=False,
                    output_field=models.BooleanField(),
                ),
                grade_status=Case(
                    When(final_grade__isnull=True, then="Pendiente"),
                    When(final_grade__gte=3.0, then="Aprobada"),
                    default="Reprobada",
                    output_field=models.CharField(),
                ),
                grade_category=Case(
                    When(final_grade__gte=4.5, then="Excelente"),
                    When(final_grade__gte=4.0, then="Muy Bueno"),
                    When(final_grade__gte=3.5, then="Bueno"),
                    When(final_grade__gte=3.0, then="Aprobado"),
                    When(final_grade__isnull=True, then="Sin Calificar"),
                    default="Reprobado",
                    output_field=models.CharField(),
                ),
                # Información del estudiante usando Subquery
                student_credits=Subquery(
                    User.objects.filter(id=OuterRef("student_id")).values(
                        "current_semester_credits"
                    )[:1]
                ),
                student_max_credits=Subquery(
                    User.objects.filter(id=OuterRef("student_id")).values(
                        "max_credits_per_semester"
                    )[:1]
                ),
            )
            .order_by("-final_grade", "student__last_name")
        )

        # Estadísticas generales
        general_stats = enrollment_analytics.aggregate(
            total_enrollments=Count("id"),
            graded_enrollments=Count("id", filter=Q(final_grade__isnull=False)),
            approved_enrollments=Count("id", filter=Q(is_approved=True)),
            failed_enrollments=Count(
                "id", filter=Q(is_approved=False, final_grade__isnull=False)
            ),
            pending_enrollments=Count("id", filter=Q(final_grade__isnull=True)),
            average_grade=Avg("final_grade"),
            highest_grade=models.Max("final_grade"),
            lowest_grade=models.Min("final_grade"),
        )

        # Distribución de calificaciones
        grade_distribution = (
            enrollment_analytics.values("grade_category")
            .annotate(count=Count("id"))
            .order_by("-count")
        )

        return {
            "subject_id": subject.id,
            "subject_code": subject.code,
            "subject_name": subject.name,
            "teacher_name": (
                subject.teacher.full_name if subject.teacher else "Sin asignar"
            ),
            "general_stats": general_stats,
            "grade_distribution": list(grade_distribution),
            "enrollment_details": list(
                enrollment_analytics.values(
                    "id",
                    "student__username",
                    "student__first_name",
                    "student__last_name",
                    "final_grade",
                    "grade_status",
                    "grade_category",
                    "enrolled_at",
                    "student_credits",
                    "student_max_credits",
                )
            ),
        }
