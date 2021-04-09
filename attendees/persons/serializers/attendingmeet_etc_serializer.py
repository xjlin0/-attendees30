from attendees.persons.models import AttendingMeet
from rest_framework import serializers


class AttendingMeetEtcSerializer(serializers.ModelSerializer):
    assembly = serializers.IntegerField()

    class Meta:
        model = AttendingMeet
        fields = '__all__'

    # def create(self, validated_data):
    #     """
    #     Create and return a new `AttendingMeet` instance, given the validated data.
    #     """
    #     return AttendingMeet.objects.create(**validated_data)
    #
    # def update(self, instance, validated_data):
    #     """
    #     Update and return an existing `AttendingMeet` instance, given the validated data.
    #     """
    #     instance.title = validated_data.get('title', instance.title)
    #     instance.code = validated_data.get('code', instance.code)
    #     instance.linenos = validated_data.get('linenos', instance.linenos)
    #     instance.language = validated_data.get('language', instance.language)
    #     instance.style = validated_data.get('style', instance.style)
    #     instance.save()
    #     return instance

