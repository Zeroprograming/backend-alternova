"""
QuerySets personalizados con consultas ORM avanzadas.
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


class UserQuerySet(models.QuerySet):
    """QuerySet personalizado para usuarios con consultas avanzadas."""

    def with_academic_stats(self):
        """Usuarios con estadísticas académicas calculadas usando annotate."""
        return self.annotate(
            total_enrollments=Count("enrollment", distinct=True),
            approved_enrollments=Count(
                "enrollment", filter=Q(enrollment__final_grade__gte=3.0), distinct=True
            ),
            failed_enrollments=Count(
                "enrollment", filter=Q(enrollment__final_grade__lt=3.0), distinct=True
            ),
            pending_enrollments=Count(
                "enrollment",
                filter=Q(enrollment__final_grade__isnull=True),
                distinct=True,
            ),
            average_grade=Avg("enrollment__final_grade"),
            total_credits=Sum("enrollment__subject__credits"),
            approval_rate=Case(
                When(total_enrollments=0, then=0),
                default=F("approved_enrollments") * 100.0 / F("total_enrollments"),
                output_field=models.FloatField(),
            ),
        )

    def students_with_prerequisites_status(self, subject):
        """Estudiantes con estado de prerrequisitos para una materia específica."""
        from subjects.models import Prerequisite, Enrollment

        # Subquery para materias prerrequisito
        prerequisite_subjects = Subquery(
            Prerequisite.objects.filter(subject=subject).values(
                "prerequisite_subject_id"
            )
        )

        # Subquery para verificar si aprobó los prerrequisitos
        approved_prerequisites = Exists(
            Enrollment.objects.filter(
                student=OuterRef("pk"),
                subject__in=prerequisite_subjects,
                final_grade__gte=3.0,
                is_active=True,
            )
        )

        return self.filter(user_type="student").annotate(
            has_prerequisites=Exists(Prerequisite.objects.filter(subject=subject)),
            prerequisites_met=approved_prerequisites,
            can_enroll=Case(
                When(has_prerequisites=False, then=True),
                When(prerequisites_met=True, then=True),
                default=False,
                output_field=models.BooleanField(),
            ),
        )

    def teachers_with_teaching_performance(self):
        """Profesores con métricas de rendimiento de enseñanza."""
        return self.filter(user_type="teacher").annotate(
            total_subjects=Count("subject", distinct=True),
            active_subjects=Count(
                "subject", filter=Q(subject__is_finished=False), distinct=True
            ),
            finished_subjects=Count(
                "subject", filter=Q(subject__is_finished=True), distinct=True
            ),
            total_students=Count("subject__enrollment", distinct=True),
            graded_students=Count(
                "subject__enrollment",
                filter=Q(subject__enrollment__final_grade__isnull=False),
                distinct=True,
            ),
            average_class_grade=Avg("subject__enrollment__final_grade"),
            grading_completion_rate=Case(
                When(total_students=0, then=0),
                default=F("graded_students") * 100.0 / F("total_students"),
                output_field=models.FloatField(),
            ),
        )


class SubjectQuerySet(models.QuerySet):
    """QuerySet personalizado para materias con consultas avanzadas."""

    def with_enrollment_stats(self):
        """Materias con estadísticas de inscripciones usando annotate."""
        return self.annotate(
            enrolled_students=Count("enrollment", distinct=True),
            graded_students=Count(
                "enrollment",
                filter=Q(enrollment__final_grade__isnull=False),
                distinct=True,
            ),
            pending_grades=Count(
                "enrollment",
                filter=Q(enrollment__final_grade__isnull=True),
                distinct=True,
            ),
            approved_students=Count(
                "enrollment", filter=Q(enrollment__final_grade__gte=3.0), distinct=True
            ),
            failed_students=Count(
                "enrollment", filter=Q(enrollment__final_grade__lt=3.0), distinct=True
            ),
            average_grade=Avg("enrollment__final_grade"),
            approval_rate=Case(
                When(enrolled_students=0, then=0),
                default=F("approved_students") * 100.0 / F("enrolled_students"),
                output_field=models.FloatField(),
            ),
            completion_percentage=Case(
                When(enrolled_students=0, then=0),
                default=F("graded_students") * 100.0 / F("enrolled_students"),
                output_field=models.FloatField(),
            ),
        )

    def available_for_student(self, student):
        """Materias disponibles para inscripción de un estudiante específico."""
        from subjects.models import Prerequisite, Enrollment

        # Subquery para materias ya inscritas
        enrolled_subjects = Subquery(
            Enrollment.objects.filter(student=student, is_active=True).values(
                "subject_id"
            )
        )

        # Subquery para prerrequisitos
        prerequisite_subjects = Subquery(
            Prerequisite.objects.filter(subject=OuterRef("pk")).values(
                "prerequisite_subject_id"
            )
        )

        # Verificar si aprobó todos los prerrequisitos
        prerequisites_met = Exists(
            Enrollment.objects.filter(
                student=student,
                subject__in=prerequisite_subjects,
                final_grade__gte=3.0,
                is_active=True,
            )
        )

        return (
            self.filter(is_active=True, is_finished=False)
            .exclude(id__in=enrolled_subjects)
            .annotate(
                has_prerequisites=Exists(
                    Prerequisite.objects.filter(subject=OuterRef("pk"))
                ),
                prerequisites_met=prerequisites_met,
                can_enroll=Case(
                    When(has_prerequisites=False, then=True),
                    When(prerequisites_met=True, then=True),
                    default=False,
                    output_field=models.BooleanField(),
                ),
            )
            .filter(can_enroll=True)
        )

    def with_prerequisites_info(self):
        """Materias con información de prerrequisitos."""
        return self.annotate(
            prerequisites_count=Count("prerequisite", distinct=True),
            required_by_count=Count("required_for", distinct=True),
        )


class EnrollmentQuerySet(models.QuerySet):
    """QuerySet personalizado para inscripciones con consultas avanzadas."""

    def with_grade_analysis(self):
        """Inscripciones con análisis de calificaciones usando annotate."""
        return self.annotate(
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
            credits_earned=Case(
                When(final_grade__gte=3.0, then=F("subject__credits")),
                default=0,
                output_field=models.PositiveIntegerField(),
            ),
        )

    def academic_performance_by_student(self, student):
        """Rendimiento académico de un estudiante específico."""
        return self.filter(student=student).annotate(
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
            weighted_points=Case(
                When(final_grade__isnull=True, then=0),
                default=F("final_grade") * F("subject__credits"),
                output_field=models.FloatField(),
            ),
        )

    def academic_performance_by_subject(self, subject):
        """Rendimiento académico de una materia específica."""
        return self.filter(subject=subject).annotate(
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
        )


class NotificationQuerySet(models.QuerySet):
    """QuerySet personalizado para notificaciones."""

    def unread_count_by_user(self, user):
        """Conteo de notificaciones no leídas por usuario."""
        return self.filter(user=user, is_active=True, read_at__isnull=True).count()

    def recent_by_user(self, user, days=7):
        """Notificaciones recientes de un usuario."""
        from django.utils import timezone
        from datetime import timedelta

        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(
            user=user, is_active=True, created_at__gte=cutoff_date
        ).order_by("-created_at")


class ReportQuerySet(models.QuerySet):
    """QuerySet personalizado para reportes."""

    def by_status_with_stats(self):
        """Reportes agrupados por estado con estadísticas."""
        return self.annotate(
            processing_time=Case(
                When(completed_at__isnull=True, then=None),
                default=F("completed_at") - F("created_at"),
                output_field=models.DurationField(),
            )
        )

    def recent_reports(self, days=30):
        """Reportes recientes."""
        from django.utils import timezone
        from datetime import timedelta

        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(created_at__gte=cutoff_date, is_active=True).order_by(
            "-created_at"
        )
