"""
Servicios comunes reutilizables.
Lógica de negocio que puede ser utilizada por múltiples apps.
"""

from django.core.mail import send_mail
from django.conf import settings
from django.core.cache import cache
import logging

logger = logging.getLogger(__name__)


class EmailService:
    """
    Servicio para envío de correos electrónicos.
    """

    @staticmethod
    def send_notification_email(recipient, subject, message):
        """
        Envía un correo de notificación.

        Args:
            recipient: Email del destinatario
            subject: Asunto del correo
            message: Mensaje del correo
        """
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient],
                fail_silently=False,
            )
            logger.info(f"Email enviado exitosamente a {recipient}")
            return True
        except Exception as e:
            logger.error(f"Error enviando email a {recipient}: {str(e)}")
            return False

    @staticmethod
    def send_bulk_email(recipients, subject, message):
        """
        Envía correos en masa.

        Args:
            recipients: Lista de emails
            subject: Asunto del correo
            message: Mensaje del correo
        """
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=recipients,
                fail_silently=False,
            )
            logger.info(f"Emails enviados a {len(recipients)} destinatarios")
            return True
        except Exception as e:
            logger.error(f"Error enviando emails en masa: {str(e)}")
            return False


class CacheService:
    """
    Servicio para manejo de caché.
    """

    @staticmethod
    def get(key):
        """Obtiene un valor del caché"""
        return cache.get(key)

    @staticmethod
    def set(key, value, timeout=None):
        """Guarda un valor en el caché"""
        cache.set(key, value, timeout)
        logger.debug(f"Cache set: {key}")

    @staticmethod
    def delete(key):
        """Elimina un valor del caché"""
        cache.delete(key)
        logger.debug(f"Cache deleted: {key}")

    @staticmethod
    def clear_pattern(pattern):
        """
        Elimina todas las claves que coincidan con un patrón.
        Requiere redis como backend de cache.
        """
        try:
            keys = cache.keys(pattern)
            if keys:
                cache.delete_many(keys)
                logger.info(f"Cleared {len(keys)} cache keys matching {pattern}")
        except AttributeError:
            logger.warning("Cache backend no soporta búsqueda por patrón")


class FileService:
    """
    Servicio para manejo de archivos.
    """

    @staticmethod
    def validate_file_size(file, max_size_mb=5):
        """
        Valida el tamaño de un archivo.

        Args:
            file: Archivo a validar
            max_size_mb: Tamaño máximo en MB

        Returns:
            tuple: (is_valid, error_message)
        """
        filesize = file.size
        max_size_bytes = max_size_mb * 1024 * 1024

        if filesize > max_size_bytes:
            return False, f"El archivo excede el tamaño máximo de {max_size_mb}MB"
        return True, None

    @staticmethod
    def get_file_extension(filename):
        """Obtiene la extensión de un archivo"""
        import os

        return os.path.splitext(filename)[1].lower()

    @staticmethod
    def generate_unique_filename(original_filename):
        """
        Genera un nombre único para un archivo.

        Args:
            original_filename: Nombre original del archivo

        Returns:
            str: Nombre único del archivo
        """
        import uuid
        import os

        ext = os.path.splitext(original_filename)[1]
        return f"{uuid.uuid4()}{ext}"


class PaginationService:
    """
    Servicio para manejo de paginación personalizada.
    """

    @staticmethod
    def paginate_queryset(queryset, page, page_size=10):
        """
        Pagina un queryset.

        Args:
            queryset: QuerySet a paginar
            page: Número de página (empieza en 1)
            page_size: Tamaño de página

        Returns:
            dict: Datos paginados con metadata
        """
        from django.core.paginator import Paginator, EmptyPage

        paginator = Paginator(queryset, page_size)

        try:
            page_obj = paginator.get_page(page)
        except EmptyPage:
            page_obj = paginator.get_page(1)

        return {
            "count": paginator.count,
            "total_pages": paginator.num_pages,
            "current_page": page_obj.number,
            "page_size": page_size,
            "next": page_obj.has_next(),
            "previous": page_obj.has_previous(),
            "results": list(page_obj.object_list.values()),
        }


class ValidationService:
    """
    Servicio para validaciones complejas.
    """

    @staticmethod
    def validate_business_rules(data, rules):
        """
        Valida reglas de negocio personalizadas.

        Args:
            data: Datos a validar
            rules: Lista de funciones de validación

        Returns:
            tuple: (is_valid, errors)
        """
        errors = []
        for rule in rules:
            try:
                rule(data)
            except ValueError as e:
                errors.append(str(e))

        return len(errors) == 0, errors
