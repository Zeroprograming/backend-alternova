"""
Middleware avanzado para registro de usuarios, duración de requests y seguridad.
"""

import time
import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils import timezone
from ...application.services.audit_services import AuditService
from ..external.utils import get_client_ip

User = get_user_model()
logger = logging.getLogger(__name__)


class UserRequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware para registrar usuario y duración por request.

    Registra información detallada de cada request incluyendo:
    - Usuario autenticado
    - Duración del request
    - IP del cliente
    - User agent
    - Método HTTP y endpoint
    - Status code de respuesta
    """

    def process_request(self, request):
        """Registra el inicio del request."""
        # Solo procesar requests de API
        if not request.path.startswith("/api/"):
            return None

        # Marcar tiempo de inicio
        request._start_time = time.time()

        # Obtener información del usuario
        user_info = self._get_user_info(request)

        # Obtener información del cliente
        client_info = self._get_client_info(request)

        # Log del request iniciado
        logger.info(
            f"Request iniciado: {request.method} {request.path} | "
            f"Usuario: {user_info['username']} | "
            f"IP: {client_info['ip']} | "
            f"User-Agent: {client_info['user_agent'][:50]}..."
        )

        return None

    def process_response(self, request, response):
        """Registra el final del request y calcula duración."""
        # Solo procesar requests de API
        if not request.path.startswith("/api/"):
            return response

        # Calcular duración
        if hasattr(request, "_start_time"):
            duration = time.time() - request._start_time
        else:
            duration = 0

        # Obtener información del usuario
        user_info = self._get_user_info(request)

        # Obtener información del cliente
        client_info = self._get_client_info(request)

        # Log del request completado
        logger.info(
            f"Request completado: {request.method} {request.path} | "
            f"Usuario: {user_info['username']} | "
            f"IP: {client_info['ip']} | "
            f"Duración: {duration:.3f}s | "
            f"Status: {response.status_code}"
        )

        # Registrar en auditoría si el usuario está autenticado
        if user_info["is_authenticated"]:
            try:
                AuditService.log_action(
                    user=user_info["user"],
                    action_type="api_request",
                    description=f"Request {request.method} {request.path}",
                    ip_address=client_info["ip"],
                    user_agent=client_info["user_agent"],
                    extra_data={
                        "method": request.method,
                        "path": request.path,
                        "duration_seconds": round(duration, 3),
                        "status_code": response.status_code,
                        "query_params": dict(request.GET),
                        "content_type": request.content_type or "unknown",
                    },
                )
            except Exception as e:
                logger.error(f"Error registrando request en auditoría: {e}")

        # Agregar headers informativos a la respuesta
        response["X-Request-Duration"] = f"{duration:.3f}s"
        response["X-Request-User"] = user_info["username"]

        return response

    def _get_user_info(self, request):
        """Obtiene información del usuario actual."""
        if hasattr(request, "user") and request.user.is_authenticated:
            return {
                "user": request.user,
                "username": request.user.username,
                "user_type": request.user.user_type,
                "is_authenticated": True,
            }
        else:
            return {
                "user": None,
                "username": "anonymous",
                "user_type": "anonymous",
                "is_authenticated": False,
            }

    def _get_client_info(self, request):
        """Obtiene información del cliente."""
        return {
            "ip": get_client_ip(request),
            "user_agent": request.META.get("HTTP_USER_AGENT", "unknown"),
        }


class IPBlockingMiddleware(MiddlewareMixin):
    """
    Middleware opcional para bloquear IPs externas.

    Permite configurar listas de IPs permitidas y bloqueadas
    para controlar el acceso al sistema.
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        # IPs permitidas (configurables en settings)
        self.allowed_ips = getattr(settings, "ALLOWED_IPS", [])
        # IPs bloqueadas (configurables en settings)
        self.blocked_ips = getattr(settings, "BLOCKED_IPS", [])
        # Habilitar bloqueo (configurable en settings)
        self.enable_blocking = getattr(settings, "ENABLE_IP_BLOCKING", False)

    def process_request(self, request):
        """Verifica si la IP está permitida o bloqueada."""
        if not self.enable_blocking:
            return None

        # Solo aplicar a requests de API
        if not request.path.startswith("/api/"):
            return None

        client_ip = get_client_ip(request)

        # Verificar IPs bloqueadas
        if self.blocked_ips and client_ip in self.blocked_ips:
            logger.warning(
                f"IP bloqueada intentó acceder: {client_ip} - {request.path}"
            )

            # Registrar intento de acceso bloqueado
            try:
                AuditService.log_action(
                    user=None,
                    action_type="blocked_ip_access",
                    description=f"Intento de acceso desde IP bloqueada: {client_ip}",
                    ip_address=client_ip,
                    user_agent=request.META.get("HTTP_USER_AGENT", "unknown"),
                    extra_data={
                        "blocked_ip": client_ip,
                        "path": request.path,
                        "method": request.method,
                    },
                )
            except Exception as e:
                logger.error(f"Error registrando IP bloqueada: {e}")

            return JsonResponse(
                {
                    "error": "Acceso denegado",
                    "message": "Tu IP no tiene permisos para acceder a este sistema",
                },
                status=403,
            )

        # Verificar IPs permitidas (si está configurado)
        if self.allowed_ips and client_ip not in self.allowed_ips:
            logger.warning(
                f"IP no permitida intentó acceder: {client_ip} - {request.path}"
            )

            # Registrar intento de acceso no permitido
            try:
                AuditService.log_action(
                    user=None,
                    action_type="unauthorized_ip_access",
                    description=f"Intento de acceso desde IP no permitida: {client_ip}",
                    ip_address=client_ip,
                    user_agent=request.META.get("HTTP_USER_AGENT", "unknown"),
                    extra_data={
                        "unauthorized_ip": client_ip,
                        "path": request.path,
                        "method": request.method,
                        "allowed_ips": self.allowed_ips,
                    },
                )
            except Exception as e:
                logger.error(f"Error registrando IP no permitida: {e}")

            return JsonResponse(
                {
                    "error": "Acceso denegado",
                    "message": "Tu IP no está en la lista de IPs permitidas",
                },
                status=403,
            )

        return None


