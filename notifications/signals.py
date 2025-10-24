"""Signals para notificaciones automáticas."""

from django.db.models.signals import post_save, post_init
from django.dispatch import receiver
from django.contrib.auth import get_user_model
from .models import Notification
from .services import NotificationService
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


@receiver(post_save, sender=User)
def user_created_notification(sender, instance, created, **kwargs):
    """
    Signal cuando se crea un usuario.
    Envía notificación de bienvenida al usuario creado.
    """
    if created:
        try:
            # Solo enviar notificación si el usuario tiene email
            if instance.email:
                # Obtener el usuario que creó la cuenta (si está disponible)
                created_by = getattr(instance, "_created_by", None)
                if created_by:
                    NotificationService.send_user_created_notification(
                        instance, created_by
                    )
                else:
                    # Si no sabemos quién creó la cuenta, enviar notificación genérica
                    NotificationService.create_notification(
                        user=instance,
                        title="¡Bienvenido al Sistema Académico!",
                        message=f"""
                        Hola {instance.first_name or instance.username},
                        
                        Tu cuenta ha sido creada exitosamente en el Sistema Académico.
                        
                        Detalles de tu cuenta:
                        - Usuario: {instance.username}
                        - Email: {instance.email}
                        - Rol: {instance.get_user_type_display()}
                        
                        Puedes acceder al sistema usando tus credenciales.
                        
                        Si tienes alguna pregunta, no dudes en contactar al administrador.
                        
                        ¡Bienvenido!
                        """,
                        notification_type="success",
                        send_email=True,
                    )

                logger.info(f"Notificación de bienvenida enviada a {instance.username}")
        except Exception as e:
            logger.error(
                f"Error enviando notificación de bienvenida a {instance.username}: {str(e)}"
            )


@receiver(post_save, sender="subjects.Enrollment")
def enrollment_created_notification(sender, instance, created, **kwargs):
    """
    Signal cuando se crea una inscripción.
    Envía notificación al estudiante sobre su inscripción.
    """
    if created:
        try:
            NotificationService.send_enrollment_notification(instance)
            logger.info(
                f"Notificación de inscripción enviada a {instance.student.username}"
            )
        except Exception as e:
            logger.error(
                f"Error enviando notificación de inscripción a {instance.student.username}: {str(e)}"
            )


@receiver(post_save, sender="subjects.Enrollment")
def enrollment_grade_notification(sender, instance, created, **kwargs):
    """
    Signal cuando se asigna una calificación a una inscripción.
    Envía notificación al estudiante sobre su calificación.
    """
    if not created and instance.final_grade is not None:
        # Verificar si la calificación cambió
        if hasattr(instance, "_previous_grade"):
            previous_grade = instance._previous_grade
            if previous_grade != instance.final_grade:
                try:
                    # Obtener el profesor que calificó (si está disponible)
                    graded_by = getattr(
                        instance, "_graded_by", instance.subject.teacher
                    )
                    if graded_by:
                        NotificationService.send_grade_notification(
                            instance, instance.final_grade, graded_by
                        )
                        logger.info(
                            f"Notificación de calificación enviada a {instance.student.username}"
                        )
                except Exception as e:
                    logger.error(
                        f"Error enviando notificación de calificación a {instance.student.username}: {str(e)}"
                    )


@receiver(post_init, sender="subjects.Enrollment")
def enrollment_init(sender, instance, **kwargs):
    """
    Signal cuando se inicializa una inscripción.
    Guarda el valor anterior de la calificación para detectar cambios.
    """
    instance._previous_grade = instance.final_grade


@receiver(post_save, sender="subjects.Subject")
def subject_finalized_notification(sender, instance, created, **kwargs):
    """
    Signal cuando se finaliza una materia.
    Envía notificación a todos los estudiantes inscritos.
    """
    if not created and instance.is_finished:
        # Verificar si la materia cambió de estado
        if hasattr(instance, "_previous_is_finished"):
            previous_finished = instance._previous_is_finished
            if not previous_finished and instance.is_finished:
                try:
                    # Obtener el profesor que finalizó (si está disponible)
                    finalized_by = getattr(instance, "_finalized_by", instance.teacher)
                    if finalized_by:
                        NotificationService.send_subject_finalized_notification(
                            instance, finalized_by
                        )
                        logger.info(
                            f"Notificaciones de materia finalizada enviadas para {instance.name}"
                        )
                except Exception as e:
                    logger.error(
                        f"Error enviando notificaciones de materia finalizada para {instance.name}: {str(e)}"
                    )


@receiver(post_init, sender="subjects.Subject")
def subject_init(sender, instance, **kwargs):
    """
    Signal cuando se inicializa una materia.
    Guarda el valor anterior del estado de finalización.
    """
    instance._previous_is_finished = instance.is_finished


@receiver(post_save, sender=Notification)
def notification_created_log(sender, instance, created, **kwargs):
    """Signal cuando se crea una notificación."""
    if created:
        logger.info(
            f"Nueva notificación para {instance.user.username}: {instance.title}"
        )
