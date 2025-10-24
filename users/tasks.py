"""
Tareas asíncronas para usuarios.
"""

# from celery import shared_task
import logging

logger = logging.getLogger(__name__)


# @shared_task
def send_welcome_email_task(user_id):
    """
    Envía email de bienvenida a un nuevo usuario.

    Args:
        user_id: ID del usuario
    """
    from .models import User
    from common.services import EmailService

    try:
        user = User.objects.get(id=user_id)

        subject = "Bienvenido a Alternova"
        message = f"Hola {user.first_name}, bienvenido a nuestra plataforma!"

        EmailService.send_notification_email(user.email, subject, message)
        logger.info(f"Email de bienvenida enviado a {user.email}")
        return True
    except User.DoesNotExist:
        logger.error(f"Usuario {user_id} no encontrado")
        return False
    except Exception as e:
        logger.error(f"Error enviando email de bienvenida: {str(e)}")
        return False


# @shared_task
def deactivate_inactive_users_task():
    """
    Desactiva usuarios que no han iniciado sesión en 6 meses.
    """
    from django.utils import timezone
    from datetime import timedelta
    from .models import User

    cutoff_date = timezone.now() - timedelta(days=180)

    inactive_users = User.objects.filter(last_login__lt=cutoff_date, is_active=True)

    count = inactive_users.update(is_active=False)
    logger.info(f"Desactivados {count} usuarios inactivos")
    return count
