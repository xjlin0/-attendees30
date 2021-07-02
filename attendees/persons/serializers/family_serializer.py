from attendees.persons.models import Family, FamilyAttendee, Relation, Utility, Attendee
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
        raw_data = self._kwargs.get('data', {})
        family_id = raw_data.get('id')

        family, family_created = Family.objects.update_or_create(
            id=family_id,
            defaults=validated_data,
        )

        if family_created:
            for attendee_id in raw_data.get('attendees', []):
                unspecified_role = Relation.objects.filter(title='unspecified').first
                attendee = Attendee.objects.get(pk=attendee_id)
                FamilyAttendee.objects.update_or_create(
                    attendee=attendee,
                    family=family,
                    defaults={
                        'attendee': attendee,
                        'family': family,
                        'role': unspecified_role,
                        'start': Utility.now_with_timezone()
                    },
                )

        return family

    def update(self, instance, validated_data):
        """
        Update and return an existing `Family` instance, given the validated data.

        """

        obj, created = Family.objects.update_or_create(
            id=instance.id,
            defaults=validated_data,
        )

        return obj
