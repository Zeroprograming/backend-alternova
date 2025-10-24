"""
Permisos específicos para usuarios.
"""

from rest_framework import permissions


class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Permiso que solo permite al propietario o admin acceder al objeto.
    """

    def has_object_permission(self, request, view, obj):
        # Admin tiene acceso total
        if request.user and request.user.is_staff:
            return True

        # El usuario solo puede acceder a su propio perfil
        return obj == request.user


class CanManageUsers(permissions.BasePermission):
    """
    Permiso para gestionar usuarios (solo admin).
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff
