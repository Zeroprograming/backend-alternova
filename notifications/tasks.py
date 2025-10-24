"""
Tareas periódicas de Celery para notificaciones.
"""

import logging
from celery import shared_task
from django.utils import timezone
from datetime import timedelta, datetime
from django.contrib.auth import get_user_model
from django.core.mail import EmailMultiAlternatives
from django.conf import settings
from django.db import models
from .models import Notification
from subjects.models import Subject, Enrollment

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(bind=True)
def cleanup_old_notifications_task(self):
    """
    Limpia notificaciones antiguas leídas (más de 30 días).
    Tarea ejecutada semanalmente.
    """
    try:
        cutoff_date = timezone.now() - timedelta(days=30)

        # Eliminar notificaciones leídas más antiguas de 30 días
        deleted_count = Notification.objects.filter(
            is_read=True, read_at__lt=cutoff_date, is_active=True
        ).count()

        # Soft delete
        Notification.objects.filter(
            is_read=True, read_at__lt=cutoff_date, is_active=True
        ).update(is_active=False)

        logger.info(
            f"Limpieza de notificaciones: {deleted_count} notificaciones archivadas"
        )

        return {
            "status": "success",
            "message": f"Archivadas {deleted_count} notificaciones antiguas",
            "count": deleted_count,
        }

    except Exception as e:
        logger.error(f"Error en limpieza de notificaciones: {str(e)}")
        return {"status": "error", "message": f"Error: {str(e)}", "count": 0}


@shared_task(bind=True)
def send_weekly_teacher_summary_task(self):
    """
    Envía resumen semanal académico a todos los profesores.
    Tarea ejecutada semanalmente (lunes).
    """
    try:
        teachers = User.objects.filter(user_type="teacher", is_active=True)
        sent_count = 0

        for teacher in teachers:
            try:
                # Obtener materias activas del profesor
                active_subjects = Subject.objects.filter(
                    teacher=teacher, is_active=True, is_finished=False
                )

                if not active_subjects.exists():
                    continue

                # Preparar datos del resumen
                summary_data = []
                total_students = 0
                total_graded = 0

                for subject in active_subjects:
                    enrollments = Enrollment.objects.filter(
                        subject=subject, is_active=True
                    )

                    enrolled_count = enrollments.count()
                    graded_count = enrollments.filter(final_grade__isnull=False).count()

                    total_students += enrolled_count
                    total_graded += graded_count

                    summary_data.append(
                        {
                            "subject": subject.name,
                            "code": subject.code,
                            "enrolled": enrolled_count,
                            "graded": graded_count,
                            "pending": enrolled_count - graded_count,
                            "average": enrollments.filter(
                                final_grade__isnull=False
                            ).aggregate(avg=models.Avg("final_grade"))["avg"]
                            or 0,
                        }
                    )

                # Crear contenido del email
                subject_email = f"[Sistema Académico] Resumen Semanal - {teacher.get_full_name() or teacher.username}"

                html_content = _create_teacher_summary_html(
                    teacher, summary_data, total_students, total_graded
                )
                text_content = _create_teacher_summary_text(
                    teacher, summary_data, total_students, total_graded
                )

                # Enviar email
                msg = EmailMultiAlternatives(
                    subject=subject_email,
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[teacher.email],
                )
                msg.attach_alternative(html_content, "text/html")
                msg.send()

                sent_count += 1
                logger.info(f"Resumen semanal enviado a {teacher.email}")

            except Exception as e:
                logger.error(f"Error enviando resumen a {teacher.email}: {str(e)}")
                continue

        logger.info(f"Resumen semanal enviado a {sent_count} profesores")

        return {
            "status": "success",
            "message": f"Resumen enviado a {sent_count} profesores",
            "count": sent_count,
        }

    except Exception as e:
        logger.error(f"Error en envío de resumen semanal: {str(e)}")
        return {"status": "error", "message": f"Error: {str(e)}", "count": 0}


