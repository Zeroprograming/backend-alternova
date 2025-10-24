"""Tareas asíncronas para materias."""

import logging

logger = logging.getLogger(__name__)


# @shared_task
def send_enrollment_confirmation_task(enrollment_id):
    """Envía confirmación de inscripción."""
    from .models import Enrollment
    from common.services import EmailService

    try:
        enrollment = Enrollment.objects.get(id=enrollment_id)
        EmailService.send_notification_email(
            enrollment.student.email,
            "Inscripción confirmada",
            f"Te has inscrito en {enrollment.subject.name}",
        )
        logger.info(f"Email de confirmación enviado para inscripción {enrollment_id}")
        return True
    except Exception as e:
        logger.error(f"Error enviando confirmación: {str(e)}")
        return False
