from attendees.persons.models import AttendingMeet
from rest_framework import serializers


class AttendingMeetSerializer(serializers.ModelSerializer):
    character_name = serializers.CharField()
    assembly_name = serializers.CharField()
    # attendee_id = serializers.CharField()

    class Meta:
        model = AttendingMeet
        # fields = '__all__'
        fields = [f.name for f in model._meta.fields if f.name not in ['is_removed']] + [
            'character_name',
            'assembly_name',
            # 'attendee_id',
        ]

