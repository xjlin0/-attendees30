from address.models import Address, Locality
from rest_framework import serializers


class AddressSerializer(serializers.ModelSerializer):
    zip_code = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    state_id = serializers.SerializerMethodField()
    country_id = serializers.SerializerMethodField()

    def get_locality(self, obj):
        return Locality.objects.filter(pk=obj.locality_id).first()

    def get_zip_code(self, obj):
        locality = self.get_locality(obj)
        return locality.postal_code if locality else None

    def get_city(self, obj):
        locality = self.get_locality(obj)
        return locality.name if locality else None

    def get_state_id(self, obj):
        locality = self.get_locality(obj)
        return locality.state.id if locality else None

    def get_country_id(self, obj):
        locality = self.get_locality(obj)
        return locality.state.country.id if locality and locality.state and locality.state.country else None

    class Meta:
        model = Address
        fields = '__all__'

