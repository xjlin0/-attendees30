from rest_framework import serializers

from attendees.whereabouts.serializers import AddressSerializer
from attendees.whereabouts.models import Place


class PlaceSerializer(serializers.ModelSerializer):
    street = serializers.CharField(read_only=True)
    address = AddressSerializer(required=False)
    # content_type = serializers.PrimaryKeyRelatedField(read_only=True)
    # object_id = serializers.CharField(read_only=True)  # https://www.django-rest-framework.org/api-guide/relations/#generic-relationships

    class Meta:
        model = Place
        # fields = '__all__'
        fields = [f.name for f in model._meta.fields if f.name not in ['is_removed']] + [
            'street',
            'address',
        ]

    # def to_representation(self, instance):
    #     rep = super().to_representation(instance)
    #     rep['address'] = AddressSerializer(instance.address).data
    #     print("hi 24 in PlaceSerializer here is AddressSerializer(instance.address).data")
    #     print(AddressSerializer(instance.address).data)
    #     return rep

    def create(self, validated_data):
        """
        Create or update `Place` instance, given the validated data.
        """

        place_id = self._kwargs['data'].get('id')
        print("hi 34 in PlaceSerializer, here is validated_data: ")
        print(validated_data)
        print("hi 36 in PlaceSerializer, here is self._kwargs: ")
        print(self._kwargs)
        print("hi 38 in PlaceSerializer, here is self._kwargs['data'].get('address'): ")
        print(self._kwargs['data'].get('address'))
        print("hi 40 in PlaceSerializer, here is validated_data.get('address'): ")
        print(validated_data.get('address'))
        # print("hi 42 in PlaceSerializer, here is validated_data.get('address'): ")
        # print(self.)
        obj, created = Place.objects.update_or_create(
            id=place_id,
            defaults=validated_data,
        )
        return obj

    def update(self, instance, validated_data):
        """
        Update and return an existing `Place` instance, given the validated data.

        """
        print("hi 40 in PlaceSerializer")
        # instance.title = validated_data.get('title', instance.title)
        # instance.code = validated_data.get('code', instance.code)
        # instance.linenos = validated_data.get('linenos', instance.linenos)
        # instance.language = validated_data.get('language', instance.language)
        # instance.style = validated_data.get('style', instance.style)
        instance.save()
        return instance
