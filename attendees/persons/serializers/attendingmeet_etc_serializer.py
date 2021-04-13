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
        print("hi 17 here is AttendingMeetEtcSerializer.create, here is validated_data: ")
        print(validated_data)
        return AttendingMeet.objects.create(**validated_data)

    def update(self, instance, validated_data):
        """
        Update and return an existing `AttendingMeet` instance, given the validated data.

        assembly: 5
        attending: 9
        category: "hi there"
        character: 22
        created: "1999-05-09T17:26:30.162000-07:00"
        finish: "2030-02-17T11:59:59-08:00"
        id: 12   # member
        is_removed: false
        meet: 9
        modified: "2020-11-15T20:27:15.590000-08:00"
        start: "2020-01-01T10:00:00-08:00"

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

