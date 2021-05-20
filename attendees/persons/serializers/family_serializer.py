from attendees.persons.models import Family
from attendees.whereabouts.serializers import PlaceSerializer

from rest_framework import serializers


class FamilySerializer(serializers.ModelSerializer):
    places = PlaceSerializer(many=True, read_only=True)

    class Meta:
        model = Family
        fields = '__all__'

    def create(self, validated_data):
        """
        Create or update `Family` instance, given the validated data.
        """
        family_id = self._kwargs.get('data', {}).get('id')
        # print("hi 19 here is family_id: ")
        # print(family_id)
        # print("hi 21 here is validated_data: ")
        # print(validated_data)

        obj, created = Family.objects.update_or_create(
            id=family_id,
            defaults=validated_data,
        )
        return obj

    def update(self, instance, validated_data):
        """
        Update and return an existing `Family` instance, given the validated data.

        """

        obj, created = Family.objects.update_or_create(
            id=instance.id,
            defaults=validated_data,
        )

        return obj
