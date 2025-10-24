"""
Decoradores personalizados reutilizables.
"""

from functools import wraps
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def log_execution(func):
    """
    Decorador que registra la ejecución de una función.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        logger.info(f"Ejecutando {func.__name__} con args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"{func.__name__} ejecutado exitosamente")
            return result
        except Exception as e:
            logger.error(f"Error en {func.__name__}: {str(e)}")
            raise

    return wrapper


def cache_response(timeout=60 * 15):
    """
    Decorador que cachea la respuesta de una vista por un tiempo determinado.

    Args:
        timeout: Tiempo en segundos (default: 15 minutos)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Crear una clave única basada en la URL y parámetros
            cache_key = f"{request.path}_{request.GET.urlencode()}"

            # Intentar obtener del cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                logger.info(f"Cache hit para {cache_key}")
                return cached_response

            # Si no está en cache, ejecutar la función
            response = func(self, request, *args, **kwargs)

            # Guardar en cache solo si la respuesta es exitosa
            if response.status_code == 200:
                cache.set(cache_key, response, timeout)
                logger.info(f"Respuesta cacheada para {cache_key}")

            return response

        return wrapper

    return decorator


def require_permission(permission_name):
    """
    Decorador que verifica si el usuario tiene un permiso específico.
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            if not request.user.has_perm(permission_name):
                return Response(
                    {"error": "No tienes permiso para realizar esta acción"},
                    status=status.HTTP_403_FORBIDDEN,
                )
            return func(self, request, *args, **kwargs)

        return wrapper

    return decorator


def validate_request_data(*required_fields):
    """
    Decorador que valida que los campos requeridos estén presentes en request.data.

    Usage:
        @validate_request_data('name', 'email')
        def post(self, request):
            ...
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            missing_fields = [
                field for field in required_fields if field not in request.data
            ]
            if missing_fields:
                return Response(
                    {
                        "error": f"Campos requeridos faltantes: {', '.join(missing_fields)}"
                    },
                    status=status.HTTP_400_BAD_REQUEST,
                )
            return func(self, request, *args, **kwargs)

        return wrapper

    return decorator


def handle_exceptions(func):
    """
    Decorador que maneja excepciones comunes y devuelve respuestas apropiadas.
    """

    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValueError as e:
            logger.error(f"ValueError en {func.__name__}: {str(e)}")
            return Response(
                {"error": "Datos inválidos", "detail": str(e)},
                status=status.HTTP_400_BAD_REQUEST,
            )
        except PermissionError as e:
            logger.error(f"PermissionError en {func.__name__}: {str(e)}")
            return Response(
                {"error": "Permiso denegado", "detail": str(e)},
                status=status.HTTP_403_FORBIDDEN,
            )
        except Exception as e:
            logger.error(f"Error inesperado en {func.__name__}: {str(e)}")
            return Response(
                {"error": "Error interno del servidor"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    return wrapper


def rate_limit(key_prefix, rate="100/hour"):
    """
    Decorador para limitar la tasa de peticiones.

    Args:
        key_prefix: Prefijo para la clave de cache
        rate: Tasa límite (ej: '100/hour', '10/minute')
    """

    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Extraer número y periodo del rate
            num_requests, period = rate.split("/")
            num_requests = int(num_requests)

            # Calcular timeout según el periodo
            timeout_map = {"second": 1, "minute": 60, "hour": 3600, "day": 86400}
            timeout = timeout_map.get(period, 3600)

            # Crear clave única para el usuario
            cache_key = f"rate_limit_{key_prefix}_{request.user.id}"

            # Obtener contador actual
            count = cache.get(cache_key, 0)

            if count >= num_requests:
                return Response(
                    {"error": "Límite de peticiones excedido. Intenta más tarde."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS,
                )

            # Incrementar contador
            cache.set(cache_key, count + 1, timeout)

            return func(self, request, *args, **kwargs)

        return wrapper

    return decorator
