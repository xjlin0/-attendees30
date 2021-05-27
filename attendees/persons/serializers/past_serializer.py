from attendees.persons.models import Past
from rest_framework import serializers


class PastSerializer(serializers.ModelSerializer):

    class Meta:
        model = Past
        fields = '__all__'

