"""
Managers personalizados para optimización de consultas ORM.
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
from .querysets import (
    UserQuerySet,
    SubjectQuerySet,
    EnrollmentQuerySet,
    NotificationQuerySet,
    ReportQuerySet,
)


class UserManager(models.Manager):
    """Manager personalizado para usuarios con consultas optimizadas."""

    def get_queryset(self):
        return UserQuerySet(self.model, using=self._db)

    def active_users(self):
        """Usuarios activos con información básica."""
        return self.filter(is_active=True)

    def students_with_enrollments(self):
        """Estudiantes con sus inscripciones usando select_related."""
        return (
            self.filter(user_type="student", is_active=True)
            .select_related()
            .prefetch_related("enrollment_set__subject")
        )

    def teachers_with_subjects(self):
        """Profesores con sus materias asignadas."""
        return self.filter(user_type="teacher", is_active=True).prefetch_related(
            "subject_set"
        )

    def users_by_role(self, role):
        """Usuarios filtrados por rol con estadísticas."""
        return self.filter(user_type=role, is_active=True).annotate(
            total_enrollments=Count("enrollment", distinct=True),
            total_subjects=Count("subject", distinct=True),
        )

    def students_with_academic_stats(self):
        """Estudiantes con estadísticas académicas calculadas."""
        return self.filter(user_type="student", is_active=True).annotate(
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
        )

    def teachers_with_teaching_stats(self):
        """Profesores con estadísticas de enseñanza."""
        return self.filter(user_type="teacher", is_active=True).annotate(
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
        )


class SubjectManager(models.Manager):
    """Manager personalizado para materias con consultas optimizadas."""

    def get_queryset(self):
        return SubjectQuerySet(self.model, using=self._db)

    def active_subjects(self):
        """Materias activas con información del profesor."""
        return self.filter(is_active=True).select_related("teacher")

    def subjects_with_enrollments(self):
        """Materias con sus inscripciones usando prefetch_related."""
        return self.filter(is_active=True).prefetch_related(
            "enrollment_set__student", "prerequisite_set__prerequisite_subject"
        )

    def subjects_by_teacher(self, teacher):
        """Materias de un profesor específico con estadísticas."""
        return self.filter(teacher=teacher, is_active=True).annotate(
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
            average_grade=Avg("enrollment__final_grade"),
            completion_percentage=Case(
                When(enrolled_students=0, then=0),
                default=F("graded_students") * 100.0 / F("enrolled_students"),
                output_field=models.FloatField(),
            ),
        )

    def subjects_with_prerequisites(self):
        """Materias con sus prerrequisitos."""
        return self.filter(is_active=True).prefetch_related(
            "prerequisite_set__prerequisite_subject"
        )

    def available_for_enrollment(self, student):
        """Materias disponibles para inscripción de un estudiante."""
        from subjects.models import Enrollment, Prerequisite

        # Subquery para verificar si el estudiante ya está inscrito
        enrolled_subjects = Subquery(
            Enrollment.objects.filter(student=student, is_active=True).values(
                "subject_id"
            )
        )

        # Subquery para verificar prerrequisitos aprobados
        prerequisite_subjects = Subquery(
            Prerequisite.objects.filter(subject=OuterRef("pk")).values(
                "prerequisite_subject_id"
            )
        )

        approved_prerequisites = Exists(
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
                prerequisites_met=approved_prerequisites,
            )
            .filter(Q(has_prerequisites=False) | Q(prerequisites_met=True))
        )


class EnrollmentManager(models.Manager):
    """Manager personalizado para inscripciones con consultas optimizadas."""

    def get_queryset(self):
        return EnrollmentQuerySet(self.model, using=self._db)

    def active_enrollments(self):
        """Inscripciones activas con información relacionada."""
        return self.filter(is_active=True).select_related(
            "student", "subject", "subject__teacher"
        )

    def enrollments_with_grades(self):
        """Inscripciones con calificaciones y estadísticas."""
        return self.filter(is_active=True).annotate(
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
        )

    def enrollments_by_student(self, student):
        """Inscripciones de un estudiante con información completa."""
        return (
            self.filter(student=student, is_active=True)
            .select_related("subject", "subject__teacher")
            .annotate(
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
            )
        )

    def enrollments_by_subject(self, subject):
        """Inscripciones de una materia con información de estudiantes."""
        return (
            self.filter(subject=subject, is_active=True)
            .select_related("student")
            .annotate(
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
            )
        )

    def academic_statistics(self):
        """Estadísticas académicas generales."""
        return self.filter(is_active=True).aggregate(
            total_enrollments=Count("id"),
            approved_enrollments=Count("id", filter=Q(final_grade__gte=3.0)),
            failed_enrollments=Count("id", filter=Q(final_grade__lt=3.0)),
            pending_enrollments=Count("id", filter=Q(final_grade__isnull=True)),
            average_grade=Avg("final_grade"),
            total_credits=Sum("subject__credits"),
        )


class NotificationManager(models.Manager):
    """Manager personalizado para notificaciones."""

    def get_queryset(self):
        return NotificationQuerySet(self.model, using=self._db)

    def unread_notifications(self, user):
        """Notificaciones no leídas de un usuario."""
        return self.filter(user=user, is_active=True, read_at__isnull=True).order_by(
            "-created_at"
        )

    def notifications_by_type(self, user, notification_type):
        """Notificaciones de un tipo específico."""
        return self.filter(
            user=user, notification_type=notification_type, is_active=True
        ).order_by("-created_at")

    def recent_notifications(self, user, days=7):
        """Notificaciones recientes de los últimos N días."""
        from django.utils import timezone
        from datetime import timedelta

        cutoff_date = timezone.now() - timedelta(days=days)
        return self.filter(
            user=user, is_active=True, created_at__gte=cutoff_date
        ).order_by("-created_at")


class ReportManager(models.Manager):
    """Manager personalizado para reportes."""

    def get_queryset(self):
        return ReportQuerySet(self.model, using=self._db)

    def reports_by_user(self, user):
        """Reportes generados por un usuario."""
        return self.filter(generated_by=user, is_active=True).order_by("-created_at")

    def reports_by_type(self, report_type):
        """Reportes filtrados por tipo."""
        return self.filter(report_type=report_type, is_active=True).order_by(
            "-created_at"
        )

    def pending_reports(self):
        """Reportes pendientes de procesamiento."""
        return self.filter(status="pending", is_active=True).order_by("created_at")

    def completed_reports(self):
        """Reportes completados."""
        return self.filter(status="completed", is_active=True).order_by("-created_at")
