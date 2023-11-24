from django.urls import path

from summery_creator.summery.api.views import (
    LessonEntriesSearchView,
    ListCreateLessonAPIView,
    RetrieveGlossaryEntryAPIView,
    RetrieveUpdateDestroyLessonAPIView,
    SearchViewAPIView,
    SendLessonMessageAPIView,
)

app_name = "summery"

urlpatterns = [
    path(
        "lessons/",
        ListCreateLessonAPIView.as_view(),
    ),
    path(
        "search/",
        SearchViewAPIView.as_view(),
    ),
    path(
        "lessons/<uuid:id>/",
        RetrieveUpdateDestroyLessonAPIView.as_view(),
    ),
    path(
        "lessons/<uuid:id>/search/",
        LessonEntriesSearchView.as_view(),
    ),
    path(
        "glossarium/<str:slug>/",
        RetrieveGlossaryEntryAPIView.as_view(),
    ),
    path(
        "message/<uuid:id>/",
        SendLessonMessageAPIView.as_view(),
    ),
]
