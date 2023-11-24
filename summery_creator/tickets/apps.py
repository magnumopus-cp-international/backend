from django.apps import AppConfig


class TicketsConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "summery_creator.tickets"

    def ready(self):
        try:
            import summery_creator.tickets.signals  # noqa F401
        except ImportError:
            pass
