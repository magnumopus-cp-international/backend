from django.urls import include, path

app_name = "api"
urlpatterns = [
    path("ticket/", include("summery_creator.tickets.api.urls")),
    path("", include("summery_creator.summery.api.urls")),
]
