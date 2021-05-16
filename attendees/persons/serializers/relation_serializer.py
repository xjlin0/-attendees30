from attendees.persons.models import Relation
from rest_framework import serializers


class RelationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Relation
        fields = '__all__'

