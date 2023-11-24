from django.urls import path

from summery_creator.summery.consumers import LessonConsumer

websocket_urlpatterns = [path("ws/lesson/<str:uuid>", LessonConsumer.as_asgi())]
