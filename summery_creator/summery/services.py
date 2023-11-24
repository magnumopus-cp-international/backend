import chardet
import textract
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.core.cache import cache
from django.core.files.base import ContentFile
from django.db.models import Case, When
from django.http import QueryDict
from elasticsearch_dsl import Q as ES_Q
from fpdf import FPDF, TitleStyle
from textract.exceptions import ExtensionNotSupported

from summery_creator.summery.api.serializers import (
    LessonSerializer,
    ListGlossaryEntrySerializer,
)
from summery_creator.summery.documents import GlossaryEntryDocument, LessonDocument
from summery_creator.summery.models import GlossaryEntry, Lesson, ModelSettings


def send_message(lesson_id, data):
    channel_layer = get_channel_layer()
    if type(data) is QueryDict:
        data = data.dict()
        if data["type"] == "terms":
            term, definition = extract_term_and_definition(data["data"])
            if term:
                data["data"] = {"sentence": term, "definition": definition}
            else:
                return
    async_to_sync(channel_layer.group_send)(
        f"lesson_{lesson_id}", {"type": "message", "data": data}
    )


def get_model_settings():
    """
    This function tries to get the ModelSettings instance from the cache.
    If it's not available in the cache, it retrieves it from the database,
    saves it to the cache, and then returns it.
    """
    settings = cache.get("model_settings")
    if not settings:
        settings, created = ModelSettings.objects.get_or_create(pk=1)
        cache.set("model_settings", settings.light)
    return settings


def extract_file_text(file: str) -> str:
    try:
        text = textract.process(file)
    except ExtensionNotSupported:
        try:
            rawdata = open(file, "rb").read()
            enc = chardet.detect(rawdata)
            with open(file, encoding=enc["encoding"]) as file:
                text = file.read()
        except Exception:
            return ""
    if type(text) is bytes:
        return text.decode()
    return text


def extract_term_and_definition(input_string):
    # Remove leading hyphen if it exists
    input_string = input_string.lstrip("-").strip()

    try:
        # Split the string on the colon
        parts = input_string.split(":")

        # If there's no colon, we return None for both term and definition
        if len(parts) == 1:
            return None, None

        # The term is the first part, and the definition is the join of the remaining parts
        term = parts[0].strip()
        definition = ":".join(parts[1:]).strip()

        return term, definition
    except Exception as e:
        # If an error occurs, we return the error message
        return str(e), None


def search_documents(query: str):
    lesson_search_query = ES_Q(
        "bool",
        should=[
            ES_Q(
                "multi_match",
                query=query,
                fields=["name", "audio_text"],
                type="best_fields",
            ),
            ES_Q("match_phrase_prefix", name=query),
            ES_Q("wildcard", name=f"*{query}*"),
            ES_Q("wildcard", audio_text=f"*{query}*"),
        ],
        minimum_should_match=1,
    )

    glossary_search_query = ES_Q(
        "bool",
        should=[
            ES_Q(
                "multi_match",
                query=query,
                fields=["sentence", "description"],
                type="best_fields",
            ),
            ES_Q("match_phrase_prefix", sentence=query),
            ES_Q("wildcard", sentence=f"*{query}*"),
            ES_Q("wildcard", description=f"*{query}*"),
        ],
        minimum_should_match=1,
    )

    # Perform the search for each document type
    lesson_search = LessonDocument.search().query(lesson_search_query)
    glossary_search = GlossaryEntryDocument.search().query(glossary_search_query)

    lesson_response = lesson_search.execute()
    glossary_response = glossary_search.execute()

    # Combine the search results with their scores for ordering
    lesson_hits = [(hit.meta.id, hit.meta.score) for hit in lesson_response]
    glossary_hits = [(hit.meta.id, hit.meta.score) for hit in glossary_response]

    # Create a list of IDs from the hits for each model
    lesson_ids = [hit[0] for hit in lesson_hits]
    glossary_ids = [hit[0] for hit in glossary_hits]

    # Get the querysets ordered by the Elasticsearch score
    lessons_queryset = Lesson.objects.filter(pk__in=lesson_ids).order_by(
        Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(lesson_ids)])
    )
    glossary_queryset = GlossaryEntry.objects.filter(pk__in=glossary_ids).order_by(
        Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(glossary_ids)])
    )

    lesson_serializer = LessonSerializer(lessons_queryset, many=True)
    glossary_serializer = ListGlossaryEntrySerializer(glossary_queryset, many=True)
    glossary_data_by_id = {item["sentence"]: item for item in glossary_serializer.data}
    lesson_data_by_id = {str(item["id"]): item for item in lesson_serializer.data}
    glossary_hits = [(hit.sentence, hit.meta.score) for hit in glossary_response]

    # Now you can attempt to combine the data with the corrected keys
    combined_serialized_data = []
    for hit_id, _ in sorted(
        lesson_hits + glossary_hits, key=lambda x: x[1], reverse=True
    ):
        lesson_data = lesson_data_by_id.get(hit_id)
        glossary_data = glossary_data_by_id.get(hit_id)
        if lesson_data:
            combined_serialized_data.append(lesson_data)
        elif glossary_data:
            combined_serialized_data.append(glossary_data)

    return combined_serialized_data


