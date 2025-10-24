"""
Views personalizadas para autenticación JWT.
"""

from rest_framework import status
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.utils import timezone
from datetime import timedelta
from common.infrastructure.audit_models import UserSession
from common.application.services.audit_services import AuditService
from common.infrastructure.external.utils import get_client_ip
import logging

logger = logging.getLogger(__name__)


class CustomTokenObtainPairView(TokenObtainPairView):
    """
    Vista personalizada para login con JWT.
    Registra auditoría y guarda sesión.
    """

    @extend_schema(
        summary="Login (Obtener JWT)",
        description="Autentica un usuario y retorna tokens JWT. Registra la sesión y auditoría.",
        tags=["Autenticación"],
        examples=[
            OpenApiExample(
                "Ejemplo de login",
                value={"username": "estudiante1", "password": "Password123!"},
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        """Login con auditoría y gestión de sesiones."""
        # Obtener tokens (validación de credenciales)
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Obtener usuario
            from .models import User

            username = request.data.get("username")
            user = User.objects.get(username=username)

            # Extraer tokens
            access_token = response.data.get("access")
            refresh_token = response.data.get("refresh")

            # Obtener información del request
            ip_address = get_client_ip(request)
            user_agent = request.META.get("HTTP_USER_AGENT", "")

            # Calcular expiración (1 hora)
            expires_at = timezone.now() + timedelta(hours=1)

            # Crear sesión
            UserSession.objects.create(
                user=user,
                access_token=access_token,
                refresh_token=refresh_token,
                ip_address=ip_address,
                user_agent=user_agent,
                expires_at=expires_at,
            )

            # Registrar en auditoría
            AuditService.log_login(user, request)

            logger.info(f"Login exitoso: {username} desde IP {ip_address}")

            # Agregar información adicional a la respuesta
            response.data["user"] = {
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "user_type": user.user_type,
                "full_name": user.full_name,
            }

        return response


class CustomTokenRefreshView(TokenRefreshView):
    """
    Vista personalizada para refrescar JWT.
    Actualiza la sesión.
    """

    @extend_schema(
        summary="Refrescar JWT",
        description="Obtiene un nuevo access token usando el refresh token",
        tags=["Autenticación"],
    )
    def post(self, request, *args, **kwargs):
        """Refresh con actualización de sesión."""
        response = super().post(request, *args, **kwargs)

        if response.status_code == 200:
            # Obtener el refresh token del request
            refresh_token = request.data.get("refresh")

            try:
                # Buscar la sesión
                session = UserSession.objects.get(
                    refresh_token=refresh_token, is_active=True
                )

                # Actualizar access token
                new_access = response.data.get("access")
                session.access_token = new_access
                session.last_activity = timezone.now()
                session.save()

                logger.info(f"Token refrescado para usuario: {session.user.username}")

            except UserSession.DoesNotExist:
                logger.warning("Sesión no encontrada para refresh token")

        return response


class TokenVerifyView(APIView):
    """
    Vista para verificar validez de un token.
    """

    permission_classes = [AllowAny]

    @extend_schema(
        summary="Verificar JWT",
        description="Verifica si un token JWT es válido",
        tags=["Autenticación"],
    )
    def post(self, request):
        """Verificar token."""
        token = request.data.get("token")

        if not token:
            return Response(
                {"error": "Token es requerido"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            from rest_framework_simplejwt.tokens import AccessToken

            AccessToken(token)
            return Response({"valid": True}, status=status.HTTP_200_OK)

        except TokenError as e:
            return Response(
                {"valid": False, "error": str(e)},
                status=status.HTTP_401_UNAUTHORIZED,
            )


class LogoutView(APIView):
    """
    Vista para logout (invalidar tokens).
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Logout",
        description="Cierra la sesión del usuario y blacklistea el refresh token",
        tags=["Autenticación"],
        request={
            "application/json": {
                "type": "object",
                "properties": {"refresh": {"type": "string"}},
                "required": ["refresh"],
            }
        },
    )
    def post(self, request):
        """Logout con blacklist de token."""
        refresh_token = request.data.get("refresh")

        if not refresh_token:
            return Response(
                {"error": "refresh token es requerido"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            # Blacklist del refresh token
            token = RefreshToken(refresh_token)
            token.blacklist()

            # Desactivar sesión
            try:
                session = UserSession.objects.get(
                    refresh_token=refresh_token, is_active=True
                )
                session.deactivate()
            except UserSession.DoesNotExist:
                pass

            # Registrar en auditoría
            AuditService.log_logout(request.user, request)

            logger.info(f"Logout exitoso: {request.user.username}")

            return Response(
                {"message": "Logout exitoso"}, status=status.HTTP_205_RESET_CONTENT
            )

        except TokenError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ActiveSessionsView(APIView):
    """
    Vista para obtener sesiones activas del usuario.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Sesiones activas",
        description="Obtiene todas las sesiones activas del usuario actual",
        tags=["Autenticación"],
    )
    def get(self, request):
        """Obtener sesiones activas."""
        sessions = UserSession.objects.filter(user=request.user, is_active=True)

        data = [
            {
                "id": session.id,
                "ip_address": session.ip_address,
                "user_agent": session.user_agent,
                "created_at": session.created_at,
                "last_activity": session.last_activity,
                "expires_at": session.expires_at,
            }
            for session in sessions
        ]

        return Response(data)


class RevokeSessionView(APIView):
    """
    Vista para revocar una sesión específica.
    """

    permission_classes = [IsAuthenticated]

    @extend_schema(
        summary="Revocar sesión",
        description="Revoca una sesión específica del usuario",
        tags=["Autenticación"],
    )
    def post(self, request, session_id):
        """Revocar sesión por ID."""
        try:
            session = UserSession.objects.get(
                id=session_id, user=request.user, is_active=True
            )

            # Blacklist del token
            try:
                token = RefreshToken(session.refresh_token)
                token.blacklist()
            except:
                pass

            # Desactivar sesión
            session.deactivate()

            logger.info(f"Sesión {session_id} revocada por {request.user.username}")

            return Response({"message": "Sesión revocada exitosamente"})

        except UserSession.DoesNotExist:
            return Response(
                {"error": "Sesión no encontrada"}, status=status.HTTP_404_NOT_FOUND
            )
