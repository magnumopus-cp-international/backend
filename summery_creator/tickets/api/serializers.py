from rest_framework import serializers

from summery_creator.tickets.models import Ticket


class TicketSerializer(serializers.ModelSerializer):
    current = serializers.IntegerField()

    class Meta:
        model = Ticket
        fields = ["name", "current", "max", "next"]
