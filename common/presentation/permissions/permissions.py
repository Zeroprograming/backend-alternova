"""
Permisos personalizados reutilizables para toda la aplicación.
"""

from rest_framework import permissions


class IsOwner(permissions.BasePermission):
    """
    Permiso que solo permite a los propietarios del objeto editarlo.
    """

    def has_object_permission(self, request, view, obj):
        # Los permisos de lectura están permitidos para cualquier request
        if request.method in permissions.SAFE_METHODS:
            return True

        # Verificar si el objeto tiene un campo 'created_by' o 'user'
        if hasattr(obj, "created_by"):
            return obj.created_by == request.user
        elif hasattr(obj, "user"):
            return obj.user == request.user

        return False


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite lectura a todos, pero escritura solo al propietario.
    """

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True

        if hasattr(obj, "created_by"):
            return obj.created_by == request.user
        elif hasattr(obj, "user"):
            return obj.user == request.user

        return False


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Permiso que permite lectura a todos, pero escritura solo a administradores.
    """

    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class IsActiveUser(permissions.BasePermission):
    """
    Permiso que solo permite acceso a usuarios activos.
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_active


class IsTeacherOrAdmin(permissions.BasePermission):
    """
    Permiso específico para profesores o administradores.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or getattr(request.user, "is_teacher", False))
        )


class IsStudentOrAdmin(permissions.BasePermission):
    """
    Permiso específico para estudiantes o administradores.
    """

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or getattr(request.user, "is_student", False))
        )
