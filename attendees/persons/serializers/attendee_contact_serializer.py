from rest_framework import serializers

from attendees.persons.models import AttendeeContact
from attendees.whereabouts.serializers import ContactSerializer


class AttendeeContactSerializer(serializers.ModelSerializer):
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = AttendeeContact
        # fields = '__all__'
        fields = [f.name for f in model._meta.fields if f.name not in ['is_removed']] + [
            # 'contact',
        ]

    def create(self, validated_data):
        """
        Create or update `AttendingMeet` instance, given the validated data.
        """

        attendeecontact_id = self._kwargs['data'].get('id')
        print("hi 23 in AttendeeContactSerializer, here is validated_data: ")
        print(validated_data)
        obj, created = AttendeeContact.objects.update_or_create(
            id=attendeecontact_id,
            defaults=validated_data,
        )
        return obj

    def update(self, instance, validated_data):
        """
        Update and return an existing `AttendingMeet` instance, given the validated data.

        """
        print("hi 36 in AttendeeContactSerializer")
        # instance.title = validated_data.get('title', instance.title)
        # instance.code = validated_data.get('code', instance.code)
        # instance.linenos = validated_data.get('linenos', instance.linenos)
        # instance.language = validated_data.get('language', instance.language)
        # instance.style = validated_data.get('style', instance.style)
        instance.save()
        return instance
