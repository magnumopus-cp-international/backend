from django_elasticsearch_dsl import Document
from django_elasticsearch_dsl.registries import registry

from summery_creator.summery.models import GlossaryEntry, Lesson


@registry.register_document
class LessonDocument(Document):
    class Index:
        name = "lessons"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = Lesson
        fields = [
            "name",
            "audio_text",
        ]

    def prepare_audio_text(self, instance):
        return instance.audio_text if instance.audio_text else ""

    def prepare_name(self, instance):
        return instance.name if instance.name else ""


@registry.register_document
class GlossaryEntryDocument(Document):
    class Index:
        name = "answers"
        settings = {"number_of_shards": 1, "number_of_replicas": 0}

    class Django:
        model = GlossaryEntry
        fields = [
            "sentence",
            "description",
        ]

    def prepare_sentence(self, instance):
        return instance.sentence if instance.sentence else ""

    def prepare_description(self, instance):
        return instance.description if instance.description else ""
