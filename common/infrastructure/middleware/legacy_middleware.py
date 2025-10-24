"""
Middleware personalizados para la aplicación.
"""

import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse

logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware que registra todas las peticiones HTTP.
    """

    def process_request(self, request):
        request.start_time = time.time()
        logger.info(
            f"Request: {request.method} {request.path} "
            f"from {request.META.get('REMOTE_ADDR')}"
        )
        return None

    def process_response(self, request, response):
        if hasattr(request, "start_time"):
            duration = time.time() - request.start_time
            logger.info(
                f"Response: {request.method} {request.path} "
                f"Status: {response.status_code} "
                f"Duration: {duration:.2f}s"
            )
        return response


class AuditMiddleware(MiddlewareMixin):
    """
    Middleware que agrega información de auditoría a las peticiones.
    Registra el usuario que realiza cambios en los modelos.
    """

    def process_request(self, request):
        # Agregar el usuario actual al request para que esté disponible
        # en signals y otras partes del código
        if hasattr(request, "user") and request.user.is_authenticated:
            request._current_user = request.user
        return None


class CORSHeaderMiddleware(MiddlewareMixin):
    """
    Middleware personalizado para agregar headers CORS.
    """

    def process_response(self, request, response):
        response["Access-Control-Allow-Origin"] = "*"
        response["Access-Control-Allow-Methods"] = (
            "GET, POST, PUT, PATCH, DELETE, OPTIONS"
        )
        response["Access-Control-Allow-Headers"] = "Content-Type, Authorization"
        return response


class ExceptionHandlerMiddleware(MiddlewareMixin):
    """
    Middleware que captura excepciones no manejadas y devuelve respuestas JSON.
    """

    def process_exception(self, request, exception):
        logger.error(f"Unhandled exception: {str(exception)}", exc_info=True)

        return JsonResponse(
            {
                "error": "Error interno del servidor",
                "detail": str(exception) if settings.DEBUG else "Ha ocurrido un error",
            },
            status=500,
        )


class APIVersionMiddleware(MiddlewareMixin):
    """
    Middleware que agrega información de versión de la API a las respuestas.
    """

    def process_response(self, request, response):
        if request.path.startswith("/api/"):
            response["X-API-Version"] = "1.0.0"
        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware básico para rate limiting.
    Nota: Para producción, usar django-ratelimit o similar.
    """

    def process_request(self, request):
        from django.core.cache import cache

        # Solo aplicar a rutas de API
        if not request.path.startswith("/api/"):
            return None

        # Obtener IP del cliente
        ip = request.META.get("REMOTE_ADDR")
        cache_key = f"rate_limit_{ip}"

        # Verificar contador
        requests_count = cache.get(cache_key, 0)

        # Límite: 100 peticiones por minuto
        if requests_count >= 100:
            return JsonResponse(
                {"error": "Límite de peticiones excedido. Intenta en un minuto."},
                status=429,
            )

        # Incrementar contador (expira en 60 segundos)
        cache.set(cache_key, requests_count + 1, 60)

        return None
