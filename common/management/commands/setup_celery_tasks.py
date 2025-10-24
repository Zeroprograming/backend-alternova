"""
Comando de Django para configurar tareas periódicas de Celery Beat.
"""

from django.core.management.base import BaseCommand
from django_celery_beat.models import PeriodicTask, CrontabSchedule
import json


class Command(BaseCommand):
    help = "Configura las tareas periódicas de Celery Beat"

    def handle(self, *args, **options):
        self.stdout.write("Configurando tareas periódicas...")

        # 1. Limpieza de notificaciones antiguas (semanal - domingos a las 2:00 AM)
        cleanup_schedule, created = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="2",
            day_of_week="0",  # Domingo
            day_of_month="*",
            month_of_year="*",
        )

        cleanup_task, created = PeriodicTask.objects.get_or_create(
            name="Limpieza de notificaciones antiguas",
            defaults={
                "crontab": cleanup_schedule,
                "task": "notifications.tasks.cleanup_old_notifications_task",
                "args": json.dumps([]),
                "kwargs": json.dumps({}),
                "enabled": True,
                "description": "Limpia notificaciones leídas más antiguas de 30 días",
            },
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Tarea creada: {cleanup_task.name}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"⚠ Tarea ya existe: {cleanup_task.name}")
            )

        # 2. Resumen semanal para profesores (lunes a las 8:00 AM)
        summary_schedule, created = CrontabSchedule.objects.get_or_create(
            minute="0",
            hour="8",
            day_of_week="1",  # Lunes
            day_of_month="*",
            month_of_year="*",
        )

        summary_task, created = PeriodicTask.objects.get_or_create(
            name="Resumen semanal para profesores",
            defaults={
                "crontab": summary_schedule,
                "task": "notifications.tasks.send_weekly_teacher_summary_task",
                "args": json.dumps([]),
                "kwargs": json.dumps({}),
                "enabled": True,
                "description": "Envía resumen semanal académico a todos los profesores",
            },
        )

        if created:
            self.stdout.write(
                self.style.SUCCESS(f"✓ Tarea creada: {summary_task.name}")
            )
        else:
            self.stdout.write(
                self.style.WARNING(f"⚠ Tarea ya existe: {summary_task.name}")
            )

        # Mostrar resumen
        total_tasks = PeriodicTask.objects.count()
        enabled_tasks = PeriodicTask.objects.filter(enabled=True).count()

        self.stdout.write("\n" + "=" * 50)
        self.stdout.write(
            self.style.SUCCESS(
                f"Configuración completada!\n"
                f"Total de tareas: {total_tasks}\n"
                f"Tareas habilitadas: {enabled_tasks}"
            )
        )
        self.stdout.write("=" * 50)

        self.stdout.write("\nTareas configuradas:")
        for task in PeriodicTask.objects.all():
            status = "✓" if task.enabled else "✗"
            schedule_info = ""
            if task.crontab:
                schedule_info = f" - {task.crontab}"
            self.stdout.write(f"  {status} {task.name}{schedule_info}")

        self.stdout.write(
            self.style.SUCCESS(
                "\nPara ejecutar las tareas periódicas, ejecuta:\n"
                "celery -A config beat --loglevel=info"
            )
        )
