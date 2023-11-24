from django.db.models.signals import post_save
from django.dispatch import receiver

from summery_creator.summery.models import Lesson
from summery_creator.summery.tasks import send_file_to_ml


@receiver(post_save, sender=Lesson)
def process_lesson(sender, instance: Lesson, created, **kwargs):
    if created:
        send_file_to_ml.apply_async(
            kwargs={
                "lesson_id": instance.id,
            },
            countdown=1,
        )
