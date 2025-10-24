@echo off
REM Script para ejecutar Celery Beat en Windows
REM Ejecutar desde la raíz del proyecto

echo Iniciando Celery Beat (Scheduler)...
echo.
echo Para detener el scheduler, presiona Ctrl+C
echo.

celery -A config beat --loglevel=info --scheduler django_celery_beat.schedulers:DatabaseScheduler
