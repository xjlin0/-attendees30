from rest_framework import serializers

from attendees.whereabouts.models import Place
# from attendees.whereabouts.serializers import PlaceSerializer


class PlaceSerializer(serializers.ModelSerializer):
    street = serializers.CharField(read_only=True)

    class Meta:
        model = Place
        fields = '__all__'
        fields = [f.name for f in model._meta.fields if f.name not in ['is_removed']] + [
            'street',
        ]

    def create(self, validated_data):
        """
        Create or update `AttendingMeet` instance, given the validated data.
        """

        locate_id = self._kwargs['data'].get('id')
        print("hi 23 in PlaceSerializer, here is validated_data: ")
        print(validated_data)
        obj, created = Place.objects.update_or_create(
            id=locate_id,
            defaults=validated_data,
        )
        return obj

    def update(self, instance, validated_data):
        """
        Update and return an existing `AttendingMeet` instance, given the validated data.

        """
        print("hi 36 in PlaceSerializer")
        # instance.title = validated_data.get('title', instance.title)
        # instance.code = validated_data.get('code', instance.code)
        # instance.linenos = validated_data.get('linenos', instance.linenos)
        # instance.language = validated_data.get('language', instance.language)
        # instance.style = validated_data.get('style', instance.style)
        instance.save()
        return instance
