from attendees.persons.models import Family
from attendees.whereabouts.serializers import PlaceSerializer

from rest_framework import serializers


class FamilySerializer(serializers.ModelSerializer):
    places = PlaceSerializer(many=True, read_only=True)

    class Meta:
        model = Family
        fields = '__all__'

