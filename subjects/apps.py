from django.apps import AppConfig


class SubjectsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "subjects"

    def ready(self):
        """Registra los signals cuando la app está lista."""
        import subjects.infrastructure.signals
