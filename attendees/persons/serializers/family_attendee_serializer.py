from rest_framework import serializers

from attendees.persons.models import FamilyAttendee
from attendees.persons.serializers import FamilySerializer, AttendeeSerializer


class FamilyAttendeeSerializer(serializers.ModelSerializer):
    family = FamilySerializer(read_only=True)
    attendee = AttendeeSerializer(read_only=True)
    

    class Meta:
        model = FamilyAttendee
        fields = '__all__'
        # fields = [f.name for f in model._meta.fields if f.name not in ['is_removed']] + [
        #     'family',
        # ]
