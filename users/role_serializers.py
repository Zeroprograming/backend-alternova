"""
Serializers para gestión de roles y usuarios.
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password

User = get_user_model()


class RoleAssignmentSerializer(serializers.Serializer):
    """Serializer para asignación de roles."""

    user_id = serializers.IntegerField(help_text="ID del usuario")
    role = serializers.ChoiceField(
        choices=[
            ("admin", "Administrador"),
            ("teacher", "Profesor"),
            ("student", "Estudiante"),
        ],
        help_text="Rol a asignar",
    )

    def validate_user_id(self, value):
        """Valida que el usuario exista."""
        try:
            User.objects.get(id=value, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado")
        return value


class UserCreateSerializer(serializers.Serializer):
    """Serializer para creación de usuarios."""

    username = serializers.CharField(max_length=150, help_text="Nombre de usuario")
    email = serializers.EmailField(
        required=False, allow_blank=True, help_text="Correo electrónico"
    )
    password = serializers.CharField(
        write_only=True,
        validators=[validate_password],
        help_text="Contraseña (mínimo 8 caracteres)",
    )
    first_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True, help_text="Nombre"
    )
    last_name = serializers.CharField(
        max_length=150, required=False, allow_blank=True, help_text="Apellido"
    )
    role = serializers.ChoiceField(
        choices=[
            ("admin", "Administrador"),
            ("teacher", "Profesor"),
            ("student", "Estudiante"),
        ],
        help_text="Rol del usuario",
    )

    def validate_username(self, value):
        """Valida que el username sea único."""
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Este nombre de usuario ya existe")
        return value

    def validate_email(self, value):
        """Valida que el email sea único si se proporciona."""
        if value and User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Este correo electrónico ya existe")
        return value


class UserRoleSerializer(serializers.ModelSerializer):
    """Serializer para mostrar información de usuario con rol."""

    role = serializers.CharField(source="user_type", read_only=True)
    full_name = serializers.CharField(read_only=True)
    is_active_display = serializers.BooleanField(source="is_active", read_only=True)

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "full_name",
            "role",
            "is_active_display",
            "date_joined",
            "last_login",
        ]
        read_only_fields = ["id", "date_joined", "last_login"]


class UserPermissionsSerializer(serializers.Serializer):
    """Serializer para mostrar permisos de usuario."""

    user_id = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True)
    role = serializers.CharField(read_only=True)
    permissions = serializers.ListField(
        child=serializers.CharField(), read_only=True, help_text="Lista de permisos"
    )


class RoleStatisticsSerializer(serializers.Serializer):
    """Serializer para estadísticas de roles."""

    admin = serializers.IntegerField(help_text="Número de administradores")
    teacher = serializers.IntegerField(help_text="Número de profesores")
    student = serializers.IntegerField(help_text="Número de estudiantes")
    total_active = serializers.IntegerField(help_text="Total de usuarios activos")
    total_inactive = serializers.IntegerField(help_text="Total de usuarios inactivos")


class BulkRoleAssignmentSerializer(serializers.Serializer):
    """Serializer para asignación masiva de roles."""

    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        help_text="Lista de IDs de usuarios",
    )
    role = serializers.ChoiceField(
        choices=[
            ("admin", "Administrador"),
            ("teacher", "Profesor"),
            ("student", "Estudiante"),
        ],
        help_text="Rol a asignar",
    )

    def validate_user_ids(self, value):
        """Valida que todos los usuarios existan."""
        existing_users = User.objects.filter(id__in=value, is_active=True).count()
        if existing_users != len(value):
            raise serializers.ValidationError(
                "Algunos usuarios no existen o están inactivos"
            )
        return value


class PasswordResetSerializer(serializers.Serializer):
    """Serializer para reset de contraseña."""

    user_id = serializers.IntegerField(help_text="ID del usuario")
    new_password = serializers.CharField(
        validators=[validate_password],
        help_text="Nueva contraseña",
    )

    def validate_user_id(self, value):
        """Valida que el usuario exista."""
        try:
            User.objects.get(id=value, is_active=True)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado")
        return value


class UserActivationSerializer(serializers.Serializer):
    """Serializer para activación/desactivación de usuarios."""

    user_id = serializers.IntegerField(help_text="ID del usuario")

    def validate_user_id(self, value):
        """Valida que el usuario exista."""
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("Usuario no encontrado")
        return value
