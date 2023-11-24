from drf_spectacular.openapi import OpenApiTypes
from drf_spectacular.utils import extend_schema
from rest_framework import generics
from rest_framework.parsers import FormParser, JSONParser, MultiPartParser
from rest_framework.response import Response

from summery_creator.summery.api.serializers import (
    CallbackSerializer,
    FullLessonSerializer,
    LessonSerializer,
)
from summery_creator.summery.models import Lesson
from summery_creator.summery.services import send_message
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


class SendLessonMessageAPIView(generics.GenericAPIView):
    serializer_class = CallbackSerializer

    @extend_schema(
        request=OpenApiTypes.OBJECT,
        responses={200: {"status": "ok"}},
    )
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        send_message(self.kwargs["id"], request.data)
        handle_ml_callback.apply_async(
            kwargs={
                "type": data["type"],
                "data": data["data"],
                "uuid": self.kwargs["id"],
            },
            countdown=1,
        )
        return Response({"status": "ok"})
