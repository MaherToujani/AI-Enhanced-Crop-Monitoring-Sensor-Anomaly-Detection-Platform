from django.apps import AppConfig


class AiAgentConfig(AppConfig):
    name = "ai_agent"

    def ready(self):
        # Import signal handlers
        from . import signals  # noqa: F401
