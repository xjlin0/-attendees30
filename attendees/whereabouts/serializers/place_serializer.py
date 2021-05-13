from address.models import Address
from rest_framework import serializers

from attendees.whereabouts.serializers import AddressSerializer
from attendees.whereabouts.models import Place


class PlaceSerializer(serializers.ModelSerializer):
    """
    Generic relation: https://www.django-rest-framework.org/api-guide/relations/#generic-relationships
    """

    street = serializers.CharField(read_only=True)
    address = AddressSerializer(required=False)

    class Meta:
        model = Place
        # fields = '__all__'
        fields = [f.name for f in model._meta.fields if f.name not in ['is_removed']] + [
            'street',
            'address',
        ]

    def create(self, validated_data):
        """
        Create or update `Place` instance, given the validated data.
        """
        place_data = self._kwargs.get('data', {})
        place_id = place_data.get('id')
        address_data = place_data.get('address')
        address_id = address_data.get('id')
        locality = validated_data.get('address', {}).get('locality')
        address_data['locality'] = locality

        if address_id:
            address, address_created = Address.objects.update_or_create(
                id=address_id,
                defaults=address_data,
            )
            validated_data['address'] = address

            place, place_created = Place.objects.update_or_create(
                id=place_id,
                defaults=validated_data,
            )
        else:  # user is creating new address
            new_address_data = address_data.get('new_address', {})
            del validated_data['address']
            place, place_created = Place.objects.update_or_create(
                id=place_id,
                defaults=validated_data,
            )
            place.address = new_address_data
            place.save()

        return place

    def update(self, instance, validated_data):
        """
        Update and return an existing `Place` instance, given the validated data.

        """
        # print("hi 40 in PlaceSerializer")
        # instance.title = validated_data.get('title', instance.title)
        # instance.code = validated_data.get('code', instance.code)
        # instance.linenos = validated_data.get('linenos', instance.linenos)
        # instance.language = validated_data.get('language', instance.language)
        # instance.style = validated_data.get('style', instance.style)
        instance.save()
        return instance
