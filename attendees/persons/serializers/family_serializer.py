from attendees.persons.models import Family
from rest_framework import serializers


class FamilySerializer(serializers.ModelSerializer):

    class Meta:
        model = Family
        fields = '__all__'

