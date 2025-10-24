"""
Middleware avanzado para gestión de roles y autenticación.
"""

import logging
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from common.application.services.audit_services import AuditService
from common.infrastructure.external.utils import get_client_ip

User = get_user_model()
logger = logging.getLogger(__name__)


class RoleBasedMiddleware(MiddlewareMixin):
    """
    Middleware que valida roles y permisos en tiempo real.
    """

    def process_request(self, request):
        """
        Procesa la request para validar roles y permisos.
        """
        # Solo procesar requests de API
        if not request.path.startswith("/api/"):
            return None

        # Obtener token JWT del header
        auth_header = request.META.get("HTTP_AUTHORIZATION", "")
        if not auth_header.startswith("Bearer "):
            return None

        try:
            # Extraer y validar token
            token = auth_header.split(" ")[1]
            access_token = AccessToken(token)
            user_id = access_token["user_id"]

            # Obtener usuario
            try:
                user = User.objects.get(id=user_id, is_active=True)
                request.user = user
            except User.DoesNotExist:
                return JsonResponse(
                    {"error": "Usuario no encontrado o inactivo"},
                    status=401,
                )

            # Validar que el usuario tenga un rol válido
            if user.user_type not in ["admin", "teacher", "student"]:
                return JsonResponse(
                    {"error": "Usuario sin rol válido"},
                    status=403,
                )

            # Log de acceso por rol
            self._log_role_access(request, user)

        except (InvalidToken, TokenError, KeyError) as e:
            logger.warning(f"Token inválido: {e}")
            return JsonResponse({"error": "Token inválido"}, status=401)

        return None

    def _log_role_access(self, request, user):
        """
        Registra el acceso por rol para auditoría.
        """
        try:
            ip_address = get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")

            AuditService.log_action(
                user=user,
                action_type="api_access",
                description=f"Acceso a {request.path} como {user.user_type}",
                ip_address=ip_address,
                user_agent=user_agent,
            )
        except Exception as e:
            logger.error(f"Error logging role access: {e}")


class AdminOnlyMiddleware(MiddlewareMixin):
    """
    Middleware que protege rutas administrativas.
    """

    ADMIN_PATHS = [
        "/api/admin/",
        "/api/users/roles/",
        "/api/users/assign-role/",
        "/api/subjects/prerequisites/",
    ]

    def process_request(self, request):
        """
        Valida que solo administradores accedan a rutas administrativas.
        """
        if not any(request.path.startswith(path) for path in self.ADMIN_PATHS):
            return None

        # Verificar que el usuario esté autenticado
        if not hasattr(request, "user") or not request.user.is_authenticated:
            return JsonResponse({"error": "Autenticación requerida"}, status=401)

        # Verificar que sea administrador
        if not request.user.is_staff:
            logger.warning(
                f"Usuario {request.user.username} intentó acceder a ruta administrativa {request.path}"
            )
            return JsonResponse(
                {"error": "Acceso denegado: se requieren permisos de administrador"},
                status=403,
            )

        return None


class TeacherOnlyMiddleware(MiddlewareMixin):
    """
    Middleware que protege rutas de profesores.
    """

    TEACHER_PATHS = [
        "/api/academic/teachers/",
        "/api/subjects/assign-grade/",
        "/api/subjects/finish-subject/",
    ]

    def process_request(self, request):
        """
        Valida que solo profesores accedan a rutas de profesores.
        """
        if not any(request.path.startswith(path) for path in self.TEACHER_PATHS):
            return None

        # Verificar que el usuario esté autenticado
        if not hasattr(request, "user") or not request.user.is_authenticated:
            return JsonResponse({"error": "Autenticación requerida"}, status=401)

        # Verificar que sea profesor o administrador
        if not (request.user.is_teacher or request.user.is_staff):
            logger.warning(
                f"Usuario {request.user.username} intentó acceder a ruta de profesor {request.path}"
            )
            return JsonResponse(
                {"error": "Acceso denegado: se requieren permisos de profesor"},
                status=403,
            )

        return None


class StudentOnlyMiddleware(MiddlewareMixin):
    """
    Middleware que protege rutas de estudiantes.
    """

    STUDENT_PATHS = [
        "/api/academic/students/",
        "/api/enrollments/enroll/",
    ]

    def process_request(self, request):
        """
        Valida que solo estudiantes accedan a rutas de estudiantes.
        """
        if not any(request.path.startswith(path) for path in self.STUDENT_PATHS):
            return None

        # Verificar que el usuario esté autenticado
        if not hasattr(request, "user") or not request.user.is_authenticated:
            return JsonResponse({"error": "Autenticación requerida"}, status=401)

        # Verificar que sea estudiante o administrador
        if not (request.user.is_student or request.user.is_staff):
            logger.warning(
                f"Usuario {request.user.username} intentó acceder a ruta de estudiante {request.path}"
            )
            return JsonResponse(
                {"error": "Acceso denegado: se requieren permisos de estudiante"},
                status=403,
            )

        return None


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware que agrega headers de seguridad.
    """

    def process_response(self, request, response):
        """
        Agrega headers de seguridad a la respuesta.
        """
        # Solo para requests de API
        if request.path.startswith("/api/"):
            response["X-Content-Type-Options"] = "nosniff"
            response["X-Frame-Options"] = "DENY"
            response["X-XSS-Protection"] = "1; mode=block"
            response["Strict-Transport-Security"] = (
                "max-age=31536000; includeSubDomains"
            )

        return response


class RateLimitMiddleware(MiddlewareMixin):
    """
    Middleware básico de rate limiting por rol.
    """

    def __init__(self, get_response):
        super().__init__(get_response)
        self.request_counts = {}

    def process_request(self, request):
        """
        Implementa rate limiting básico por IP y usuario.
        """
        # Solo para requests de API
        if not request.path.startswith("/api/"):
            return None

        # Obtener identificador único
        if hasattr(request, "user") and request.user.is_authenticated:
            identifier = f"user_{request.user.id}"
        else:
            identifier = f"ip_{get_client_ip(request)}"

        # Contar requests
        import time

        current_time = int(time.time())
        minute_key = f"{identifier}_{current_time // 60}"

        if minute_key not in self.request_counts:
            self.request_counts[minute_key] = 0

        self.request_counts[minute_key] += 1

        # Límites por rol
        if hasattr(request, "user") and request.user.is_authenticated:
            if request.user.is_staff:
                limit = 1000  # Admin: 1000 requests/min
            elif request.user.is_teacher:
                limit = 500  # Profesor: 500 requests/min
            elif request.user.is_student:
                limit = 200  # Estudiante: 200 requests/min
            else:
                limit = 100  # Usuario no autenticado: 100 requests/min
        else:
            limit = 100  # IP no autenticada: 100 requests/min

        # Verificar límite
        if self.request_counts[minute_key] > limit:
            logger.warning(f"Rate limit excedido para {identifier}")
            return JsonResponse(
                {"error": "Demasiadas requests. Intenta más tarde."},
                status=429,
            )

        # Limpiar contadores antiguos
        self._cleanup_old_counts(current_time)

        return None

    def _cleanup_old_counts(self, current_time):
        """
        Limpia contadores de más de 5 minutos.
        """
        cutoff_time = current_time - 300  # 5 minutos
        cutoff_minute = cutoff_time // 60

        keys_to_remove = [
            key
            for key in self.request_counts.keys()
            if int(key.split("_")[-1]) < cutoff_minute
        ]

        for key in keys_to_remove:
            del self.request_counts[key]
