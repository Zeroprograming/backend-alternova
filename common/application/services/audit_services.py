"""
Servicio para gestión de auditoría.
"""

from ...infrastructure.audit_models import AuditLog
from ...infrastructure.external.utils import get_client_ip
import logging

logger = logging.getLogger(__name__)


class AuditService:
    """Servicio para registro de auditoría."""

    @staticmethod
    def log_action(
        user,
        action_type,
        description,
        request=None,
        content_object=None,
        extra_data=None,
    ):
        """
        Registra una acción en el log de auditoría.

        Args:
            user: Usuario que realiza la acción
            action_type: Tipo de acción (login, create, update, etc.)
            description: Descripción de la acción
            request: Request de Django (opcional)
            content_object: Objeto afectado (opcional)
            extra_data: Datos adicionales (opcional)

        Returns:
            AuditLog: Registro creado
        """
        # Extraer información del request
        ip_address = None
        user_agent = ""

        if request:
            ip_address = get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")

        # Crear registro de auditoría
        audit_log = AuditLog.objects.create(
            user=user,
            action_type=action_type,
            description=description,
            ip_address=ip_address,
            user_agent=user_agent,
            content_object=content_object,
            extra_data=extra_data or {},
        )

        logger.info(
            f"Audit: {user.username if user else 'System'} - {action_type} - {description}"
        )

        return audit_log

    @staticmethod
    def log_login(user, request):
        """Registra un inicio de sesión."""
        return AuditService.log_action(
            user=user,
            action_type="login",
            description=f"Usuario {user.username} inició sesión",
            request=request,
        )

    @staticmethod
    def log_logout(user, request):
        """Registra un cierre de sesión."""
        return AuditService.log_action(
            user=user,
            action_type="logout",
            description=f"Usuario {user.username} cerró sesión",
            request=request,
        )

    @staticmethod
    def log_grade_change(teacher, enrollment, old_grade, new_grade, request=None):
        """Registra cambio de nota."""
        return AuditService.log_action(
            user=teacher,
            action_type="grade_assigned",
            description=f"Nota cambiada de {old_grade} a {new_grade} para {enrollment.student.username} en {enrollment.subject.code}",
            request=request,
            content_object=enrollment,
            extra_data={
                "old_grade": str(old_grade) if old_grade else None,
                "new_grade": str(new_grade),
                "student_id": enrollment.student.id,
                "subject_id": enrollment.subject.id,
            },
        )

    @staticmethod
    def log_enrollment(student, subject, request=None):
        """Registra inscripción."""
        return AuditService.log_action(
            user=student,
            action_type="enrollment",
            description=f"Estudiante {student.username} inscrito en {subject.code}",
            request=request,
            content_object=subject,
        )

    @staticmethod
    def log_deletion(user, object_deleted, description, request=None):
        """Registra eliminación."""
        return AuditService.log_action(
            user=user,
            action_type="delete",
            description=description,
            request=request,
            content_object=object_deleted,
        )

    @staticmethod
    def get_user_activity(user, limit=50):
        """Obtiene el historial de actividad de un usuario."""
        return AuditLog.objects.filter(user=user).order_by("-created_at")[:limit]

    @staticmethod
    def get_recent_logins(days=7):
        """Obtiene logins recientes."""
        from django.utils import timezone
        from datetime import timedelta

        cutoff = timezone.now() - timedelta(days=days)

        return AuditLog.objects.filter(
            action_type="login", created_at__gte=cutoff
        ).order_by("-created_at")
