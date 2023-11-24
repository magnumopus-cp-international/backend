from django.urls import path

from summery_creator.summery.api.views import (
    ListCreateLessonAPIView,
    RetrieveUpdateDestroyLessonAPIView,
    SendLessonMessageAPIView,
)

app_name = "summery"

urlpatterns = [
    path(
        "lessons/",
        ListCreateLessonAPIView.as_view(),
    ),
    path(
        "lessons/<uuid:id>/",
        RetrieveUpdateDestroyLessonAPIView.as_view(),
    ),
    path(
        "message/<uuid:id>/",
        SendLessonMessageAPIView.as_view(),
    ),
]
