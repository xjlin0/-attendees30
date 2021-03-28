from attendees.persons.models import AttendingMeet
from rest_framework import serializers


class AttendingMeetSerializer(serializers.ModelSerializer):

    class Meta:
        model = AttendingMeet
        fields = '__all__'
        # fields = [f.name for f in model._meta.fields if f.name not in ['is_removed']] + [
        #     'joined_meets',
        #     # 'display_label',
        #     # 'division_label',
        #     # 'parents_notifiers_names',
        #     'self_email_addresses',
        #     # 'caregiver_email_addresses',
        #     'self_phone_numbers',
        #     # 'caregiver_phone_numbers',
        # ]

