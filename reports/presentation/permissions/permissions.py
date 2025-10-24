"""
Permisos específicos para reportes CSV.
"""

from rest_framework import permissions


class CanGenerateStudentReport(permissions.BasePermission):
    """
    Permite generar reportes de estudiantes.
    - El propio estudiante puede generar su reporte
    - Los administradores pueden generar cualquier reporte
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Si es administrador, puede generar cualquier reporte
        if request.user.is_staff:
            return True

        # Si es el propio estudiante, puede generar su reporte
        if hasattr(obj, "id") and obj.id == request.user.id:
            return True

        return False


class CanGenerateTeacherReport(permissions.BasePermission):
    """
    Permite generar reportes de profesores.
    - El propio profesor puede generar su reporte
    - Los administradores pueden generar cualquier reporte
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        # Si es administrador, puede generar cualquier reporte
        if request.user.is_staff:
            return True

        # Si es el propio profesor, puede generar su reporte
        if hasattr(obj, "id") and obj.id == request.user.id:
            return True

        return False


class CanGenerateGeneralReport(permissions.BasePermission):
    """
    Permite generar reportes generales del sistema.
    - Solo administradores pueden generar reportes generales
    """

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_staff
