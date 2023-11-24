import json

from rest_framework import serializers

from summery_creator.summery.models import GlossaryEntry, Lesson


class LessonSerializer(serializers.ModelSerializer):
    text = serializers.CharField(
        source="audio_text",
        allow_null=True,
        allow_blank=True,
        required=False,
        write_only=True,
    )

    class Meta:
        model = Lesson
        fields = ["id", "name", "uploaded", "file", "text"]
        extra_kwargs = {
            "uploaded": {"read_only": True},
            "id": {"read_only": True},
            "file": {"write_only": True},
            "text": {"write_only": True, "required": False},
        }


class ListGlossaryEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = GlossaryEntry
        fields = [
            "lesson_id",
            "slug",
            "sentence",
            "description",
        ]


class GlossaryEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = GlossaryEntry
        fields = [
            "sentence",
            "description",
            "from_seconds",
            "to_seconds",
            "entry_sentence",
        ]


class FullGlossaryEntrySerializer(serializers.ModelSerializer):
    text = serializers.CharField(source="lesson.audio_text", read_only=True)

    class Meta:
        model = GlossaryEntry
        fields = [
            "lesson_id",
            "sentence",
            "description",
            "from_seconds",
            "to_seconds",
            "entry_sentence",
            "text",
        ]


class FullLessonSerializer(serializers.ModelSerializer):
    entries = GlossaryEntrySerializer(many=True)

    class Meta:
        model = Lesson
        fields = [
            "id",
            "name",
            "description",
            "uploaded",
            "file",
            "audio_text",
            "entries",
            "report",
        ]
        extra_kwargs = {
            "id": {"read_only": True},
            "uploaded": {"read_only": True},
        }


class CallbackSerializer(serializers.Serializer):
    type = serializers.ChoiceField(
        choices=["trans", "trans_end", "terms", "time", "summary", "name"]
    )
    data = serializers.CharField()

    def validate_data(self, value):
        try:
            return json.loads(value)
        except json.decoder.JSONDecodeError:
            return value
