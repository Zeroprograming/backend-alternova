"""
Servicios para notificaciones.
"""

import logging
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.db import transaction
from .models import Notification

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationService:
    """Servicio para gestionar notificaciones."""

    @staticmethod
    def create_notification(
        user, title, message, notification_type="info", send_email=True
    ):
        """
        Crea una notificación para un usuario.

        Args:
            user: Usuario destinatario
            title: Título de la notificación
            message: Mensaje de la notificación
            notification_type: Tipo de notificación (info, warning, success, error)
            send_email: Si enviar email o no
        """
        try:
            # Crear notificación en base de datos
            notification = Notification.objects.create(
                user=user,
                title=title,
                message=message,
                notification_type=notification_type,
            )

            # Enviar email si está habilitado
            if send_email and user.email:
                NotificationService.send_notification_email(notification)

            logger.info(f"Notificación creada para {user.username}: {title}")
            return notification

        except Exception as e:
            logger.error(f"Error creando notificación para {user.username}: {str(e)}")
            raise

    @staticmethod
    def send_notification_email(notification):
        """
        Envía una notificación por email.

        Args:
            notification: Instancia de Notification
        """
        try:
            subject = f"[Sistema Académico] {notification.title}"

            # Crear contenido HTML del email
            html_content = NotificationService._create_email_html(notification)

            # Crear contenido texto plano
            text_content = f"""
            {notification.title}
            
            {notification.message}
            
            Tipo: {notification.get_notification_type_display()}
            Fecha: {notification.created_at.strftime('%d/%m/%Y %H:%M')}
            
            ---
            Sistema Académico
            """

            # Enviar email
            msg = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[notification.user.email],
            )
            msg.attach_alternative(html_content, "text/html")
            msg.send()

            logger.info(
                f"Email enviado a {notification.user.email}: {notification.title}"
            )

        except Exception as e:
            logger.error(f"Error enviando email a {notification.user.email}: {str(e)}")
            # No lanzamos excepción para que la notificación se guarde aunque falle el email

    @staticmethod
    def _create_email_html(notification):
        """
        Crea el contenido HTML para el email.

        Args:
            notification: Instancia de Notification
        """
        context = {
            "notification": notification,
            "user": notification.user,
            "site_name": "Sistema Académico",
        }

        # Template HTML simple para el email
        html_template = """
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="utf-8">
            <title>{{ notification.title }}</title>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                .header { background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
                .content { padding: 20px; background-color: #fff; border: 1px solid #ddd; border-radius: 5px; }
                .footer { margin-top: 20px; padding: 10px; font-size: 12px; color: #666; text-align: center; }
                .type-{{ notification.notification_type }} { 
                    padding: 10px; 
                    border-radius: 5px; 
                    margin-bottom: 15px; 
                }
                .type-info { background-color: #d1ecf1; border-left: 4px solid #17a2b8; }
                .type-success { background-color: #d4edda; border-left: 4px solid #28a745; }
                .type-warning { background-color: #fff3cd; border-left: 4px solid #ffc107; }
                .type-error { background-color: #f8d7da; border-left: 4px solid #dc3545; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>{{ site_name }}</h1>
                </div>
                
                <div class="content">
                    <h2>{{ notification.title }}</h2>
                    
                    <div class="type-{{ notification.notification_type }}">
                        <strong>Tipo:</strong> {{ notification.get_notification_type_display() }}
                    </div>
                    
                    <div>
                        {{ notification.message|linebreaks }}
                    </div>
                    
                    <p><strong>Fecha:</strong> {{ notification.created_at|date:"d/m/Y H:i" }}</p>
                </div>
                
                <div class="footer">
                    <p>Este es un mensaje automático del {{ site_name }}.</p>
                    <p>Por favor, no responda a este email.</p>
                </div>
            </div>
        </body>
        </html>
        """

        from django.template import Template, Context

        template = Template(html_template)
        return template.render(Context(context))

    @staticmethod
    def send_user_created_notification(user, created_by):
        """
        Envía notificación cuando un usuario es creado por un admin.

        Args:
            user: Usuario creado
            created_by: Usuario que creó la cuenta
        """
        title = "¡Bienvenido al Sistema Académico!"
        message = f"""
        Hola {user.first_name or user.username},
        
        Tu cuenta ha sido creada exitosamente en el Sistema Académico.
        
        Detalles de tu cuenta:
        - Usuario: {user.username}
        - Email: {user.email}
        - Rol: {user.get_user_type_display()}
        - Creado por: {created_by.get_full_name() or created_by.username}
        
        Puedes acceder al sistema usando tus credenciales.
        
        Si tienes alguna pregunta, no dudes en contactar al administrador.
        
        ¡Bienvenido!
        """

        return NotificationService.create_notification(
            user=user,
            title=title,
            message=message,
            notification_type="success",
            send_email=True,
        )

    @staticmethod
    def send_grade_notification(enrollment, grade, graded_by):
        """
        Envía notificación cuando un estudiante es calificado.

        Args:
            enrollment: Inscripción calificada
            grade: Calificación asignada
            graded_by: Profesor que calificó
        """
        student = enrollment.student
        subject = enrollment.subject

        # Determinar el tipo de notificación según la calificación
        if grade >= 3.0:
            notification_type = "success"
            status = "APROBADA"
        else:
            notification_type = "warning"
            status = "REPROBADA"

        title = f"Calificación asignada - {subject.name}"
        message = f"""
        Hola {student.first_name or student.username},
        
        Se ha asignado una calificación a tu inscripción en la materia "{subject.name}".
        
        Detalles:
        - Materia: {subject.name} ({subject.code})
        - Calificación: {grade}/5.0
        - Estado: {status}
        - Profesor: {graded_by.get_full_name() or graded_by.username}
        - Fecha: {timezone.now().strftime('%d/%m/%Y %H:%M')}
        
        {"¡Felicitaciones por aprobar la materia!" if grade >= 3.0 else "No te desanimes, puedes volver a intentar en el próximo semestre."}
        
        Puedes consultar tu historial académico completo en el sistema.
        """

        return NotificationService.create_notification(
            user=student,
            title=title,
            message=message,
            notification_type=notification_type,
            send_email=True,
        )

    @staticmethod
    def send_enrollment_notification(enrollment):
        """
        Envía notificación cuando un estudiante se inscribe en una materia.

        Args:
            enrollment: Inscripción creada
        """
        student = enrollment.student
        subject = enrollment.subject

        title = f"Inscripción exitosa - {subject.name}"
        message = f"""
        Hola {student.first_name or student.username},
        
        Te has inscrito exitosamente en la materia "{subject.name}".
        
        Detalles de la inscripción:
        - Materia: {subject.name} ({subject.code})
        - Créditos: {subject.credits}
        - Profesor: {subject.teacher.get_full_name() if subject.teacher else 'Por asignar'}
        - Semestre: {enrollment.semester}
        - Año académico: {enrollment.academic_year}
        
        Recuerda revisar los horarios y asistir a las clases.
        
        ¡Éxito en tu materia!
        """

        return NotificationService.create_notification(
            user=student,
            title=title,
            message=message,
            notification_type="info",
            send_email=True,
        )

    @staticmethod
    def send_subject_finalized_notification(subject, finalized_by):
        """
        Envía notificación cuando una materia es finalizada.

        Args:
            subject: Materia finalizada
            finalized_by: Profesor que finalizó la materia
        """
        # Notificar a todos los estudiantes inscritos
        enrollments = subject.enrollment_set.filter(is_active=True)

        for enrollment in enrollments:
            student = enrollment.student

            title = f"Materia finalizada - {subject.name}"
            message = f"""
            Hola {student.first_name or student.username},
            
            La materia "{subject.name}" ha sido finalizada por el profesor.
            
            Detalles:
            - Materia: {subject.name} ({subject.code})
            - Profesor: {finalized_by.get_full_name() or finalized_by.username}
            - Fecha de finalización: {timezone.now().strftime('%d/%m/%Y %H:%M')}
            
            Todas las calificaciones han sido asignadas. Puedes consultar tu calificación final en el sistema.
            
            ¡Gracias por participar en esta materia!
            """

            NotificationService.create_notification(
                user=student,
                title=title,
                message=message,
                notification_type="info",
                send_email=True,
            )

    @staticmethod
    def mark_notification_as_read(notification_id, user):
        """
        Marca una notificación como leída.

        Args:
            notification_id: ID de la notificación
            user: Usuario que marca como leída
        """
        try:
            notification = Notification.objects.get(id=notification_id, user=user)
            notification.mark_as_read()
            logger.info(
                f"Notificación {notification_id} marcada como leída por {user.username}"
            )
            return notification
        except Notification.DoesNotExist:
            logger.warning(
                f"Notificación {notification_id} no encontrada para {user.username}"
            )
            raise

    @staticmethod
    def mark_all_notifications_as_read(user):
        """
        Marca todas las notificaciones de un usuario como leídas.

        Args:
            user: Usuario
        """
        try:
            notifications = Notification.objects.filter(user=user, is_read=False)
            count = notifications.count()

            for notification in notifications:
                notification.mark_as_read()

            logger.info(
                f"{count} notificaciones marcadas como leídas para {user.username}"
            )
            return count
        except Exception as e:
            logger.error(
                f"Error marcando notificaciones como leídas para {user.username}: {str(e)}"
            )
            raise

    @staticmethod
    def get_user_notifications(user, unread_only=False, limit=None):
        """
        Obtiene las notificaciones de un usuario.

        Args:
            user: Usuario
            unread_only: Solo notificaciones no leídas
            limit: Límite de resultados
        """
        queryset = Notification.objects.filter(user=user, is_active=True)

        if unread_only:
            queryset = queryset.filter(is_read=False)

        queryset = queryset.order_by("-created_at")

        if limit:
            queryset = queryset[:limit]

        return queryset

    @staticmethod
    def get_unread_count(user):
        """
        Obtiene el conteo de notificaciones no leídas de un usuario.

        Args:
            user: Usuario
        """
        return Notification.objects.filter(
            user=user, is_active=True, is_read=False
        ).count()

    # Métodos existentes para compatibilidad
    @staticmethod
    def list_notifications(requesting_user, is_read=None):
        """
        Lista notificaciones del usuario.

        Args:
            requesting_user: Usuario que hace la petición
            is_read: Filtro opcional por leídas/no leídas

        Returns:
            QuerySet: Notificaciones filtradas
        """
        queryset = Notification.objects.filter(user=requesting_user, is_active=True)

        if is_read is not None:
            queryset = queryset.filter(is_read=is_read)

        return queryset.order_by("-created_at")

    @staticmethod
    def retrieve_notification(notification_id, requesting_user):
        """
        Obtiene una notificación con validaciones.

        Args:
            notification_id: ID de la notificación
            requesting_user: Usuario que hace la petición

        Returns:
            Notification: Notificación encontrada

        Raises:
            ValueError: Si no existe
            PermissionError: Si no tiene acceso
        """
        try:
            notification = Notification.objects.get(id=notification_id, is_active=True)

            # Solo el dueño puede ver la notificación
            if notification.user != requesting_user:
                raise PermissionError("No puedes ver notificaciones de otros usuarios")

            return notification

        except Notification.DoesNotExist:
            raise ValueError("Notificación no encontrada")

    @staticmethod
    @transaction.atomic
    def delete_notification(notification, requesting_user):
        """
        Elimina una notificación.

        Args:
            notification: Notificación a eliminar
            requesting_user: Usuario que elimina

        Returns:
            Notification: Notificación eliminada

        Raises:
            PermissionError: Si no tiene permisos
        """
        # Solo el dueño puede eliminar
        if notification.user != requesting_user:
            raise PermissionError("No puedes eliminar notificaciones de otros usuarios")

        notification.soft_delete()

        logger.info(
            f"Notificación {notification.id} eliminada por {requesting_user.username}"
        )

        return notification

    @staticmethod
    def mark_all_as_read(user):
        """Marca todas las notificaciones de un usuario como leídas."""
        return NotificationService.mark_all_notifications_as_read(user)
