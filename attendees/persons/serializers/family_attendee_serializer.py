from rest_framework import serializers

from attendees.persons.models import FamilyAttendee, Family, Attendee
from attendees.persons.serializers import FamilySerializer, AttendeeSerializer


class FamilyAttendeeSerializer(serializers.ModelSerializer):
    family = FamilySerializer(many=False)
    # attendee = AttendeeSerializer(many=False)

    class Meta:
        model = FamilyAttendee
        fields = '__all__'
        # fields = [f.name for f in model._meta.fields if f.name not in ['is_removed']] + [
        #     'family',
        # ]

    def create(self, validated_data):
        """
        Create or update `FamilyAttendee` instance, given the validated data.
        """
        familyattendee_id = self._kwargs.get('data', {}).get('id')
        new_family = Family.objects.filter(pk=self._kwargs.get('data', {}).get('family', {}).get('id')).first()
        new_attendee_data = validated_data.get('attendee', {})
        if new_family:
            validated_data['family'] = new_family
        print("hi 27 here is new_attendee_data: ", new_attendee_data)
        if new_attendee_data:
            # attendee, attendee_created = Attendee.objects.update_or_create(
            #     id=new_attendee_data.get('id'),
            #     defaults=new_attendee_data,
            # )
            attendee = Attendee.objects.get(pk=new_attendee_data)
            validated_data['attendee'] = attendee
        # Todo: 20210517  create relationships among families such as siblings, etc
        obj, created = FamilyAttendee.objects.update_or_create(
            id=familyattendee_id,
            defaults=validated_data,
        )
        return obj

    def update(self, instance, validated_data):
        """
        Update and return an existing `FamilyAttendee` instance, given the validated data.

        """
        new_family = Family.objects.filter(pk=self._kwargs.get('data', {}).get('family', {}).get('id')).first()
        new_attendee_data = validated_data.get('attendee', {})

        if new_family:
            # instance.family = new_family
            validated_data['family'] = new_family
        # else:
        #     validated_data['family'] = instance.family

        if new_attendee_data:
            attendee, attendee_created = Attendee.objects.update_or_create(
                id=instance.attendee.id,
                defaults=new_attendee_data,
            )
            validated_data['attendee'] = attendee
        # else:
        #     validated_data['attendee'] = instance.attendee
        # Todo: 20210517  update relationships among families such as siblings, etc
        obj, created = FamilyAttendee.objects.update_or_create(
            id=instance.id,
            defaults=validated_data,
        )

        return obj
