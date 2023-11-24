from drf_spectacular.openapi import OpenApiTypes
from drf_spectacular.utils import (
    OpenApiParameter,
    OpenApiResponse,
    extend_schema,
    inline_serializer,
)
from rest_framework import generics, status
from rest_framework.generics import ListAPIView, get_object_or_404
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from summery_creator.summery.api.serializers import (
    CallbackSerializer,
    FullGlossaryEntrySerializer,
    FullLessonSerializer,
    LessonSerializer,
    ListGlossaryEntrySerializer,
)
from summery_creator.summery.models import GlossaryEntry, Lesson
from summery_creator.summery.services import (
    search_documents,
    search_glossary_entries,
    send_message,
)
from summery_creator.summery.tasks import handle_ml_callback


class ListCreateLessonAPIView(generics.ListCreateAPIView):
    serializer_class = LessonSerializer
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_queryset(self):
        return Lesson.objects.order_by("-uploaded")


class RetrieveUpdateDestroyLessonAPIView(generics.RetrieveUpdateDestroyAPIView):
    lookup_field = "id"
    lookup_url_kwarg = "id"
    serializer_class = FullLessonSerializer
    queryset = Lesson.objects.all()


class RetrieveGlossaryEntryAPIView(generics.RetrieveAPIView):
    serializer_class = FullGlossaryEntrySerializer
    queryset = GlossaryEntry.objects.all()
    lookup_field = "slug"
    lookup_url_kwarg = "slug"


class SendLessonMessageAPIView(generics.GenericAPIView):
    serializer_class = CallbackSerializer

    @extend_schema(
        request=OpenApiTypes.OBJECT,
        responses={200: {"status": "ok"}},
    )
    def post(self, request, *args, **kwargs):
        # serializer = self.get_serializer(data=request.data)
        # serializer.is_valid(raise_exception=True)
        data = request.data
        send_message(self.kwargs["id"], data)
        handle_ml_callback.apply_async(
            kwargs={
                "type": data["type"],
                "data": data["data"],
                "uuid": self.kwargs["id"],
            },
            countdown=1,
        )
        return Response({"status": "ok"})


class SearchViewAPIView(ListAPIView):
    serializer_class = None

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="q", description="Search query", required=True, type=str
            )
        ],
        responses={
            200: inline_serializer(
                name="CombinedSearchResponse",
                fields={
                    "lessons": LessonSerializer(many=True),
                    "glossary_entries": ListGlossaryEntrySerializer(many=True),
                },
            )
        },
        description="Endpoint for searching Lessons and Glossary Entries",
    )
    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "")
        if not query:
            return Response(
                {"detail": "Query parameter q is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        data = search_documents(query)
        return Response(data, status=status.HTTP_200_OK)


class LessonEntriesSearchView(generics.RetrieveAPIView):
    lookup_field = "id"
    lookup_url_kwarg = "id"
    serializer_class = ListGlossaryEntrySerializer

    @extend_schema(
        parameters=[
            OpenApiParameter(
                name="q",
                description="Search term for entries",
                required=False,
                type=str,
            )
        ],
        responses={
            200: OpenApiResponse(
                response=ListGlossaryEntrySerializer(many=True),
                description="List of filtered entries",
            )
        },
    )
    def get(self, request, *args, **kwargs):
        query = request.GET.get("q", "")
        if not query:
            return Response(
                {"detail": "Query parameter q is required."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        lesson = get_object_or_404(Lesson, id=self.kwargs["id"])
        data = search_glossary_entries(query, lesson.entries.all())
        return Response(data, status=status.HTTP_200_OK)
