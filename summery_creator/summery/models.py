import uuid

from django.db import models


class Lesson(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=500, blank=True, null=True)
    audio_text = models.TextField(null=True)
    file = models.FileField(upload_to="uploads/", null=True)
    uploaded = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class GlossaryEntry(models.Model):
    lesson = models.ForeignKey(
        "Lesson", related_name="entries", on_delete=models.CASCADE
    )
    sentence = models.CharField(max_length=500, blank=True, null=True)
    description = models.TextField(null=True)

    def __str__(self):
        return self.sentence
