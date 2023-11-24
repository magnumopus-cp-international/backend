from django.core.cache import cache
from django.db.models.signals import post_save
from django.dispatch import receiver

from summery_creator.summery.models import Lesson, ModelSettings
from summery_creator.summery.tasks import run_report_create, send_file_to_ml


@receiver(post_save, sender=Lesson)
def process_lesson(sender, instance: Lesson, created, **kwargs):
    if created:
        send_file_to_ml.apply_async(
            kwargs={
                "lesson_id": instance.id,
            },
            countdown=1,
        )
    elif (
        instance.name
        and instance.description
        and instance.audio_text
        and not instance.report
    ):
        run_report_create.apply_async(
            kwargs={
                "lesson_id": instance.id,
            },
            countdown=1,
        )


@receiver(post_save, sender=ModelSettings)
def invalidate_model_settings_cache(sender, instance, **kwargs):
    cache.delete("model_settings")
