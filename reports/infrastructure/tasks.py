"""Tareas asíncronas para reportes."""

import logging

logger = logging.getLogger(__name__)


# @shared_task
def generate_report_task(report_id):
    """Genera un reporte de forma asíncrona."""
    from .models import Report
    from .services import ReportService

    try:
        report = Report.objects.get(id=report_id)
        report.status = "processing"
        report.save()

        # Generar el reporte según el tipo
        if report.report_type == "grades":
            ReportService.generate_grades_report(report.filters)
        elif report.report_type == "enrollments":
            ReportService.generate_enrollments_report(report.filters)

        # Marcar como completado
        ReportService.mark_as_completed(report)
        logger.info(f"Reporte {report_id} generado exitosamente")
        return True
    except Exception as e:
        logger.error(f"Error generando reporte {report_id}: {str(e)}")
        ReportService.mark_as_failed(report, str(e))
        return False