def search_glossary_entries(query: str, queryset):
    # Define the search query for glossary entries
    glossary_search_query = ES_Q(
        "bool",
        should=[
            ES_Q(
                "multi_match",
                query=query,
                fields=["sentence", "description"],
                type="best_fields",
            ),
            ES_Q("match_phrase_prefix", sentence=query),
            ES_Q("wildcard", sentence=f"*{query}*"),
            ES_Q("wildcard", description=f"*{query}*"),
        ],
        minimum_should_match=1,
    )

    # Perform the search for glossary entries
    glossary_search = GlossaryEntryDocument.search().query(glossary_search_query)
    glossary_response = glossary_search.execute()

    # Process the search results and extract the IDs and scores
    glossary_hits = [(hit.meta.id, hit.meta.score) for hit in glossary_response]

    # Create a list of IDs from the hits
    glossary_ids = [hit[0] for hit in glossary_hits]

    # Filter the passed queryset by the IDs obtained from the search results
    filtered_queryset = queryset.filter(pk__in=glossary_ids).order_by(
        Case(*[When(pk=pk, then=pos) for pos, pk in enumerate(glossary_ids)])
    )

    # Serialize the filtered queryset
    glossary_serializer = ListGlossaryEntrySerializer(filtered_queryset, many=True)

    # Return the serialized data
    return glossary_serializer.data


class PDF(FPDF):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_font(
            "DejaVu", "", "/usr/share/fonts/TTF/DejaVuSansCondensed.ttf", uni=True
        )
        self.add_font(
            "DejaVu", "B", "/usr/share/fonts/TTF/DejaVuSansCondensed-Bold.ttf", uni=True
        )


def create_lesson_pdf(lesson):
    pdf = PDF()
    pdf.add_page()

    pdf.set_section_title_styles(
        level0=TitleStyle(
            font_family="DejaVu",
            font_style="B",
            font_size_pt=24,
            color=0,
            underline=False,
            t_margin=10,
            l_margin=10,
            b_margin=10,
        ),
        level1=TitleStyle(
            font_family="DejaVu",
            font_style="B",
            font_size_pt=18,
            color=0,
            underline=False,
            t_margin=10,
            l_margin=10,
            b_margin=10,
        ),
    )

    # Title as a section
    pdf.set_xy(0, 10)  # Set position for the title to be centered
    pdf.set_font("DejaVu", "B", 24)
    pdf.cell(210, 10, lesson.name, ln=True, align="C")  # Title centered

    # Description
    pdf.set_font("DejaVu", "", 12)
    pdf.multi_cell(0, 10, lesson.description)
    pdf.ln(10)

    for entry in lesson.entries.all():
        pdf.set_font("DejaVu", "B", 12)
        # Start a new section for the entry
        pdf.start_section(entry.sentence, level=1)
        if entry.entry_sentence and entry.entry_sentence in lesson.audio_text:
            link = pdf.add_link()
            # Set a link for the section title
            pdf.set_link(link)
            # Calculate the position where the entry_sentence is found within audio_text
            start_pos = lesson.audio_text.find(entry.entry_sentence)
            if start_pos >= 0:
                # Ideally, you would calculate the y position corresponding to the start_pos.
                # This is a placeholder to demonstrate the concept.
                y_position = pdf.get_y()
                pdf.set_link(link, y=y_position)
        # Section title will be added automatically by start_section, so no need to add another cell.
        pdf.set_font("DejaVu", "", 12)
        pdf.multi_cell(0, 10, entry.description)
        pdf.ln()

    # Audio text (if exists)
    if lesson.audio_text:
        pdf.multi_cell(0, 10, lesson.audio_text)

    # Output PDF to string
    pdf_output = pdf.output(dest="S")  # Removed the encode() call

    # Save PDF to Django FileField
    lesson.report.save(f"{lesson.name}.pdf", ContentFile(pdf_output))

    # Commit changes to the database
    lesson.save()
