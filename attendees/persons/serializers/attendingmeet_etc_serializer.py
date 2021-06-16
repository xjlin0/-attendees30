from attendees.persons.models import AttendingMeet
from rest_framework import serializers


class AttendingMeetEtcSerializer(serializers.ModelSerializer):
    assembly = serializers.IntegerField(read_only=True)

    class Meta:
        model = AttendingMeet
        fields = '__all__'

    def create(self, validated_data):
        """
        Create or update `AttendingMeet` instance, given the validated data.
        """
        attendingmeet_id = self._kwargs['data'].get('id')
        # print("hi 17 hre is attendingmeet_id: ")
        # print(attendingmeet_id)
        # print("hi 19 hre is validated_data: ")
        # print(validated_data)
        obj, created = AttendingMeet.objects.update_or_create(
            id=attendingmeet_id,
            defaults=validated_data,
        )
        return obj

    def update(self, instance, validated_data):
        """
        Update and return an existing `AttendingMeet` instance, given the validated data.

        """

        if True:  # need validations such as if the assembly matching meet, it's better to validate on UI first
            instance.meet = validated_data.get('meet', instance.meet)
            # instance.meet.assembly = validated_data.get('assembly', instance.meet.assembly)
            instance.meet.save()

        instance.attending = validated_data.get('attending', instance.attending)
        instance.start = validated_data.get('start', instance.start)
        instance.finish = validated_data.get('finish', instance.finish)
        instance.character = validated_data.get('character', instance.character)
        instance.category = validated_data.get('category', instance.category)

        instance.save()
        return instance

