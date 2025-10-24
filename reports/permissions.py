"""Permisos para reportes."""

from rest_framework import permissions


class CanGenerateReports(permissions.BasePermission):
    """Permiso para generar reportes."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and (request.user.is_staff or request.user.is_teacher)
        )


class IsReportOwner(permissions.BasePermission):
    """Solo el dueño puede ver/descargar sus reportes."""

    def has_object_permission(self, request, view, obj):
        if request.user.is_staff:
            return True
        return obj.generated_by == request.user
