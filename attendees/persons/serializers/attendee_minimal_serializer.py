from attendees.persons.models import Attendee
from rest_framework import serializers


class AttendeeMinimalSerializer(serializers.ModelSerializer):
    # parents_notifiers_names = serializers.CharField()
    # self_email_addresses = serializers.CharField(read_only=True)
    # caregiver_email_addresses = serializers.CharField()
    # self_phone_numbers = serializers.CharField(read_only=True)
    # caregiver_phone_numbers = serializers.CharField()
    # joined_roaster = serializers.IntegerField()
    photo = serializers.ImageField(use_url=True)   # trying DevExtreme dxFileUploader https://supportcenter.devexpress.com/ticket/details/t404408
    joined_meets = serializers.JSONField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(many=False, read_only=True)  # For MVP, Admin UI can handle this use case. Todo: when non admins start to use app, admin need to edit this on UI

    class Meta:
        model = Attendee
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

    def create(self, validated_data):
        """
        Create and return a new `Attendee` instance, given the validated data.
        """

        attendee_id = self._kwargs['data'].get('attendee-id')

        obj, created = Attendee.objects.update_or_create(
            id=attendee_id,
            defaults=validated_data,
        )
        return obj

    def update(self, instance, validated_data):
        """
        Update and return an existing `AttendingMeet` instance, given the validated data.

        """
        print("hi AttendeeMinimalSerializer.update() 47 here is validated_data: ")
        print(validated_data)
        instance.save()
        return instance

