from django.contrib import admin

from .models import GlossaryEntry, Lesson, ModelSettings


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ("name", "uploaded", "file")
    search_fields = ("name", "description")
    list_filter = ("uploaded",)


@admin.register(GlossaryEntry)
class GlossaryEntryAdmin(admin.ModelAdmin):
    list_display = ("sentence", "lesson", "from_seconds", "to_seconds")
    search_fields = ("sentence", "description")
    list_filter = ("lesson",)
    raw_id_fields = ("lesson",)


@admin.register(ModelSettings)
class ModelSettingsAdmin(admin.ModelAdmin):
    list_display = ("light",)
