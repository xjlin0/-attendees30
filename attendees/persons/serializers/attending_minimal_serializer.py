from attendees.persons.models import Attending
from rest_framework import serializers

from attendees.persons.serializers import RegistrationSerializer


class AttendingMinimalSerializer(serializers.ModelSerializer):
    attending_label = serializers.CharField(read_only=True)
    registration = RegistrationSerializer(many=False)

    class Meta:
        model = Attending
        fields = '__all__'

    def create(self, validated_data):
        """
        Create or update `Attending` instance, given the validated data.
        """
        attending_id = self._kwargs.get('data', {}).get('id')
        print("hi 20 here is family_id: ")
        print(attending_id)
        print("hi 22 here is validated_data: ")
        print(validated_data)

        obj, created = Attending.objects.update_or_create(
            id=attending_id,
            defaults=validated_data,
        )
        return obj

    def update(self, instance, validated_data):
        """
        Update and return an existing `Attending` instance, given the validated data.

        """
        print("hi 36 here is instance: ")
        print(instance)
        print("hi 38 here is validated_data: ")
        print(validated_data)

        obj, created = Attending.objects.update_or_create(
            id=instance.id,
            defaults=validated_data,
        )

        return obj
