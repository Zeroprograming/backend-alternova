"""
Middleware de infraestructura para la capa de infraestructura.
Implementa middleware que interactúa con sistemas externos.
"""

import logging
import time
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from common.audit_services import AuditService
from common.utils import get_client_ip
from .external.jwt_service import JWTService

User = get_user_model()
logger = logging.getLogger(__name__)


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware para logging de requests.
    Registra información detallada de cada request.
    """

    def process_request(self, request):
        """Procesa el request y registra información."""
        request.start_time = time.time()

        # Solo procesar requests de API
        if not request.path.startswith("/api/"):
            return None

        # Obtener información del request
        ip_address = get_client_ip(request)
        user_agent = request.META.get("HTTP_USER_AGENT", "")
        method = request.method
        path = request.path
        query_params = request.GET.dict()

        # Intentar obtener información del usuario
        user_info = self._get_user_info(request)

        # Log del request
        logger.info(
            f"Request: {method} {path} | "
            f"IP: {ip_address} | "
            f"User: {user_info.get('username', 'Anonymous')} | "
            f"Query: {query_params}"
        )

        return None

    def process_response(self, request, response):
        """Procesa la respuesta y registra información."""
        if not hasattr(request, "start_time"):
            return response

        # Calcular duración del request
        duration = time.time() - request.start_time

        # Solo procesar responses de API
        if not request.path.startswith("/api/"):
            return response

        # Obtener información del request
        ip_address = get_client_ip(request)
        user_info = self._get_user_info(request)

        # Log de la respuesta
        logger.info(
            f"Response: {request.method} {request.path} | "
            f"Status: {response.status_code} | "
            f"Duration: {duration:.3f}s | "
            f"IP: {ip_address} | "
            f"User: {user_info.get('username', 'Anonymous')}"
        )

        return response

    def _get_user_info(self, request) -> dict:
        """Obtiene información del usuario del request."""
        try:
            # Intentar obtener token JWT
            auth_header = request.META.get("HTTP_AUTHORIZATION", "")
            if auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                user_data = JWTService.validate_token(token)
                if user_data:
                    return {
                        "user_id": user_data.get("user_id"),
                        "username": user_data.get("username"),
                        "user_type": user_data.get("user_type"),
                    }
        except Exception as e:
            logger.debug(f"Failed to get user info: {str(e)}")

        return {}


class JWTAuthenticationMiddleware(MiddlewareMixin):
    """
    Middleware para autenticación JWT.
    Valida tokens JWT y establece el usuario en el request.
    """

    def process_request(self, request):
        """Procesa el request y valida el token JWT."""
        # Solo procesar requests de API
        if not request.path.startswith("/api/"):
            return None

        # Obtener token del header Authorization
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return None

        try:
            token = auth_header.split(" ")[1]
            user_data = JWTService.validate_token(token)

            if user_data:
                # Establecer información del usuario en el request
                request.user_data = user_data
                request.user_id = user_data.get("user_id")
                request.username = user_data.get("username")
                request.user_type = user_data.get("user_type")

                # Obtener usuario completo de la base de datos
                try:
                    user = User.objects.get(id=user_data["user_id"], is_active=True)
                    request.user = user
                except User.DoesNotExist:
                    logger.warning(f"User {user_data['user_id']} not found or inactive")
                    return None
            else:
                logger.warning("Invalid JWT token")
                return None

        except (InvalidToken, TokenError) as e:
            logger.warning(f"JWT token error: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"JWT authentication error: {str(e)}")
            return None

        return None


class RoleBasedAccessMiddleware(MiddlewareMixin):
    """
    Middleware para control de acceso basado en roles.
    Valida permisos según el rol del usuario.
    """

    # Definir rutas protegidas por rol
    ADMIN_ROUTES = [
        "/api/admin/",
        "/api/users/",
        "/api/roles/",
        "/api/reports/",
        "/api/statistics/",
    ]

    TEACHER_ROUTES = [
        "/api/subjects/",
        "/api/grades/",
        "/api/students/",
        "/api/teacher/",
    ]

    STUDENT_ROUTES = [
        "/api/student/",
        "/api/enrollments/",
        "/api/grades/",
        "/api/notifications/",
    ]

    def process_request(self, request):
        """Procesa el request y valida permisos."""
        # Solo procesar requests de API
        if not request.path.startswith("/api/"):
            return None

        # Obtener información del usuario
        user_type = getattr(request, "user_type", None)
        if not user_type:
            return None

        # Verificar permisos según la ruta
        if not self._has_permission(request.path, user_type):
            logger.warning(
                f"Access denied: User {getattr(request, 'username', 'Unknown')} "
                f"with role {user_type} tried to access {request.path}"
            )

            return JsonResponse({"error": "Insufficient permissions"}, status=403)

        return None

    def _has_permission(self, path: str, user_type: str) -> bool:
        """Verifica si el usuario tiene permisos para acceder a la ruta."""
        # Rutas públicas (no requieren autenticación)
        public_routes = [
            "/api/auth/login/",
            "/api/auth/refresh/",
            "/api/auth/verify/",
            "/api/health/",
            "/api/schema/",
            "/api/docs/",
            "/api/redoc/",
        ]

        if path in public_routes:
            return True

        # Verificar permisos por rol
        if user_type == "admin":
            return True  # Los admins tienen acceso a todo

        elif user_type == "teacher":
            return self._is_teacher_route(path)

        elif user_type == "student":
            return self._is_student_route(path)

        return False

    def _is_teacher_route(self, path: str) -> bool:
        """Verifica si la ruta es accesible para profesores."""
        for route in self.TEACHER_ROUTES:
            if path.startswith(route):
                return True
        return False

    def _is_student_route(self, path: str) -> bool:
        """Verifica si la ruta es accesible para estudiantes."""
        for route in self.STUDENT_ROUTES:
            if path.startswith(route):
                return True
        return False


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware para agregar headers de seguridad.
    Agrega headers HTTP de seguridad a las respuestas.
    """

    def process_response(self, request, response):
        """Procesa la respuesta y agrega headers de seguridad."""
        # Solo procesar responses de API
        if not request.path.startswith("/api/"):
            return response

        # Headers de seguridad
        security_headers = {
            "X-Content-Type-Options": "nosniff",
            "X-Frame-Options": "DENY",
            "X-XSS-Protection": "1; mode=block",
            "Strict-Transport-Security": "max-age=31536000; includeSubDomains",
            "Content-Security-Policy": "default-src 'self'",
            "Referrer-Policy": "strict-origin-when-cross-origin",
        }

        # Agregar headers a la respuesta
        for header, value in security_headers.items():
            response[header] = value

        return response


