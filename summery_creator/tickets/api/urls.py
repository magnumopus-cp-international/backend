from django.urls import path

from summery_creator.tickets.api.views import RetrieveTicketSerializer

urlpatterns = [
    path("<str:uuid>", RetrieveTicketSerializer.as_view(), name="ticket"),
]
