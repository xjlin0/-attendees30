from attendees.persons.models import Attending
from rest_framework import serializers


class AttendingMinimalSerializer(serializers.ModelSerializer):
    attending_label = serializers.CharField()

    class Meta:
        model = Attending
        fields = '__all__'