class GlobalErrorLoggingMiddleware(MiddlewareMixin):
    """
    Middleware para registrar errores globales.

    Captura y registra todos los errores que ocurren en el sistema,
    incluyendo excepciones no manejadas.
    """

    def process_exception(self, request, exception):
        """Captura y registra excepciones no manejadas."""
        # Obtener información del usuario
        user_info = self._get_user_info(request)

        # Obtener información del cliente
        client_info = self._get_client_info(request)

        # Log del error
        logger.error(
            f"Error global capturado: {type(exception).__name__}: {str(exception)} | "
            f"Usuario: {user_info['username']} | "
            f"IP: {client_info['ip']} | "
            f"Path: {request.path} | "
            f"Method: {request.method}"
        )

        # Registrar en auditoría
        try:
            AuditService.log_action(
                user=user_info["user"],
                action_type="global_error",
                description=f"Error global: {type(exception).__name__}",
                ip_address=client_info["ip"],
                user_agent=client_info["user_agent"],
                extra_data={
                    "exception_type": type(exception).__name__,
                    "exception_message": str(exception),
                    "path": request.path,
                    "method": request.method,
                    "query_params": dict(request.GET),
                    "post_data": (
                        dict(request.POST) if request.method == "POST" else None
                    ),
                    "user_authenticated": user_info["is_authenticated"],
                },
            )
        except Exception as audit_error:
            logger.error(f"Error registrando excepción en auditoría: {audit_error}")

        # Retornar respuesta de error personalizada
        return JsonResponse(
            {
                "error": "Error interno del servidor",
                "message": "Ha ocurrido un error inesperado. Por favor, contacta al administrador.",
                "error_id": f"{timezone.now().timestamp()}",  # ID único para tracking
            },
            status=500,
        )

    def _get_user_info(self, request):
        """Obtiene información del usuario actual."""
        if hasattr(request, "user") and request.user.is_authenticated:
            return {
                "user": request.user,
                "username": request.user.username,
                "user_type": request.user.user_type,
                "is_authenticated": True,
            }
        else:
            return {
                "user": None,
                "username": "anonymous",
                "user_type": "anonymous",
                "is_authenticated": False,
            }

    def _get_client_info(self, request):
        """Obtiene información del cliente."""
        return {
            "ip": get_client_ip(request),
            "user_agent": request.META.get("HTTP_USER_AGENT", "unknown"),
        }


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """
    Middleware adicional para monitoreo de rendimiento.

    Registra requests lentos y estadísticas de rendimiento.
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        # Umbral de tiempo para considerar un request lento (en segundos)
        self.slow_request_threshold = getattr(settings, "SLOW_REQUEST_THRESHOLD", 2.0)

    def process_request(self, request):
        """Registra el inicio del request para monitoreo."""
        if request.path.startswith("/api/"):
            request._performance_start_time = time.time()
        return None

    def process_response(self, request, response):
        """Registra el rendimiento del request."""
        if not request.path.startswith("/api/"):
            return response

        if hasattr(request, "_performance_start_time"):
            duration = time.time() - request._performance_start_time

            # Registrar requests lentos
            if duration > self.slow_request_threshold:
                user_info = self._get_user_info(request)
                client_info = self._get_client_info(request)

                logger.warning(
                    f"Request lento detectado: {request.method} {request.path} | "
                    f"Duración: {duration:.3f}s | "
                    f"Usuario: {user_info['username']} | "
                    f"IP: {client_info['ip']}"
                )

                # Registrar en auditoría
                try:
                    AuditService.log_action(
                        user=user_info["user"],
                        action_type="slow_request",
                        description=f"Request lento: {duration:.3f}s",
                        ip_address=client_info["ip"],
                        user_agent=client_info["user_agent"],
                        extra_data={
                            "duration_seconds": round(duration, 3),
                            "threshold_seconds": self.slow_request_threshold,
                            "path": request.path,
                            "method": request.method,
                            "status_code": response.status_code,
                        },
                    )
                except Exception as e:
                    logger.error(f"Error registrando request lento: {e}")

        return response

    def _get_user_info(self, request):
        """Obtiene información del usuario actual."""
        if hasattr(request, "user") and request.user.is_authenticated:
            return {
                "user": request.user,
                "username": request.user.username,
                "is_authenticated": True,
            }
        else:
            return {"user": None, "username": "anonymous", "is_authenticated": False}

    def _get_client_info(self, request):
        """Obtiene información del cliente."""
        return {
            "ip": get_client_ip(request),
            "user_agent": request.META.get("HTTP_USER_AGENT", "unknown"),
        }