def _create_teacher_summary_html(teacher, summary_data, total_students, total_graded):
    """Crea el contenido HTML para el resumen del profesor."""
    from django.template import Template, Context

    html_template = """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="utf-8">
        <title>Resumen Semanal Académico</title>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 800px; margin: 0 auto; padding: 20px; }
            .header { background-color: #f8f9fa; padding: 20px; border-radius: 5px; margin-bottom: 20px; }
            .content { padding: 20px; background-color: #fff; border: 1px solid #ddd; border-radius: 5px; }
            .summary-stats { background-color: #e9ecef; padding: 15px; border-radius: 5px; margin-bottom: 20px; }
            .subject-table { width: 100%; border-collapse: collapse; margin-top: 15px; }
            .subject-table th, .subject-table td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            .subject-table th { background-color: #f2f2f2; }
            .footer { margin-top: 20px; padding: 10px; font-size: 12px; color: #666; text-align: center; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Sistema Académico - Resumen Semanal</h1>
                <p>Profesor: {{ teacher.get_full_name|default:teacher.username }}</p>
                <p>Fecha: {{ current_date|date:"d/m/Y" }}</p>
            </div>
            
            <div class="content">
                <h2>Resumen General</h2>
                <div class="summary-stats">
                    <p><strong>Total de estudiantes inscritos:</strong> {{ total_students }}</p>
                    <p><strong>Total de calificaciones asignadas:</strong> {{ total_graded }}</p>
                    <p><strong>Calificaciones pendientes:</strong> {{ total_students|add:"-"|add:total_graded }}</p>
                </div>
                
                <h2>Detalle por Materia</h2>
                <table class="subject-table">
                    <thead>
                        <tr>
                            <th>Materia</th>
                            <th>Código</th>
                            <th>Inscritos</th>
                            <th>Calificados</th>
                            <th>Pendientes</th>
                            <th>Promedio</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for data in summary_data %}
                        <tr>
                            <td>{{ data.subject }}</td>
                            <td>{{ data.code }}</td>
                            <td>{{ data.enrolled }}</td>
                            <td>{{ data.graded }}</td>
                            <td>{{ data.pending }}</td>
                            <td>{{ data.average|floatformat:2 }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                
                <h2>Recomendaciones</h2>
                <ul>
                    {% if total_students|add:"-"|add:total_graded > 0 %}
                    <li>Hay {{ total_students|add:"-"|add:total_graded }} calificaciones pendientes. Considere completarlas pronto.</li>
                    {% endif %}
                    {% for data in summary_data %}
                        {% if data.pending > 0 %}
                        <li>{{ data.subject }}: {{ data.pending }} calificaciones pendientes</li>
                        {% endif %}
                    {% endfor %}
                </ul>
            </div>
            
            <div class="footer">
                <p>Este es un reporte automático del Sistema Académico.</p>
                <p>Generado el {{ current_date|date:"d/m/Y H:i" }}</p>
            </div>
        </div>
    </body>
    </html>
    """

    context = {
        "teacher": teacher,
        "summary_data": summary_data,
        "total_students": total_students,
        "total_graded": total_graded,
        "current_date": timezone.now(),
    }

    template = Template(html_template)
    return template.render(Context(context))


def _create_teacher_summary_text(teacher, summary_data, total_students, total_graded):
    """Crea el contenido de texto plano para el resumen del profesor."""
    text_content = f"""
    RESUMEN SEMANAL ACADÉMICO
    =========================
    
    Profesor: {teacher.get_full_name() or teacher.username}
    Fecha: {timezone.now().strftime('%d/%m/%Y')}
    
    RESUMEN GENERAL:
    - Total de estudiantes inscritos: {total_students}
    - Total de calificaciones asignadas: {total_graded}
    - Calificaciones pendientes: {total_students - total_graded}
    
    DETALLE POR MATERIA:
    """

    for data in summary_data:
        text_content += f"""
    - {data['subject']} ({data['code']}):
      * Inscritos: {data['enrolled']}
      * Calificados: {data['graded']}
      * Pendientes: {data['pending']}
      * Promedio: {data['average']:.2f}
        """

    text_content += f"""
    
    RECOMENDACIONES:
    """

    if total_students - total_graded > 0:
        text_content += f"- Hay {total_students - total_graded} calificaciones pendientes. Considere completarlas pronto.\n"

    for data in summary_data:
        if data["pending"] > 0:
            text_content += (
                f"- {data['subject']}: {data['pending']} calificaciones pendientes\n"
            )

    text_content += f"""
    
    ---
    Sistema Académico
    Generado el {timezone.now().strftime('%d/%m/%Y %H:%M')}
    """

    return text_content
