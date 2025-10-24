"""
Serializers para usuarios.
Nota: Los serializers deben ser simples, sin lógica compleja.
"""

from rest_framework import serializers
from .models import User, UserProfile
from .role_serializers import (
    RoleAssignmentSerializer,
    UserCreateSerializer as RoleUserCreateSerializer,
)


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer para el perfil de usuario."""

    class Meta:
        model = UserProfile
        fields = [
            "address",
            "city",
            "country",
            "emergency_contact_name",
            "emergency_contact_phone",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["created_at", "updated_at"]


class UserSerializer(serializers.ModelSerializer):
    """Serializer básico para usuario."""

    profile = UserProfileSerializer(read_only=True)
    full_name = serializers.ReadOnlyField()
    is_student = serializers.ReadOnlyField()
    is_teacher = serializers.ReadOnlyField()

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "first_name",
            "last_name",
            "user_type",
            "phone",
            "avatar",
            "bio",
            "birth_date",
            "full_name",
            "is_student",
            "is_teacher",
            "is_active",
            "date_joined",
            "profile",
        ]
        read_only_fields = ["id", "date_joined"]
        extra_kwargs = {"password": {"write_only": True}}


class UserCreateSerializer(serializers.ModelSerializer):
    """Serializer para crear usuarios."""

    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "password",
            "password_confirm",
            "first_name",
            "last_name",
            "user_type",
            "phone",
            "birth_date",
        ]

    def validate(self, attrs):
        if attrs["password"] != attrs["password_confirm"]:
            raise serializers.ValidationError(
                {"password": "Las contraseñas no coinciden"}
            )
        attrs.pop("password_confirm")
        return attrs


class UserUpdateSerializer(serializers.ModelSerializer):
    """Serializer para actualizar usuarios."""

    class Meta:
        model = User
        fields = ["first_name", "last_name", "phone", "avatar", "bio", "birth_date"]


class UserListSerializer(serializers.ModelSerializer):
    """Serializer simplificado para listado de usuarios."""

    class Meta:
        model = User
        fields = [
            "id",
            "username",
            "email",
            "full_name",
            "user_type",
            "avatar",
            "is_active",
        ]
