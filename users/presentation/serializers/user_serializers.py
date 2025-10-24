"""
Serializers de presentación para la capa de presentación.
Implementa la serialización de datos para la interfaz de usuario.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from typing import Optional, List, Dict, Any
from datetime import datetime

from ...domain.entities import User, UserProfile
from ...domain.value_objects import (
    UserId,
    Username,
    Email,
    Password,
    UserType,
    UserStatus,
    AcademicInfo,
)
from ...application.dto.user_dto import (
    UserDTO,
    UserProfileDTO,
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
    AcademicInfoDTO,
    StudentAcademicSummaryDTO,
    UserStatisticsDTO,
    SearchUsersDTO,
    SearchUsersResponseDTO,
    UserPermissionsDTO,
    AuditLogDTO,
    NotificationDTO,
    CreateNotificationDTO,
    NotificationResponseDTO,
)

DjangoUser = get_user_model()


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para el perfil de usuario."""

    full_address = serializers.SerializerMethodField()

    class Meta:
        model = DjangoUser.profile.related.related_model
        fields = [
            "address",
            "city",
            "country",
            "emergency_contact_name",
            "emergency_contact_phone",
            "full_address",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]

    def get_full_address(self, obj):
        """Retorna la dirección completa."""
        parts = [obj.address, obj.city, obj.country]
        return ", ".join(filter(None, parts))


class AcademicInfoSerializer(serializers.Serializer):
    """Serializer para información académica."""

    max_credits_per_semester = serializers.IntegerField(min_value=0, max_value=30)
    current_semester_credits = serializers.IntegerField(min_value=0)
    available_credits = serializers.IntegerField(read_only=True)
    academic_year = serializers.CharField(max_length=9)
    can_enroll = serializers.BooleanField(read_only=True)

    def validate(self, data):
        """Valida los datos académicos."""
        if data["current_semester_credits"] > data["max_credits_per_semester"]:
            raise serializers.ValidationError(
                "Current credits cannot exceed max credits per semester"
            )
        return data


class UserSerializer(serializers.ModelSerializer):
    """Serializer para usuarios."""

    full_name = serializers.SerializerMethodField()
    is_student = serializers.SerializerMethodField()
    is_teacher = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    academic_info = AcademicInfoSerializer(read_only=True)
    profile = UserProfileSerializer(read_only=True)

    class Meta:
        model = DjangoUser
        fields = [
            "id",
            "username",
            "email",
            "user_type",
            "first_name",
            "last_name",
            "phone",
            "is_active",
            "full_name",
            "is_student",
            "is_teacher",
            "is_admin",
            "academic_info",
            "profile",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]

    def get_full_name(self, obj):
        """Retorna el nombre completo."""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.username

    def get_is_student(self, obj):
        """Verifica si es estudiante."""
        return obj.user_type == "student"

    def get_is_teacher(self, obj):
        """Verifica si es profesor."""
        return obj.user_type == "teacher"

    def get_is_admin(self, obj):
        """Verifica si es administrador."""
        return obj.user_type == "admin"


class UserListSerializer(serializers.ModelSerializer):
    """Serializer para listado de usuarios."""

    full_name = serializers.SerializerMethodField()
    is_student = serializers.SerializerMethodField()
    is_teacher = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()

    class Meta:
        model = DjangoUser
        fields = [
            "id",
            "username",
            "email",
            "user_type",
            "first_name",
            "last_name",
            "phone",
            "is_active",
            "full_name",
            "is_student",
            "is_teacher",
            "is_admin",
            "date_joined",
        ]
        read_only_fields = ["id", "date_joined"]

    def get_full_name(self, obj):
        """Retorna el nombre completo."""
        if obj.first_name and obj.last_name:
            return f"{obj.first_name} {obj.last_name}"
        return obj.username

    def get_is_student(self, obj):
        """Verifica si es estudiante."""
        return obj.user_type == "student"

    def get_is_teacher(self, obj):
        """Verifica si es profesor."""
        return obj.user_type == "teacher"

    def get_is_admin(self, obj):
        """Verifica si es administrador."""
        return obj.user_type == "admin"


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuarios."""

    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    academic_info = AcademicInfoSerializer(required=False)

    class Meta:
        model = DjangoUser
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "user_type",
            "first_name",
            "last_name",
            "phone",
            "academic_info",
        ]

    def validate(self, data):
        """Valida los datos de creación."""
        if data["password"] != data["password_confirm"]:
            raise serializers.ValidationError("Passwords don't match")

        # Validar información académica si es estudiante
        if data["user_type"] == "student" and not data.get("academic_info"):
            data["academic_info"] = {
                "max_credits_per_semester": 18,
                "current_semester_credits": 0,
                "academic_year": "2024-1",
            }

        return data

    def create(self, validated_data):
        """Crea un nuevo usuario."""
        # Extraer información académica
        academic_info = validated_data.pop("academic_info", None)
        password_confirm = validated_data.pop("password_confirm")

        # Crear usuario
        user = DjangoUser.objects.create_user(**validated_data)

        # Crear información académica si es estudiante
        if academic_info and user.user_type == "student":
            user.max_credits_per_semester = academic_info["max_credits_per_semester"]
            user.current_semester_credits = academic_info["current_semester_credits"]
            user.academic_year = academic_info["academic_year"]
            user.save()

        return user


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar usuarios."""

    academic_info = AcademicInfoSerializer(required=False)

    class Meta:
        model = DjangoUser
        fields = ["first_name", "last_name", "phone", "user_type", "academic_info"]

    def update(self, instance, validated_data):
        """Actualiza un usuario."""
        # Extraer información académica
        academic_info = validated_data.pop("academic_info", None)

        # Actualizar campos básicos
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Actualizar información académica si es estudiante
        if academic_info and instance.user_type == "student":
            instance.max_credits_per_semester = academic_info[
                "max_credits_per_semester"
            ]
            instance.current_semester_credits = academic_info[
                "current_semester_credits"
            ]
            instance.academic_year = academic_info["academic_year"]

        instance.save()
        return instance


