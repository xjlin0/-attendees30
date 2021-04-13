from attendees.persons.models import AttendingMeet
from rest_framework import serializers


class AttendingMeetEtcSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    assembly = serializers.IntegerField()

    class Meta:
        model = AttendingMeet
        fields = '__all__'

    def create(self, validated_data):
        """
        Create and return a new `AttendingMeet` instance, given the validated data.
        """

        attendingmeet_id = self._kwargs['data'].get('id')
        assembly_id = validated_data.pop('assembly', None)

        obj, created = AttendingMeet.objects.update_or_create(
            id=attendingmeet_id,
            defaults=validated_data,
        )
        return obj

    def update(self, instance, validated_data):
        """
        Update and return an existing `AttendingMeet` instance, given the validated data.

        """
        print("hi 38 here is AttendingMeetEtcSerializer.update, here is validated_data: ")
        print(validated_data)
        print("hi 40 here is AttendingMeetEtcSerializer.update, here is instance: ")
        print(instance)

        # instance.title = validated_data.get('title', instance.title)
        # instance.code = validated_data.get('code', instance.code)
        # instance.linenos = validated_data.get('linenos', instance.linenos)
        # instance.language = validated_data.get('language', instance.language)
        # instance.style = validated_data.get('style', instance.style)
        instance.save()
        return instance

