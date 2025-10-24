@echo off
REM Script para ejecutar Celery Worker en Windows
REM Ejecutar desde la raíz del proyecto

echo Iniciando Celery Worker...
echo.
echo Para detener el worker, presiona Ctrl+C
echo.

celery -A config worker --loglevel=info --pool=solo