class RateLimitingMiddleware(MiddlewareMixin):
    """
    Middleware para limitación de velocidad.
    Limita el número de requests por IP y usuario.
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        self.rate_limits = {
            "login": {"requests": 5, "window": 300},  # 5 requests en 5 minutos
            "api": {"requests": 100, "window": 60},  # 100 requests en 1 minuto
            "default": {"requests": 50, "window": 60},  # 50 requests en 1 minuto
        }

    def process_request(self, request):
        """Procesa el request y verifica límites de velocidad."""
        # Solo procesar requests de API
        if not request.path.startswith("/api/"):
            return None

        # Obtener información del request
        ip_address = get_client_ip(request)
        user_id = getattr(request, "user_id", None)

        # Determinar el tipo de límite
        if request.path.startswith("/api/auth/login/"):
            limit_type = "login"
        elif request.path.startswith("/api/"):
            limit_type = "api"
        else:
            limit_type = "default"

        # Verificar límite de velocidad
        if not self._check_rate_limit(ip_address, user_id, limit_type):
            logger.warning(
                f"Rate limit exceeded: IP {ip_address}, "
                f"User {user_id}, Path {request.path}"
            )

            return JsonResponse(
                {"error": "Rate limit exceeded. Please try again later."}, status=429
            )

        return None

    def _check_rate_limit(self, ip_address: str, user_id: int, limit_type: str) -> bool:
        """Verifica si se ha excedido el límite de velocidad."""
        try:
            from django.core.cache import cache

            # Obtener configuración del límite
            limit_config = self.rate_limits.get(limit_type, self.rate_limits["default"])
            max_requests = limit_config["requests"]
            window_seconds = limit_config["window"]

            # Crear clave de caché
            if user_id:
                cache_key = f"rate_limit_user_{user_id}_{limit_type}"
            else:
                cache_key = f"rate_limit_ip_{ip_address}_{limit_type}"

            # Obtener contador actual
            current_count = cache.get(cache_key, 0)

            # Verificar si se ha excedido el límite
            if current_count >= max_requests:
                return False

            # Incrementar contador
            cache.set(cache_key, current_count + 1, window_seconds)

            return True

        except Exception as e:
            logger.error(f"Rate limiting error: {str(e)}")
            return True  # En caso de error, permitir el request


class ErrorHandlingMiddleware(MiddlewareMixin):
    """
    Middleware para manejo de errores.
    Captura errores y los registra de manera consistente.
    """

    def process_exception(self, request, exception):
        """Procesa excepciones y las registra."""
        # Solo procesar excepciones de API
        if not request.path.startswith("/api/"):
            return None

        # Obtener información del request
        ip_address = get_client_ip(request)
        user_info = self._get_user_info(request)

        # Log del error
        logger.error(
            f"API Error: {request.method} {request.path} | "
            f"IP: {ip_address} | "
            f"User: {user_info.get('username', 'Anonymous')} | "
            f"Error: {str(exception)}"
        )

        # Registrar en auditoría
        try:
            AuditService.log_action(
                user_id=user_info.get("user_id"),
                action_type="error",
                description=f"API Error: {str(exception)}",
                extra_data={
                    "path": request.path,
                    "method": request.method,
                    "ip_address": ip_address,
                    "error_type": type(exception).__name__,
                },
            )
        except Exception as audit_error:
            logger.error(f"Failed to log error to audit: {str(audit_error)}")

        # Retornar respuesta de error
        return JsonResponse({"error": "Internal server error"}, status=500)

    def _get_user_info(self, request) -> dict:
        """Obtiene información del usuario del request."""
        return {
            "user_id": getattr(request, "user_id", None),
            "username": getattr(request, "username", "Anonymous"),
            "user_type": getattr(request, "user_type", None),
        }

