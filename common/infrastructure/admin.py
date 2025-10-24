"""
Configuración del admin para modelos de common.
"""

from django.contrib import admin
from .audit_models import AuditLog, UserSession


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin para registros de auditoría."""

    list_display = [
        "id",
        "user",
        "action_type",
        "description",
        "ip_address",
        "created_at",
    ]
    list_filter = ["action_type", "created_at"]
    search_fields = ["user__username", "description", "ip_address"]
    readonly_fields = [
        "user",
        "action_type",
        "description",
        "ip_address",
        "user_agent",
        "content_type",
        "object_id",
        "extra_data",
        "created_at",
    ]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]

    def has_add_permission(self, request):
        """No permitir agregar manualmente."""
        return False

    def has_delete_permission(self, request, obj=None):
        """Solo superuser puede eliminar logs."""
        return request.user.is_superuser


@admin.register(UserSession)
class UserSessionAdmin(admin.ModelAdmin):
    """Admin para sesiones de usuario."""

    list_display = [
        "id",
        "user",
        "ip_address",
        "is_active",
        "created_at",
        "last_activity",
        "expires_at",
    ]
    list_filter = ["is_active", "created_at"]
    search_fields = ["user__username", "ip_address"]
    readonly_fields = [
        "user",
        "access_token",
        "refresh_token",
        "ip_address",
        "user_agent",
        "created_at",
        "last_activity",
        "expires_at",
    ]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]

    def has_add_permission(self, request):
        """No permitir agregar manualmente."""
        return False
