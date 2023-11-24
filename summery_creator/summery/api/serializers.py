from rest_framework import serializers

from summery_creator.summery.models import GlossaryEntry, Lesson


class LessonSerializer(serializers.ModelSerializer):
    text = serializers.CharField(
        source="audio_text", allow_null=True, allow_blank=True, required=False
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


class GlossaryEntrySerializer(serializers.ModelSerializer):
    class Meta:
        model = GlossaryEntry
        fields = ["sentence", "description"]


class FullLessonSerializer(serializers.ModelSerializer):
    entries = GlossaryEntrySerializer(many=True)

    class Meta:
        model = Lesson
        fields = ["id", "name", "uploaded", "file", "audio_text", "entries"]
        extra_kwargs = {
            "id": {"read_only": True},
            "uploaded": {"read_only": True},
        }


class CallbackSerializer(serializers.Serializer):
    type = serializers.ChoiceField(choices=["trans", "terms"])
    data = serializers.CharField()
