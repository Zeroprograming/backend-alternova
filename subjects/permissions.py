"""Permisos específicos para materias."""

from rest_framework import permissions


class IsTeacherOfSubject(permissions.BasePermission):
    """Permiso para profesores de la materia."""

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.teacher == request.user