class LoginSerializer(serializers.Serializer):
    """Serializer para login."""

    username = serializers.CharField(max_length=150)
    password = serializers.CharField(write_only=True)
    ip_address = serializers.CharField(read_only=True)
    user_agent = serializers.CharField(read_only=True)

    def validate_username(self, value):
        """Valida el nombre de usuario."""
        if not value:
            raise serializers.ValidationError("Username is required")
        return value

    def validate_password(self, value):
        """Valida la contraseña."""
        if not value:
            raise serializers.ValidationError("Password is required")
        return value


class LoginResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de login."""

    success = serializers.BooleanField()
    user = UserSerializer(required=False)
    tokens = serializers.DictField(required=False)
    session_id = serializers.CharField(required=False)
    error = serializers.CharField(required=False)


class LogoutSerializer(serializers.Serializer):
    """Serializer para logout."""

    session_id = serializers.CharField(max_length=255)
    user_id = serializers.IntegerField(read_only=True)

    def validate_session_id(self, value):
        """Valida el ID de sesión."""
        if not value:
            raise serializers.ValidationError("Session ID is required")
        return value


class LogoutResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de logout."""

    success = serializers.BooleanField()
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)


class RefreshTokenSerializer(serializers.Serializer):
    """Serializer para refresh token."""

    refresh_token = serializers.CharField(max_length=255)

    def validate_refresh_token(self, value):
        """Valida el refresh token."""
        if not value:
            raise serializers.ValidationError("Refresh token is required")
        return value


class RefreshTokenResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de refresh token."""

    success = serializers.BooleanField()
    tokens = serializers.DictField(required=False)
    error = serializers.CharField(required=False)


class VerifyTokenSerializer(serializers.Serializer):
    """Serializer para verificar token."""

    access_token = serializers.CharField(max_length=255)

    def validate_access_token(self, value):
        """Valida el access token."""
        if not value:
            raise serializers.ValidationError("Access token is required")
        return value


class VerifyTokenResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de verificar token."""

    success = serializers.BooleanField()
    user = UserSerializer(required=False)
    error = serializers.CharField(required=False)


class RoleAssignmentSerializer(serializers.Serializer):
    """Serializer para asignación de roles."""

    user_id = serializers.IntegerField()
    new_role = serializers.ChoiceField(
        choices=[
            ("admin", "Administrador"),
            ("teacher", "Profesor"),
            ("student", "Estudiante"),
        ]
    )

    def validate_user_id(self, value):
        """Valida el ID del usuario."""
        try:
            DjangoUser.objects.get(id=value, is_active=True)
        except DjangoUser.DoesNotExist:
            raise serializers.ValidationError("User not found")
        return value

    def validate_new_role(self, value):
        """Valida el nuevo rol."""
        if value not in ["admin", "teacher", "student"]:
            raise serializers.ValidationError("Invalid role")
        return value


class RoleAssignmentResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de asignación de roles."""

    success = serializers.BooleanField()
    user = UserSerializer(required=False)
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)


class BulkRoleAssignmentSerializer(serializers.Serializer):
    """Serializer para asignación masiva de roles."""

    user_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)
    new_role = serializers.ChoiceField(
        choices=[
            ("admin", "Administrador"),
            ("teacher", "Profesor"),
            ("student", "Estudiante"),
        ]
    )

    def validate_user_ids(self, value):
        """Valida los IDs de usuarios."""
        if not value:
            raise serializers.ValidationError("User IDs are required")

        # Verificar que todos los usuarios existen
        existing_users = DjangoUser.objects.filter(
            id__in=value, is_active=True
        ).values_list("id", flat=True)

        missing_ids = set(value) - set(existing_users)
        if missing_ids:
            raise serializers.ValidationError(f"Users not found: {list(missing_ids)}")

        return value

    def validate_new_role(self, value):
        """Valida el nuevo rol."""
        if value not in ["admin", "teacher", "student"]:
            raise serializers.ValidationError("Invalid role")
        return value


class BulkRoleAssignmentResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de asignación masiva de roles."""

    success = serializers.BooleanField()
    successful_assignments = serializers.ListField(required=False)
    failed_assignments = serializers.ListField(required=False)
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)


class UserSessionSerializer(serializers.Serializer):
    """Serializer para sesiones de usuario."""

    session_id = serializers.CharField(max_length=255)
    user_id = serializers.IntegerField()
    ip_address = serializers.IPAddressField()
    user_agent = serializers.CharField(max_length=500)
    created_at = serializers.DateTimeField()
    last_activity = serializers.DateTimeField()
    is_active = serializers.BooleanField()


class UserStatisticsSerializer(serializers.Serializer):
    """Serializer para estadísticas de usuarios."""

    total_users = serializers.IntegerField()
    active_users = serializers.IntegerField()
    inactive_users = serializers.IntegerField()
    suspended_users = serializers.IntegerField()
    students = serializers.IntegerField()
    teachers = serializers.IntegerField()
    admins = serializers.IntegerField()
    activation_rate = serializers.FloatField()


class SearchUsersSerializer(serializers.Serializer):
    """Serializer para búsqueda de usuarios."""

    query = serializers.CharField(max_length=255)
    user_type = serializers.ChoiceField(
        choices=[
            ("admin", "Administrador"),
            ("teacher", "Profesor"),
            ("student", "Estudiante"),
        ],
        required=False,
    )
    status = serializers.ChoiceField(
        choices=[
            ("active", "Activo"),
            ("inactive", "Inactivo"),
            ("suspended", "Suspendido"),
        ],
        required=False,
    )
    limit = serializers.IntegerField(min_value=1, max_value=100, required=False)
    offset = serializers.IntegerField(min_value=0, required=False)


class SearchUsersResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de búsqueda de usuarios."""

    success = serializers.BooleanField()
    users = UserListSerializer(many=True, required=False)
    total = serializers.IntegerField(required=False)
    error = serializers.CharField(required=False)


class UserPermissionsSerializer(serializers.Serializer):
    """Serializer para permisos de usuario."""

    user_id = serializers.IntegerField()
    user_type = serializers.CharField(max_length=20)
    permissions = serializers.ListField(child=serializers.CharField())
    is_active = serializers.BooleanField()


class AuditLogSerializer(serializers.Serializer):
    """Serializer para logs de auditoría."""

    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    action_type = serializers.CharField(max_length=100)
    description = serializers.CharField(max_length=500)
    content_object_type = serializers.CharField(required=False)
    content_object_id = serializers.IntegerField(required=False)
    extra_data = serializers.DictField(required=False)
    created_at = serializers.DateTimeField()


class NotificationSerializer(serializers.Serializer):
    """Serializer para notificaciones."""

    id = serializers.IntegerField()
    user_id = serializers.IntegerField()
    title = serializers.CharField(max_length=200)
    message = serializers.CharField(max_length=1000)
    notification_type = serializers.CharField(max_length=50)
    is_read = serializers.BooleanField()
    read_at = serializers.DateTimeField(required=False)
    created_at = serializers.DateTimeField()


class CreateNotificationSerializer(serializers.Serializer):
    """Serializer para crear notificaciones."""

    user_id = serializers.IntegerField()
    title = serializers.CharField(max_length=200)
    message = serializers.CharField(max_length=1000)
    notification_type = serializers.ChoiceField(
        choices=[
            ("info", "Información"),
            ("warning", "Advertencia"),
            ("error", "Error"),
        ],
        default="info",
    )
    send_email = serializers.BooleanField(default=True)

    def validate_user_id(self, value):
        """Valida el ID del usuario."""
        try:
            DjangoUser.objects.get(id=value, is_active=True)
        except DjangoUser.DoesNotExist:
            raise serializers.ValidationError("User not found")
        return value


class NotificationResponseSerializer(serializers.Serializer):
    """Serializer para respuesta de notificaciones."""

    success = serializers.BooleanField()
    notification = NotificationSerializer(required=False)
    message = serializers.CharField(required=False)
    error = serializers.CharField(required=False)
