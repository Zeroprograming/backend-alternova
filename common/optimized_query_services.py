"""
Servicios optimizados con prefetch_related para mejorar el rendimiento de consultas.
"""

from django.db import models
from django.db.models import Prefetch, Q, Count, Avg, Sum
from django.contrib.auth import get_user_model
from common.audit_services import AuditService
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


class OptimizedQueryService:
    """Servicio con consultas optimizadas usando prefetch_related."""

    @staticmethod
    def get_students_with_complete_academic_info():
        """
        Obtiene estudiantes con información académica completa usando prefetch_related.
        Optimiza las consultas para evitar N+1 queries.
        """
        from subjects.models import Enrollment, Subject

        # Prefetch optimizado para inscripciones con materias y profesores
        enrollments_prefetch = Prefetch(
            "enrollments",
            queryset=Enrollment.objects.filter(is_active=True)
            .select_related("subject", "subject__teacher")
            .order_by("-academic_year", "subject__code"),
        )

        return (
            User.objects.filter(user_type="student", is_active=True)
            .prefetch_related(enrollments_prefetch)
            .annotate(
                total_enrollments=Count(
                    "enrollments", filter=Q(enrollments__is_active=True)
                ),
                approved_enrollments=Count(
                    "enrollments",
                    filter=Q(
                        enrollments__is_active=True, enrollments__final_grade__gte=3.0
                    ),
                ),
                average_grade=Avg(
                    "enrollments__final_grade", filter=Q(enrollments__is_active=True)
                ),
                total_credits=Sum(
                    "enrollments__subject__credits",
                    filter=Q(enrollments__is_active=True),
                ),
            )
        )

    @staticmethod
    def get_teachers_with_complete_teaching_info():
        """
        Obtiene profesores con información completa de enseñanza usando prefetch_related.
        """
        from subjects.models import Subject, Enrollment

        # Prefetch optimizado para materias con inscripciones
        subjects_prefetch = Prefetch(
            "subject_set",
            queryset=Subject.objects.filter(is_active=True)
            .prefetch_related(
                Prefetch(
                    "enrollments",
                    queryset=Enrollment.objects.filter(is_active=True)
                    .select_related("student")
                    .order_by("student__last_name", "student__first_name"),
                )
            )
            .order_by("code"),
        )

        return (
            User.objects.filter(user_type="teacher", is_active=True)
            .prefetch_related(subjects_prefetch)
            .annotate(
                total_subjects=Count(
                    "subject_set", filter=Q(subject_set__is_active=True)
                ),
                active_subjects=Count(
                    "subject_set",
                    filter=Q(
                        subject_set__is_active=True, subject_set__is_finished=False
                    ),
                ),
                total_students=Count(
                    "subject_set__enrollments",
                    filter=Q(subject_set__enrollments__is_active=True),
                ),
                graded_students=Count(
                    "subject_set__enrollments",
                    filter=Q(
                        subject_set__enrollments__is_active=True,
                        subject_set__enrollments__final_grade__isnull=False,
                    ),
                ),
            )
        )

    @staticmethod
    def get_subjects_with_complete_info():
        """
        Obtiene materias con información completa usando prefetch_related.
        """
        from subjects.models import Enrollment, Prerequisite

        # Prefetch optimizado para inscripciones con estudiantes
        enrollments_prefetch = Prefetch(
            "enrollments",
            queryset=Enrollment.objects.filter(is_active=True)
            .select_related("student")
            .order_by("student__last_name", "student__first_name"),
        )

        # Prefetch optimizado para prerrequisitos
        prerequisites_prefetch = Prefetch(
            "prerequisite_set",
            queryset=Prerequisite.objects.filter(is_active=True).select_related(
                "prerequisite_subject"
            ),
        )

        return (
            Subject.objects.filter(is_active=True)
            .select_related("teacher")
            .prefetch_related(enrollments_prefetch, prerequisites_prefetch)
            .annotate(
                enrolled_students=Count(
                    "enrollments", filter=Q(enrollments__is_active=True)
                ),
                graded_students=Count(
                    "enrollments",
                    filter=Q(
                        enrollments__is_active=True,
                        enrollments__final_grade__isnull=False,
                    ),
                ),
                average_grade=Avg(
                    "enrollments__final_grade", filter=Q(enrollments__is_active=True)
                ),
                prerequisites_count=Count(
                    "prerequisite_set", filter=Q(prerequisite_set__is_active=True)
                ),
            )
        )

    @staticmethod
    def get_enrollments_with_complete_info():
        """
        Obtiene inscripciones con información completa usando prefetch_related.
        """
        from subjects.models import Enrollment

        return (
            Enrollment.objects.filter(is_active=True)
            .select_related("student", "subject", "subject__teacher")
            .annotate(
                is_approved=models.Case(
                    models.When(final_grade__gte=3.0, then=True),
                    default=False,
                    output_field=models.BooleanField(),
                ),
                grade_status=models.Case(
                    models.When(final_grade__isnull=True, then="Pendiente"),
                    models.When(final_grade__gte=3.0, then="Aprobada"),
                    default="Reprobada",
                    output_field=models.CharField(),
                ),
            )
            .order_by("-enrolled_at")
        )

    @staticmethod
    def get_notifications_with_user_info():
        """
        Obtiene notificaciones con información del usuario usando prefetch_related.
        """
        from notifications.models import Notification

        return (
            Notification.objects.filter(is_active=True)
            .select_related("user")
            .order_by("-created_at")
        )

    @staticmethod
    def get_reports_with_generator_info():
        """
        Obtiene reportes con información del generador usando prefetch_related.
        """
        from reports.models import Report

        return (
            Report.objects.filter(is_active=True)
            .select_related("generated_by")
            .order_by("-created_at")
        )

    @staticmethod
    def bulk_update_student_credits():
        """
        Actualización masiva de créditos de estudiantes usando consultas optimizadas.
        """
        from subjects.models import Enrollment

        # Obtener estudiantes con sus inscripciones activas usando prefetch_related
        students_with_enrollments = User.objects.filter(
            user_type="student", is_active=True
        ).prefetch_related(
            Prefetch(
                "enrollments",
                queryset=Enrollment.objects.filter(is_active=True).select_related(
                    "subject"
                ),
            )
        )

        updated_count = 0

        for student in students_with_enrollments:
            # Calcular créditos actuales del semestre
            current_credits = sum(
                enrollment.subject.credits
                for enrollment in student.enrollments.all()
                if enrollment.academic_year == student.academic_year
            )

            # Actualizar solo si hay diferencia
            if student.current_semester_credits != current_credits:
                student.current_semester_credits = current_credits
                student.save(update_fields=["current_semester_credits"])
                updated_count += 1

                # Log de auditoría
                AuditService.log_action(
                    user=student,
                    action_type="credits_updated",
                    description=f"Créditos del semestre actualizados automáticamente: {current_credits}",
                    extra_data={
                        "previous_credits": student.current_semester_credits,
                        "new_credits": current_credits,
                        "academic_year": student.academic_year,
                    },
                )

        logger.info(f"Actualizados créditos de {updated_count} estudiantes")
        return updated_count

    @staticmethod
    def bulk_calculate_subject_statistics():
        """
        Cálculo masivo de estadísticas de materias usando consultas optimizadas.
        """
        from subjects.models import Subject, Enrollment

        # Obtener materias con sus inscripciones usando prefetch_related
        subjects_with_enrollments = Subject.objects.filter(
            is_active=True
        ).prefetch_related(
            Prefetch(
                "enrollments",
                queryset=Enrollment.objects.filter(is_active=True).select_related(
                    "student"
                ),
            )
        )

        statistics = []

        for subject in subjects_with_enrollments:
            enrollments = subject.enrollments.all()

            if enrollments.exists():
                stats = {
                    "subject_id": subject.id,
                    "subject_code": subject.code,
                    "subject_name": subject.name,
                    "total_enrollments": enrollments.count(),
                    "graded_enrollments": enrollments.filter(
                        final_grade__isnull=False
                    ).count(),
                    "approved_enrollments": enrollments.filter(
                        final_grade__gte=3.0
                    ).count(),
                    "failed_enrollments": enrollments.filter(
                        final_grade__lt=3.0
                    ).count(),
                    "pending_enrollments": enrollments.filter(
                        final_grade__isnull=True
                    ).count(),
                    "average_grade": enrollments.aggregate(
                        avg=models.Avg("final_grade")
                    )["avg"]
                    or 0,
                    "completion_rate": (
                        enrollments.filter(final_grade__isnull=False).count()
                        * 100.0
                        / enrollments.count()
                        if enrollments.count() > 0
                        else 0
                    ),
                    "approval_rate": (
                        enrollments.filter(final_grade__gte=3.0).count()
                        * 100.0
                        / enrollments.count()
                        if enrollments.count() > 0
                        else 0
                    ),
                }
            else:
                stats = {
                    "subject_id": subject.id,
                    "subject_code": subject.code,
                    "subject_name": subject.name,
                    "total_enrollments": 0,
                    "graded_enrollments": 0,
                    "approved_enrollments": 0,
                    "failed_enrollments": 0,
                    "pending_enrollments": 0,
                    "average_grade": 0,
                    "completion_rate": 0,
                    "approval_rate": 0,
                }

            statistics.append(stats)

        logger.info(f"Calculadas estadísticas para {len(statistics)} materias")
        return statistics

    @staticmethod
    def get_optimized_dashboard_data():
        """
        Obtiene datos optimizados para el dashboard usando prefetch_related.
        """
        from subjects.models import Subject, Enrollment
        from notifications.models import Notification
        from reports.models import Report

        # Consultas optimizadas con prefetch_related
        students_stats = User.objects.filter(
            user_type="student", is_active=True
        ).aggregate(
            total_students=Count("id"),
            students_with_enrollments=Count(
                "id", filter=Q(enrollments__is_active=True)
            ),
        )

        teachers_stats = User.objects.filter(
            user_type="teacher", is_active=True
        ).aggregate(
            total_teachers=Count("id"),
            teachers_with_subjects=Count("id", filter=Q(subject_set__is_active=True)),
        )

        subjects_stats = Subject.objects.filter(is_active=True).aggregate(
            total_subjects=Count("id"),
            active_subjects=Count("id", filter=Q(is_finished=False)),
            finished_subjects=Count("id", filter=Q(is_finished=True)),
        )

        enrollments_stats = Enrollment.objects.filter(is_active=True).aggregate(
            total_enrollments=Count("id"),
            approved_enrollments=Count("id", filter=Q(final_grade__gte=3.0)),
            failed_enrollments=Count("id", filter=Q(final_grade__lt=3.0)),
            pending_enrollments=Count("id", filter=Q(final_grade__isnull=True)),
        )

        return {
            "students": students_stats,
            "teachers": teachers_stats,
            "subjects": subjects_stats,
            "enrollments": enrollments_stats,
            "system_stats": {
                "total_users": User.objects.filter(is_active=True).count(),
                "total_notifications": Notification.objects.filter(
                    is_active=True
                ).count(),
                "total_reports": Report.objects.filter(is_active=True).count(),
            },
        }
