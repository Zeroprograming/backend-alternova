"""
Vistas de autenticación para la capa de presentación.
Implementa la interfaz de autenticación usando Django REST Framework.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.utils import timezone
from datetime import timedelta
import logging

from ...domain.entities import User
from ...domain.value_objects import (
    UserId,
    Username,
    Email,
    Password,
    UserType,
    UserStatus,
)
from ...domain.repositories import (
    UserRepository,
    UserProfileRepository,
    UserSessionRepository,
    AuditRepository,
)
from ...domain.services import UserDomainService, AcademicDomainService
from ...application.services.user_application_service import AuthApplicationService
from ...application.dto.user_dto import (
    LoginDTO,
    LoginResponseDTO,
    LogoutDTO,
    LogoutResponseDTO,
    RefreshTokenDTO,
    RefreshTokenResponseDTO,
    VerifyTokenDTO,
    VerifyTokenResponseDTO,
    UserSessionDTO,
    UserPermissionsDTO,
)
from ...infrastructure.repositories.django_user_repository import (
    DjangoUserRepository,
    DjangoUserProfileRepository,
    DjangoUserSessionRepository,
    DjangoAuditRepository,
    DjangoNotificationRepository,
)
from ...infrastructure.external.email_service import (
    EmailService,
    JWTService,
    PasswordService,
)
from ...infrastructure.middleware.auth_middleware import (
    RequestLoggingMiddleware,
    JWTAuthenticationMiddleware,
    RoleBasedAccessMiddleware,
    SecurityHeadersMiddleware,
    RateLimitingMiddleware,
    ErrorHandlingMiddleware,
)

logger = logging.getLogger(__name__)


class AuthPresentationViewSet(viewsets.ViewSet):
    """
    ViewSet para autenticación en la capa de presentación.
    Coordina entre la capa de aplicación y la interfaz de usuario.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Inicializar servicios de infraestructura
        self._user_repository = DjangoUserRepository()
        self._profile_repository = DjangoUserProfileRepository()
        self._session_repository = DjangoUserSessionRepository()
        self._audit_repository = DjangoAuditRepository()
        self._notification_repository = DjangoNotificationRepository()

        # Inicializar servicios de dominio
        self._domain_service = UserDomainService(
            self._user_repository, self._profile_repository
        )
        self._academic_domain_service = AcademicDomainService(self._user_repository)

        # Inicializar servicios de aplicación
        self._auth_app_service = AuthApplicationService(
            self._user_repository,
            self._session_repository,
            self._audit_repository,
            self._domain_service,
        )

    @extend_schema(
        summary="Login de usuario",
        description="Autentica un usuario y retorna tokens JWT",
        request=LoginDTO,
        responses={200: LoginResponseDTO, 400: "Bad Request"},
        examples=[
            OpenApiExample(
                "Login Example",
                summary="Ejemplo de login",
                description="Ejemplo de login de usuario",
                value={
                    "username": "johndoe",
                    "password": "password123",
                    "ip_address": "192.168.1.1",
                    "user_agent": "Mozilla/5.0...",
                },
            )
        ],
    )
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def login(self, request):
        """Realiza login de usuario."""
        try:
            # Validar datos de entrada
            serializer = LoginDTO(**request.data)

            # Obtener información del request
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")

            # Realizar login usando el servicio de aplicación
            result = self._auth_app_service.login(
                username=serializer.username,
                password=serializer.password,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return Response(
                {"error": "Login failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Logout de usuario",
        description="Cierra la sesión de un usuario",
        request=LogoutDTO,
        responses={200: LogoutResponseDTO, 400: "Bad Request"},
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """Realiza logout de usuario."""
        try:
            # Validar datos de entrada
            serializer = LogoutDTO(**request.data)

            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Realizar logout usando el servicio de aplicación
            result = self._auth_app_service.logout(
                session_id=serializer.session_id, user_id=requesting_user.id.value
            )

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            return Response(
                {"error": "Logout failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    @extend_schema(
        summary="Refrescar token",
        description="Refresca un token JWT usando el refresh token",
        request=RefreshTokenDTO,
        responses={200: RefreshTokenResponseDTO, 400: "Bad Request"},
    )
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def refresh_token(self, request):
        """Refresca un token JWT."""
        try:
            # Validar datos de entrada
            serializer = RefreshTokenDTO(**request.data)

            # Refrescar token usando el servicio de aplicación
            result = self._auth_app_service.refresh_token(serializer.refresh_token)

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return Response(
                {"error": "Token refresh failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Verificar token",
        description="Verifica la validez de un token JWT",
        request=VerifyTokenDTO,
        responses={200: VerifyTokenResponseDTO, 400: "Bad Request"},
    )
    @action(detail=False, methods=["post"], permission_classes=[AllowAny])
    def verify_token(self, request):
        """Verifica un token JWT."""
        try:
            # Validar datos de entrada
            serializer = VerifyTokenDTO(**request.data)

            # Verificar token usando el servicio de aplicación
            result = self._auth_app_service.verify_token(serializer.access_token)

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return Response(
                {"error": "Token verification failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Obtener sesiones activas",
        description="Obtiene las sesiones activas de un usuario",
        responses={200: "List of UserSessionDTO"},
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def active_sessions(self, request):
        """Obtiene sesiones activas de un usuario."""
        try:
            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Obtener sesiones activas usando el servicio de aplicación
            sessions = self._auth_app_service.get_active_sessions(
                requesting_user.id.value
            )

            return Response(
                {"success": True, "sessions": sessions}, status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error getting active sessions: {str(e)}")
            return Response(
                {"error": "Failed to get active sessions"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Revocar sesión",
        description="Revoca una sesión específica de un usuario",
        responses={200: "Success", 400: "Bad Request"},
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def revoke_session(self, request):
        """Revoca una sesión específica."""
        try:
            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Obtener session_id del request
            session_id = request.data.get("session_id")
            if not session_id:
                return Response(
                    {"error": "Session ID is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Revocar sesión usando el servicio de aplicación
            result = self._auth_app_service.revoke_session(
                session_id, requesting_user.id.value
            )

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error revoking session: {str(e)}")
            return Response(
                {"error": "Failed to revoke session"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Revocar todas las sesiones",
        description="Revoca todas las sesiones de un usuario",
        responses={200: "Success", 400: "Bad Request"},
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def revoke_all_sessions(self, request):
        """Revoca todas las sesiones de un usuario."""
        try:
            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Revocar todas las sesiones usando el servicio de aplicación
            result = self._auth_app_service.revoke_all_sessions(
                requesting_user.id.value
            )

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error revoking all sessions: {str(e)}")
            return Response(
                {"error": "Failed to revoke all sessions"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Obtener permisos de usuario",
        description="Obtiene los permisos de un usuario",
        responses={200: UserPermissionsDTO},
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def permissions(self, request):
        """Obtiene permisos de un usuario."""
        try:
            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Obtener permisos usando el servicio de aplicación
            permissions = self._auth_app_service.get_user_permissions(
                requesting_user.id.value
            )

            if permissions["success"]:
                return Response(permissions, status=status.HTTP_200_OK)
            else:
                return Response(permissions, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error getting user permissions: {str(e)}")
            return Response(
                {"error": "Failed to get user permissions"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    def _get_requesting_user(self, request) -> User:
        """Obtiene el usuario que realiza la solicitud."""
        try:
            # Obtener información del usuario del request
            user_id = getattr(request, "user_id", None)
            if not user_id:
                raise ValueError("User not authenticated")

            # Buscar usuario en el repositorio
            user = self._user_repository.find_by_id(UserId(user_id))
            if not user:
                raise ValueError("User not found")

            return user

        except Exception as e:
            logger.error(f"Error getting requesting user: {str(e)}")
            raise ValueError("Failed to get requesting user")

    def _get_client_ip(self, request) -> str:
        """Obtiene la dirección IP del cliente."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class CustomTokenObtainPairView(APIView):
    """
    Vista personalizada para login con JWT.
    Registra auditoría y guarda sesión.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Login (Obtener JWT)",
        description="Autentica un usuario y retorna tokens JWT",
        request=LoginDTO,
        responses={200: LoginResponseDTO, 400: "Bad Request"},
    )
    def post(self, request):
        """Realiza login de usuario."""
        try:
            # Validar datos de entrada
            serializer = LoginDTO(**request.data)

            # Obtener información del request
            ip_address = self._get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")

            # Realizar login usando el servicio de aplicación
            auth_service = AuthApplicationService(
                DjangoUserRepository(),
                DjangoUserSessionRepository(),
                DjangoAuditRepository(),
                UserDomainService(
                    DjangoUserRepository(), DjangoUserProfileRepository()
                ),
            )

            result = auth_service.login(
                username=serializer.username,
                password=serializer.password,
                ip_address=ip_address,
                user_agent=user_agent,
            )

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error during login: {str(e)}")
            return Response(
                {"error": "Login failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_client_ip(self, request) -> str:
        """Obtiene la dirección IP del cliente."""
        x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded_for:
            ip = x_forwarded_for.split(",")[0]
        else:
            ip = request.META.get("REMOTE_ADDR")
        return ip


class CustomTokenRefreshView(APIView):
    """
    Vista personalizada para refresh de JWT.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Refresh Token",
        description="Refresca un token JWT usando el refresh token",
        request=RefreshTokenDTO,
        responses={200: RefreshTokenResponseDTO, 400: "Bad Request"},
    )
    def post(self, request):
        """Refresca un token JWT."""
        try:
            # Validar datos de entrada
            serializer = RefreshTokenDTO(**request.data)

            # Refrescar token usando el servicio de aplicación
            auth_service = AuthApplicationService(
                DjangoUserRepository(),
                DjangoUserSessionRepository(),
                DjangoAuditRepository(),
                UserDomainService(
                    DjangoUserRepository(), DjangoUserProfileRepository()
                ),
            )

            result = auth_service.refresh_token(serializer.refresh_token)

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error refreshing token: {str(e)}")
            return Response(
                {"error": "Token refresh failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class TokenVerifyView(APIView):
    """
    Vista para verificar tokens JWT.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Verify Token",
        description="Verifica la validez de un token JWT",
        request=VerifyTokenDTO,
        responses={200: VerifyTokenResponseDTO, 400: "Bad Request"},
    )
    def post(self, request):
        """Verifica un token JWT."""
        try:
            # Validar datos de entrada
            serializer = VerifyTokenDTO(**request.data)

            # Verificar token usando el servicio de aplicación
            auth_service = AuthApplicationService(
                DjangoUserRepository(),
                DjangoUserSessionRepository(),
                DjangoAuditRepository(),
                UserDomainService(
                    DjangoUserRepository(), DjangoUserProfileRepository()
                ),
            )

            result = auth_service.verify_token(serializer.access_token)

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error verifying token: {str(e)}")
            return Response(
                {"error": "Token verification failed"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class LogoutView(APIView):
    """
    Vista para logout de usuarios.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Logout",
        description="Cierra la sesión de un usuario",
        request=LogoutDTO,
        responses={200: LogoutResponseDTO, 400: "Bad Request"},
    )
    def post(self, request):
        """Realiza logout de usuario."""
        try:
            # Validar datos de entrada
            serializer = LogoutDTO(**request.data)

            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Realizar logout usando el servicio de aplicación
            auth_service = AuthApplicationService(
                DjangoUserRepository(),
                DjangoUserSessionRepository(),
                DjangoAuditRepository(),
                UserDomainService(
                    DjangoUserRepository(), DjangoUserProfileRepository()
                ),
            )

            result = auth_service.logout(
                session_id=serializer.session_id, user_id=requesting_user.id.value
            )

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error during logout: {str(e)}")
            return Response(
                {"error": "Logout failed"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    def _get_requesting_user(self, request) -> User:
        """Obtiene el usuario que realiza la solicitud."""
        try:
            # Obtener información del usuario del request
            user_id = getattr(request, "user_id", None)
            if not user_id:
                raise ValueError("User not authenticated")

            # Buscar usuario en el repositorio
            user_repository = DjangoUserRepository()
            user = user_repository.find_by_id(UserId(user_id))
            if not user:
                raise ValueError("User not found")

            return user

        except Exception as e:
            logger.error(f"Error getting requesting user: {str(e)}")
            raise ValueError("Failed to get requesting user")
