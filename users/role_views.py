"""
Vistas para gestión de roles y usuarios.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes
from .models import User
from .serializers import UserSerializer, UserCreateSerializer, RoleAssignmentSerializer
from .permissions import CanManageRoles, IsAdminUser
from .role_services import RoleManagementService, UserManagementService
import logging

logger = logging.getLogger(__name__)


class RoleManagementViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión de roles de usuarios.
    Solo administradores pueden acceder.
    """

    permission_classes = [IsAuthenticated, CanManageRoles]

    @extend_schema(
        summary="Asignar rol a usuario",
        description="Asigna un nuevo rol a un usuario específico",
        tags=["Administración - Roles"],
        request=RoleAssignmentSerializer,
    )
    @action(detail=False, methods=["post"])
    def assign_role(self, request):
        """Asigna un rol a un usuario."""
        serializer = RoleAssignmentSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = RoleManagementService.assign_role(
                user_id=serializer.validated_data["user_id"],
                new_role=serializer.validated_data["role"],
                requesting_user=request.user,
            )

            return Response(
                {
                    "message": f"Rol {serializer.validated_data['role']} asignado exitosamente",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Asignación masiva de roles",
        description="Asigna un rol a múltiples usuarios",
        tags=["Administración - Roles"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "user_ids": {
                        "type": "array",
                        "items": {"type": "integer"},
                        "description": "Lista de IDs de usuarios",
                    },
                    "role": {
                        "type": "string",
                        "enum": ["admin", "teacher", "student"],
                        "description": "Rol a asignar",
                    },
                },
                "required": ["user_ids", "role"],
            }
        },
    )
    @action(detail=False, methods=["post"])
    def bulk_assign_role(self, request):
        """Asignación masiva de roles."""
        user_ids = request.data.get("user_ids", [])
        role = request.data.get("role")

        if not user_ids or not role:
            return Response(
                {"error": "Se requieren user_ids y role"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            updated_users = RoleManagementService.bulk_assign_role(
                user_ids=user_ids,
                new_role=role,
                requesting_user=request.user,
            )

            return Response(
                {
                    "message": f"Rol {role} asignado a {len(updated_users)} usuarios",
                    "updated_users": UserSerializer(updated_users, many=True).data,
                },
                status=status.HTTP_200_OK,
            )

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Listar usuarios por rol",
        description="Obtiene todos los usuarios de un rol específico",
        tags=["Administración - Roles"],
        parameters=[
            OpenApiParameter(
                name="role",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Rol a filtrar",
                required=True,
                enum=["admin", "teacher", "student"],
            ),
        ],
    )
    @action(detail=False, methods=["get"])
    def users_by_role(self, request):
        """Lista usuarios por rol."""
        role = request.query_params.get("role")

        if not role:
            return Response(
                {"error": "Se requiere parámetro role"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            users = RoleManagementService.get_users_by_role(role)
            serializer = UserSerializer(users, many=True)

            return Response(
                {
                    "role": role,
                    "count": users.count(),
                    "users": serializer.data,
                }
            )

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Estadísticas de roles",
        description="Obtiene estadísticas de distribución de roles",
        tags=["Administración - Roles"],
    )
    @action(detail=False, methods=["get"])
    def role_statistics(self, request):
        """Obtiene estadísticas de roles."""
        stats = RoleManagementService.get_role_statistics()
        return Response(stats)

    @extend_schema(
        summary="Permisos de usuario",
        description="Obtiene los permisos de un usuario específico",
        tags=["Administración - Roles"],
        parameters=[
            OpenApiParameter(
                name="user_id",
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description="ID del usuario",
                required=True,
            ),
        ],
    )
    @action(detail=False, methods=["get"])
    def user_permissions(self, request):
        """Obtiene permisos de un usuario."""
        user_id = request.query_params.get("user_id")

        if not user_id:
            return Response(
                {"error": "Se requiere parámetro user_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(id=user_id, is_active=True)
            permissions = RoleManagementService.get_user_permissions(user)

            return Response(
                {
                    "user": {
                        "id": user.id,
                        "username": user.username,
                        "role": user.user_type,
                    },
                    "permissions": permissions,
                }
            )

        except User.DoesNotExist:
            return Response(
                {"error": "Usuario no encontrado"},
                status=status.HTTP_404_NOT_FOUND,
            )


class UserManagementViewSet(viewsets.ViewSet):
    """
    ViewSet para gestión general de usuarios.
    Solo administradores pueden acceder.
    """

    permission_classes = [IsAuthenticated, IsAdminUser]

    @extend_schema(
        summary="Crear usuario",
        description="Crea un nuevo usuario con rol específico",
        tags=["Administración - Usuarios"],
        request=UserCreateSerializer,
    )
    @action(detail=False, methods=["post"])
    def create_user(self, request):
        """Crea un nuevo usuario."""
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            user = UserManagementService.create_user_with_role(
                user_data=serializer.validated_data,
                role=serializer.validated_data["role"],
                requesting_user=request.user,
            )

            return Response(
                {
                    "message": f"Usuario {user.username} creado exitosamente",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_201_CREATED,
            )

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Desactivar usuario",
        description="Desactiva un usuario del sistema",
        tags=["Administración - Usuarios"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "ID del usuario"},
                },
                "required": ["user_id"],
            }
        },
    )
    @action(detail=False, methods=["post"])
    def deactivate_user(self, request):
        """Desactiva un usuario."""
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"error": "Se requiere user_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = UserManagementService.deactivate_user(user_id, request.user)

            return Response(
                {
                    "message": f"Usuario {user.username} desactivado exitosamente",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Activar usuario",
        description="Activa un usuario del sistema",
        tags=["Administración - Usuarios"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "ID del usuario"},
                },
                "required": ["user_id"],
            }
        },
    )
    @action(detail=False, methods=["post"])
    def activate_user(self, request):
        """Activa un usuario."""
        user_id = request.data.get("user_id")

        if not user_id:
            return Response(
                {"error": "Se requiere user_id"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = UserManagementService.activate_user(user_id, request.user)

            return Response(
                {
                    "message": f"Usuario {user.username} activado exitosamente",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Resetear contraseña",
        description="Resetea la contraseña de un usuario",
        tags=["Administración - Usuarios"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "user_id": {"type": "integer", "description": "ID del usuario"},
                    "new_password": {
                        "type": "string",
                        "description": "Nueva contraseña",
                    },
                },
                "required": ["user_id", "new_password"],
            }
        },
    )
    @action(detail=False, methods=["post"])
    def reset_password(self, request):
        """Resetea la contraseña de un usuario."""
        user_id = request.data.get("user_id")
        new_password = request.data.get("new_password")

        if not user_id or not new_password:
            return Response(
                {"error": "Se requieren user_id y new_password"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = UserManagementService.reset_user_password(
                user_id, new_password, request.user
            )

            return Response(
                {
                    "message": f"Contraseña reseteada para {user.username}",
                    "user": UserSerializer(user).data,
                },
                status=status.HTTP_200_OK,
            )

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
