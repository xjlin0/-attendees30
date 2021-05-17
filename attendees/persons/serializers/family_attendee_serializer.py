from rest_framework import serializers

from attendees.persons.models import FamilyAttendee
from attendees.persons.serializers import FamilySerializer, AttendeeSerializer


class FamilyAttendeeSerializer(serializers.ModelSerializer):
    family = FamilySerializer(required=False)
    attendee = AttendeeSerializer(required=False)

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

        familyattendee_id = self._kwargs['data'].get('id')
        print("hi 24 here is self._kwargs['data']: ")
        print(self._kwargs['data'])
        print("hi 26 here is validated_data: ")
        print(validated_data)
        obj, created = FamilyAttendee.objects.update_or_create(
            id=familyattendee_id,
            defaults=validated_data,
        )
        return obj

    def update(self, instance, validated_data):
        """
        Update and return an existing `FamilyAttendee` instance, given the validated data.

        """
        print("hi 39 here is validated_data: ")
        print(validated_data)
        # instance.title = validated_data.get('title', instance.title)
        # instance.code = validated_data.get('code', instance.code)
        # instance.linenos = validated_data.get('linenos', instance.linenos)
        # instance.language = validated_data.get('language', instance.language)
        # instance.style = validated_data.get('style', instance.style)
        instance.save()
        return instance
