"""
Views para usuarios.
Nota: Las views deben ser simples, delegar lógica a services.py
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiExample
from drf_spectacular.types import OpenApiTypes
from common.presentation.permissions.permissions import IsAdminOrReadOnly
from ...infrastructure.models import User
from ...presentation.serializers.legacy_serializers import (
    UserSerializer,
    UserListSerializer,
    UserCreateSerializer,
    UserUpdateSerializer,
)
from ...application.services.legacy_services import UserService
from ...presentation.permissions.permissions import IsOwnerOrAdmin
import logging

logger = logging.getLogger(__name__)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet para gestión de usuarios con validaciones y permisos granulares.
    La lógica compleja está delegada en UserService.
    """

    queryset = User.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        """Retorna el serializer apropiado según la acción."""
        if self.action == "list":
            return UserListSerializer
        elif self.action == "create":
            return UserCreateSerializer
        elif self.action in ["update", "partial_update"]:
            return UserUpdateSerializer
        return UserSerializer

    def get_permissions(self):
        """Permisos personalizados por acción."""
        if self.action == "create":
            # Cualquiera puede registrarse
            return [AllowAny()]
        elif self.action == "destroy":
            # Solo admin puede eliminar
            return [IsAuthenticated(), IsAdminUser()]
        elif self.action in ["update", "partial_update"]:
            # Solo el owner o admin pueden actualizar
            return [IsAuthenticated(), IsOwnerOrAdmin()]
        elif self.action == "list":
            # Solo admin puede listar todos los usuarios
            return [IsAuthenticated(), IsAdminUser()]
        return super().get_permissions()

    def get_queryset(self):
        """Filtrar queryset según el tipo de usuario."""
        user = self.request.user

        # Admin ve todos los usuarios
        if user.is_staff:
            return User.objects.all()

        # Usuarios normales solo ven usuarios activos
        return User.objects.filter(is_active=True)

    @extend_schema(
        summary="Listar usuarios",
        description="Lista todos los usuarios (solo admin). Soporta filtros por tipo.",
        tags=["Usuarios"],
        parameters=[
            OpenApiParameter(
                name="user_type",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Filtrar por tipo de usuario (student, teacher, admin)",
                required=False,
                enum=["student", "teacher", "admin"],
            ),
            OpenApiParameter(
                name="search",
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description="Buscar por nombre, email o username",
                required=False,
            ),
        ],
    )
    def list(self, request):
        """Enrutar a service para listar usuarios."""
        # Extraer parámetros
        user_type = request.query_params.get("user_type")
        search_term = request.query_params.get("search")

        # Delegar a service
        queryset = UserService.list_users(request.user, user_type, search_term)

        # Paginación
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = UserListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = UserListSerializer(queryset, many=True)
        return Response(serializer.data)

    @extend_schema(
        summary="Obtener usuario",
        description="Obtiene los detalles de un usuario específico",
        tags=["Usuarios"],
    )
    def retrieve(self, request, pk=None):
        """Enrutar a service para obtener usuario."""
        try:
            # Delegar a service
            user, show_full_details = UserService.retrieve_user(pk, request.user)

            # Serializar según permisos
            if show_full_details:
                serializer = UserSerializer(user)
            else:
                serializer = UserListSerializer(user)

            return Response(serializer.data)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_404_NOT_FOUND)

    @extend_schema(
        summary="Crear usuario",
        description="Registra un nuevo usuario en el sistema",
        tags=["Usuarios"],
        examples=[
            OpenApiExample(
                "Ejemplo de registro",
                value={
                    "username": "estudiante1",
                    "email": "estudiante@example.com",
                    "password": "Password123!",
                    "password_confirm": "Password123!",
                    "first_name": "Juan",
                    "last_name": "Pérez",
                    "user_type": "student",
                },
                request_only=True,
            ),
        ],
    )
    def create(self, request):
        """Enrutar a service para crear usuario."""
        # Validar datos con serializer
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Delegar TODO a service
            user = UserService.create_user(**serializer.validated_data)
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Actualizar usuario completo",
        description="Actualiza todos los campos de un usuario (requiere todos los datos)",
        tags=["Usuarios"],
    )
    def update(self, request, pk=None):
        """Enrutar a service para actualizar usuario."""
        # Obtener usuario
        user = self.get_object()

        # Validar y serializar datos
        serializer = UserUpdateSerializer(user, data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            # Delegar TODO a service
            updated_user = UserService.update_user(
                user, serializer.validated_data, request.user
            )
            return Response(UserSerializer(updated_user).data)

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Actualizar usuario parcial",
        description="Actualiza campos específicos del usuario",
        tags=["Usuarios"],
    )
    def partial_update(self, request, pk=None):
        """Enrutar a service para actualización parcial."""
        # Obtener usuario
        user = self.get_object()

        # Validar datos
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        try:
            # Delegar TODO a service
            updated_user = UserService.partial_update_user(
                user, serializer.validated_data, request.user
            )
            return Response(UserSerializer(updated_user).data)

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Eliminar usuario",
        description="Desactiva un usuario (soft delete). Solo administradores.",
        tags=["Usuarios"],
    )
    def destroy(self, request, pk=None):
        """Enrutar a service para eliminar usuario."""
        # Obtener usuario
        user = self.get_object()

        try:
            # Delegar TODO a service
            UserService.delete_user(user, request.user)
            return Response(
                {"message": "Usuario desactivado exitosamente"},
                status=status.HTTP_204_NO_CONTENT,
            )

        except PermissionError as e:
            return Response({"error": str(e)}, status=status.HTTP_403_FORBIDDEN)
        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    # ========== Acciones personalizadas ==========

    @extend_schema(
        summary="Perfil del usuario actual",
        description="Obtiene el perfil del usuario autenticado",
        tags=["Usuarios"],
    )
    @action(detail=False, methods=["get"])
    def me(self, request):
        """Obtener perfil del usuario actual."""
        serializer = UserSerializer(request.user)
        return Response(serializer.data)

    @extend_schema(
        summary="Cambiar tipo de usuario",
        description="Cambia el tipo de un usuario (solo admin)",
        tags=["Usuarios"],
        request={
            "application/json": {
                "type": "object",
                "properties": {
                    "user_type": {
                        "type": "string",
                        "enum": ["student", "teacher", "admin"],
                    }
                },
                "required": ["user_type"],
            }
        },
    )
    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsAdminUser]
    )
    def change_type(self, request, pk=None):
        """Enrutar a service para cambiar tipo de usuario."""
        user = self.get_object()
        new_type = request.data.get("user_type")

        if not new_type:
            return Response(
                {"error": "user_type es requerido"}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            # Delegar a service
            updated_user = UserService.change_user_type(user, new_type)
            return Response(UserSerializer(updated_user).data)

        except ValueError as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    @extend_schema(
        summary="Activar usuario",
        description="Reactiva un usuario desactivado (solo admin)",
        tags=["Usuarios"],
    )
    @action(
        detail=True, methods=["post"], permission_classes=[IsAuthenticated, IsAdminUser]
    )
    def activate(self, request, pk=None):
        """Enrutar a service para activar usuario."""
        user = self.get_object()

        if user.is_active:
            return Response(
                {"error": "El usuario ya está activo"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Delegar a service
        UserService.activate_user(user)

        return Response(
            {"message": "Usuario activado exitosamente"}, status=status.HTTP_200_OK
        )
