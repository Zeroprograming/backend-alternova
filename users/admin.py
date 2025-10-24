from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, UserProfile


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin personalizado para el modelo User."""

    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "user_type",
        "is_staff",
        "is_active",
        "date_joined",
    )
    list_filter = (
        "user_type",
        "is_staff",
        "is_active",
        "date_joined",
    )
    search_fields = ("username", "email", "first_name", "last_name")
    ordering = ("-date_joined",)

    fieldsets = (
        (None, {"fields": ("username", "password")}),
        ("Información Personal", {"fields": ("first_name", "last_name", "email")}),
        (
            "Permisos y Roles",
            {
                "fields": (
                    "user_type",
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Información Académica",
            {
                "fields": (
                    "max_credits_per_semester",
                    "current_semester_credits",
                    "academic_year",
                )
            },
        ),
        ("Fechas Importantes", {"fields": ("last_login", "date_joined")}),
    )

    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": (
                    "username",
                    "email",
                    "password1",
                    "password2",
                    "user_type",
                    "is_staff",
                    "is_active",
                ),
            },
        ),
    )

    readonly_fields = ("date_joined", "last_login")


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin para el modelo UserProfile."""

    list_display = ("user", "city", "country", "created_at")
    list_filter = ("country", "created_at")
    search_fields = ("user__username", "user__email", "city")
    readonly_fields = ("created_at", "updated_at")

    fieldsets = (
        (None, {"fields": ("user",)}),
        (
            "Información de Contacto",
            {
                "fields": (
                    "address",
                    "city",
                    "country",
                )
            },
        ),
        (
            "Contacto de Emergencia",
            {
                "fields": (
                    "emergency_contact_name",
                    "emergency_contact_phone",
                )
            },
        ),
        ("Fechas", {"fields": ("created_at", "updated_at")}),
    )
