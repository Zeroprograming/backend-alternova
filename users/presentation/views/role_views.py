"""
Vistas de roles para la capa de presentación.
Implementa la interfaz de gestión de roles usando Django REST Framework.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
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
from ...application.services.user_application_service import RoleApplicationService
from ...application.dto.user_dto import (
    RoleAssignmentDTO,
    RoleAssignmentResponseDTO,
    BulkRoleAssignmentDTO,
    BulkRoleAssignmentResponseDTO,
    UserDTO,
    UserStatisticsDTO,
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


class RolePresentationViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de roles en la capa de presentación.
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
        self._role_app_service = RoleApplicationService(
            self._user_repository, self._audit_repository, self._domain_service
        )

    @extend_schema(
        summary="Asignar rol a usuario",
        description="Asigna un nuevo rol a un usuario específico",
        request=RoleAssignmentDTO,
        responses={200: RoleAssignmentResponseDTO, 400: "Bad Request"},
        examples=[
            OpenApiExample(
                "Role Assignment Example",
                summary="Ejemplo de asignación de rol",
                description="Ejemplo de asignación de rol a usuario",
                value={"user_id": 1, "new_role": "teacher"},
            )
        ],
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def assign_role(self, request):
        """Asigna un rol a un usuario."""
        try:
            # Validar datos de entrada
            serializer = RoleAssignmentDTO(**request.data)

            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Asignar rol usando el servicio de aplicación
            result = self._role_app_service.assign_role(
                user_id=serializer.user_id,
                new_role=serializer.new_role,
                requesting_user=requesting_user,
            )

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error assigning role: {str(e)}")
            return Response(
                {"error": "Failed to assign role"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Asignación masiva de roles",
        description="Asigna un rol a múltiples usuarios",
        request=BulkRoleAssignmentDTO,
        responses={200: BulkRoleAssignmentResponseDTO, 400: "Bad Request"},
        examples=[
            OpenApiExample(
                "Bulk Role Assignment Example",
                summary="Ejemplo de asignación masiva de roles",
                description="Ejemplo de asignación masiva de roles",
                value={"user_ids": [1, 2, 3], "new_role": "student"},
            )
        ],
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def bulk_assign_role(self, request):
        """Asigna un rol a múltiples usuarios."""
        try:
            # Validar datos de entrada
            serializer = BulkRoleAssignmentDTO(**request.data)

            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Asignar rol masivamente usando el servicio de aplicación
            result = self._role_app_service.bulk_assign_role(
                user_ids=serializer.user_ids,
                new_role=serializer.new_role,
                requesting_user=requesting_user,
            )

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error bulk assigning role: {str(e)}")
            return Response(
                {"error": "Failed to bulk assign role"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Obtener usuarios por rol",
        description="Obtiene usuarios filtrados por rol",
        parameters=[
            OpenApiParameter("role", OpenApiTypes.STR, description="Rol a buscar"),
            OpenApiParameter(
                "limit", OpenApiTypes.INT, description="Límite de resultados"
            ),
            OpenApiParameter(
                "offset", OpenApiTypes.INT, description="Offset para paginación"
            ),
        ],
        responses={200: "List of UserDTO"},
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def users_by_role(self, request):
        """Obtiene usuarios por rol."""
        try:
            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Obtener parámetros de filtro
            role = request.query_params.get("role")
            limit = request.query_params.get("limit")
            offset = request.query_params.get("offset")

            if not role:
                return Response(
                    {"error": "Role parameter is required"},
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Convertir parámetros numéricos
            if limit:
                limit = int(limit)
            if offset:
                offset = int(offset)

            # Obtener usuarios por rol usando el servicio de aplicación
            result = self._role_app_service.get_users_by_role(
                role=role, requesting_user=requesting_user, limit=limit, offset=offset
            )

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error getting users by role: {str(e)}")
            return Response(
                {"error": "Failed to get users by role"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Obtener estadísticas de roles",
        description="Obtiene estadísticas de distribución de roles",
        responses={200: UserStatisticsDTO},
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def role_statistics(self, request):
        """Obtiene estadísticas de roles."""
        try:
            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Obtener estadísticas usando el servicio de aplicación
            result = self._role_app_service.get_role_statistics(requesting_user)

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error getting role statistics: {str(e)}")
            return Response(
                {"error": "Failed to get role statistics"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Desactivar usuario",
        description="Desactiva un usuario del sistema",
        responses={200: "Success", 400: "Bad Request"},
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def deactivate_user(self, request):
        """Desactiva un usuario."""
        try:
            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Obtener user_id del request
            user_id = request.data.get("user_id")
            if not user_id:
                return Response(
                    {"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Desactivar usuario usando el servicio de aplicación
            result = self._role_app_service.deactivate_user(
                user_id=int(user_id), requesting_user=requesting_user
            )

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error deactivating user: {str(e)}")
            return Response(
                {"error": "Failed to deactivate user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Activar usuario",
        description="Activa un usuario del sistema",
        responses={200: "Success", 400: "Bad Request"},
    )
    @action(detail=False, methods=["post"], permission_classes=[IsAuthenticated])
    def activate_user(self, request):
        """Activa un usuario."""
        try:
            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Obtener user_id del request
            user_id = request.data.get("user_id")
            if not user_id:
                return Response(
                    {"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Activar usuario usando el servicio de aplicación
            result = self._role_app_service.activate_user(
                user_id=int(user_id), requesting_user=requesting_user
            )

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error activating user: {str(e)}")
            return Response(
                {"error": "Failed to activate user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Obtener permisos de usuario",
        description="Obtiene los permisos de un usuario específico",
        parameters=[
            OpenApiParameter("user_id", OpenApiTypes.INT, description="ID del usuario")
        ],
        responses={200: UserPermissionsDTO},
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def user_permissions(self, request):
        """Obtiene permisos de un usuario."""
        try:
            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Obtener user_id del query params
            user_id = request.query_params.get("user_id")
            if not user_id:
                return Response(
                    {"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Obtener permisos usando el servicio de aplicación
            permissions = self._role_app_service.get_user_permissions(int(user_id))

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

    @extend_schema(
        summary="Obtener roles disponibles",
        description="Obtiene la lista de roles disponibles en el sistema",
        responses={200: "List of available roles"},
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def available_roles(self, request):
        """Obtiene roles disponibles."""
        try:
            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Verificar permisos
            if not requesting_user.is_admin:
                return Response(
                    {"error": "Insufficient permissions"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Definir roles disponibles
            available_roles = [
                {
                    "value": "admin",
                    "label": "Administrador",
                    "description": "Acceso completo al sistema",
                },
                {
                    "value": "teacher",
                    "label": "Profesor",
                    "description": "Gestión de materias y calificaciones",
                },
                {
                    "value": "student",
                    "label": "Estudiante",
                    "description": "Acceso a materias y calificaciones propias",
                },
            ]

            return Response(
                {"success": True, "roles": available_roles}, status=status.HTTP_200_OK
            )

        except Exception as e:
            logger.error(f"Error getting available roles: {str(e)}")
            return Response(
                {"error": "Failed to get available roles"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Obtener transiciones de rol válidas",
        description="Obtiene las transiciones de rol válidas para un usuario",
        parameters=[
            OpenApiParameter("user_id", OpenApiTypes.INT, description="ID del usuario")
        ],
        responses={200: "List of valid role transitions"},
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def valid_role_transitions(self, request):
        """Obtiene transiciones de rol válidas."""
        try:
            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Verificar permisos
            if not requesting_user.is_admin:
                return Response(
                    {"error": "Insufficient permissions"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Obtener user_id del query params
            user_id = request.query_params.get("user_id")
            if not user_id:
                return Response(
                    {"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST
                )

            # Buscar usuario
            user = self._user_repository.find_by_id(UserId(int(user_id)))
            if not user:
                return Response(
                    {"error": "User not found"}, status=status.HTTP_404_NOT_FOUND
                )

            # Definir transiciones válidas
            valid_transitions = {
                "student": [
                    {"value": "teacher", "label": "Profesor"},
                    {"value": "admin", "label": "Administrador"},
                ],
                "teacher": [{"value": "admin", "label": "Administrador"}],
                "admin": [],
            }

            return Response(
                {
                    "success": True,
                    "current_role": user.user_type.value,
                    "valid_transitions": valid_transitions.get(
                        user.user_type.value, []
                    ),
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Error getting valid role transitions: {str(e)}")
            return Response(
                {"error": "Failed to get valid role transitions"},
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
