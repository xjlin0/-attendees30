from rest_framework import serializers

from attendees.occasions.models import Assembly


class AssemblySerializer(serializers.ModelSerializer):
    class Meta:
        model = Assembly
        fields = '__all__'

