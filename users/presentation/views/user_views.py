"""
Vistas de presentación para la capa de presentación.
Implementa la interfaz de usuario (API) usando Django REST Framework.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
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
from ...application.services.user_application_service import (
    UserApplicationService,
    AuthApplicationService,
    RoleApplicationService,
)
from ...application.dto.user_dto import (
    UserDTO,
    CreateUserDTO,
    UpdateUserDTO,
    LoginDTO,
    LoginResponseDTO,
    LogoutDTO,
    LogoutResponseDTO,
    RefreshTokenDTO,
    RefreshTokenResponseDTO,
    VerifyTokenDTO,
    VerifyTokenResponseDTO,
    RoleAssignmentDTO,
    RoleAssignmentResponseDTO,
    BulkRoleAssignmentDTO,
    BulkRoleAssignmentResponseDTO,
    UserSessionDTO,
    UserStatisticsDTO,
    SearchUsersDTO,
    SearchUsersResponseDTO,
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


class UserPresentationViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de usuarios en la capa de presentación.
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
        self._user_app_service = UserApplicationService(
            self._user_repository,
            self._profile_repository,
            self._session_repository,
            self._audit_repository,
            self._domain_service,
        )
        self._auth_app_service = AuthApplicationService(
            self._user_repository,
            self._session_repository,
            self._audit_repository,
            self._domain_service,
        )
        self._role_app_service = RoleApplicationService(
            self._user_repository, self._audit_repository, self._domain_service
        )

    @extend_schema(
        summary="Crear usuario",
        description="Crea un nuevo usuario en el sistema",
        request=CreateUserDTO,
        responses={201: UserDTO, 400: "Bad Request"},
    )
    def create(self, request):
        """Crea un nuevo usuario."""
        try:
            # Validar datos de entrada
            serializer = CreateUserDTO(**request.data)

            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Crear usuario usando el servicio de aplicación
            result = self._user_app_service.create_user(
                username=serializer.username,
                email=serializer.email,
                password=serializer.password,
                user_type=serializer.user_type,
                first_name=serializer.first_name,
                last_name=serializer.last_name,
                phone=serializer.phone,
                max_credits_per_semester=serializer.max_credits_per_semester,
                academic_year=serializer.academic_year,
                requesting_user=requesting_user,
            )

            if result["success"]:
                return Response(result, status=status.HTTP_201_CREATED)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error creating user: {str(e)}")
            return Response(
                {"error": "Failed to create user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Obtener usuario",
        description="Obtiene un usuario por ID",
        responses={200: UserDTO, 404: "Not Found"},
    )
    def retrieve(self, request, pk=None):
        """Obtiene un usuario por ID."""
        try:
            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Obtener usuario usando el servicio de aplicación
            result = self._user_app_service.get_user(int(pk), requesting_user)

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            logger.error(f"Error retrieving user: {str(e)}")
            return Response(
                {"error": "Failed to retrieve user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Listar usuarios",
        description="Lista usuarios con filtros y paginación",
        parameters=[
            OpenApiParameter(
                "user_type", OpenApiTypes.STR, description="Tipo de usuario"
            ),
            OpenApiParameter(
                "status", OpenApiTypes.STR, description="Estado del usuario"
            ),
            OpenApiParameter(
                "search", OpenApiTypes.STR, description="Texto de búsqueda"
            ),
            OpenApiParameter(
                "limit", OpenApiTypes.INT, description="Límite de resultados"
            ),
            OpenApiParameter(
                "offset", OpenApiTypes.INT, description="Offset para paginación"
            ),
        ],
        responses={200: SearchUsersResponseDTO},
    )
    def list(self, request):
        """Lista usuarios con filtros."""
        try:
            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Obtener parámetros de filtro
            user_type = request.query_params.get("user_type")
            status_param = request.query_params.get("status")
            search = request.query_params.get("search")
            limit = request.query_params.get("limit")
            offset = request.query_params.get("offset")

            # Convertir parámetros numéricos
            if limit:
                limit = int(limit)
            if offset:
                offset = int(offset)

            # Listar usuarios usando el servicio de aplicación
            result = self._user_app_service.list_users(
                requesting_user=requesting_user,
                user_type=user_type,
                status=status_param,
                search=search,
                limit=limit,
                offset=offset,
            )

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error listing users: {str(e)}")
            return Response(
                {"error": "Failed to list users"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Actualizar usuario",
        description="Actualiza un usuario existente",
        request=UpdateUserDTO,
        responses={200: UserDTO, 400: "Bad Request"},
    )
    def update(self, request, pk=None):
        """Actualiza un usuario."""
        try:
            # Validar datos de entrada
            serializer = UpdateUserDTO(**request.data)

            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Actualizar usuario usando el servicio de aplicación
            result = self._user_app_service.update_user(
                user_id=int(pk), requesting_user=requesting_user, **request.data
            )

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error updating user: {str(e)}")
            return Response(
                {"error": "Failed to update user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Eliminar usuario",
        description="Elimina un usuario del sistema",
        responses={200: "Success", 400: "Bad Request"},
    )
    def destroy(self, request, pk=None):
        """Elimina un usuario."""
        try:
            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Eliminar usuario usando el servicio de aplicación
            result = self._user_app_service.delete_user(int(pk), requesting_user)

            if result["success"]:
                return Response(result, status=status.HTTP_200_OK)
            else:
                return Response(result, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            logger.error(f"Error deleting user: {str(e)}")
            return Response(
                {"error": "Failed to delete user"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Obtener estadísticas de usuarios",
        description="Obtiene estadísticas generales de usuarios",
        responses={200: UserStatisticsDTO},
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def statistics(self, request):
        """Obtiene estadísticas de usuarios."""
        try:
            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Verificar permisos
            if not requesting_user.is_admin:
                return Response(
                    {"error": "Insufficient permissions"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Obtener estadísticas usando el servicio de aplicación
            stats = self._user_app_service.get_user_statistics()

            return Response(stats, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error getting user statistics: {str(e)}")
            return Response(
                {"error": "Failed to get user statistics"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

    @extend_schema(
        summary="Buscar usuarios",
        description="Busca usuarios por texto con filtros",
        parameters=[
            OpenApiParameter(
                "query", OpenApiTypes.STR, description="Texto de búsqueda"
            ),
            OpenApiParameter(
                "user_type", OpenApiTypes.STR, description="Tipo de usuario"
            ),
            OpenApiParameter(
                "status", OpenApiTypes.STR, description="Estado del usuario"
            ),
            OpenApiParameter(
                "limit", OpenApiTypes.INT, description="Límite de resultados"
            ),
        ],
        responses={200: SearchUsersResponseDTO},
    )
    @action(detail=False, methods=["get"], permission_classes=[IsAuthenticated])
    def search(self, request):
        """Busca usuarios por texto."""
        try:
            # Obtener usuario solicitante
            requesting_user = self._get_requesting_user(request)

            # Verificar permisos
            if not requesting_user.is_admin:
                return Response(
                    {"error": "Insufficient permissions"},
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Obtener parámetros de búsqueda
            query = request.query_params.get("query", "")
            user_type = request.query_params.get("user_type")
            status_param = request.query_params.get("status")
            limit = request.query_params.get("limit")

            if limit:
                limit = int(limit)

            # Buscar usuarios usando el servicio de aplicación
            users = self._user_app_service.search_users(
                query=query, user_type=user_type, status=status_param, limit=limit
            )

            return Response(
                {
                    "success": True,
                    "users": [
                        {
                            "id": user.id.value,
                            "username": user.username.value,
                            "email": user.email.value,
                            "user_type": user.user_type.value,
                            "full_name": user.full_name,
                            "status": user.status.value,
                        }
                        for user in users
                    ],
                    "total": len(users),
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            logger.error(f"Error searching users: {str(e)}")
            return Response(
                {"error": "Failed to search users"},
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
