import uuid

from django.db import models

from summery_creator.common.models import Singleton, SlugModel


class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(null=True)
    audio_text = models.TextField(null=True)
    file = models.FileField(upload_to="uploads/", null=True)
    uploaded = models.DateTimeField(auto_now_add=True)
    report = models.FileField(upload_to="reports/", null=True)

    class Meta:
        ordering = ["-uploaded"]

    def __str__(self):
        return self.name if self.name else "New upload"


class GlossaryEntry(SlugModel):
    lesson = models.ForeignKey(
        "Lesson", related_name="entries", on_delete=models.CASCADE
    )
    sentence = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(null=True)

    # time entry
    from_seconds = models.IntegerField(null=True)
    to_seconds = models.IntegerField(null=True)
    entry_sentence = models.CharField(null=True, blank=True)

    def __str__(self):
        return self.sentence

    class Meta:
        ordering = ["-from_seconds"]

    class SlugMeta:
        slug_length = 10


class ModelSettings(Singleton):
    light = models.BooleanField(default=False)

    def __str__(self):
        return "light model" if self.light else "medium model"
