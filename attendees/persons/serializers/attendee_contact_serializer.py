from rest_framework import serializers

from attendees.persons.models import AttendeeContact
from attendees.whereabouts.serializers import ContactSerializer


class AttendeeContactSerializer(serializers.ModelSerializer):
    contact = ContactSerializer(read_only=True)

    class Meta:
        model = AttendeeContact
        # fields = '__all__'
        fields = [f.name for f in model._meta.fields if f.name not in ['is_removed']] + [
            'contact',
        ]
