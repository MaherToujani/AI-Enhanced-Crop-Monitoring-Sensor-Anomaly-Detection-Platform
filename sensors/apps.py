from django.apps import AppConfig


class SensorsConfig(AppConfig):
    name = "sensors"

    def ready(self):
        # Import signal handlers
        from . import signals  # noqa: F401
