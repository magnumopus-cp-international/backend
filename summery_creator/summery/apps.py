from django.apps import AppConfig


class SummeryConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "summery_creator.summery"

    def ready(self):
        import summery_creator.summery.signals  # noqa
