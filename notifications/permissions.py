"""Permisos para notificaciones."""

from rest_framework import permissions


class IsNotificationOwner(permissions.BasePermission):
    """Solo el dueño puede ver/modificar sus notificaciones."""

    def has_object_permission(self, request, view, obj):
        return obj.user == request.user
