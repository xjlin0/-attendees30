from address.models import Address
from rest_framework import serializers


class AddressSerializer(serializers.ModelSerializer):
    postal_code = serializers.SerializerMethodField()
    city = serializers.SerializerMethodField()
    state_id = serializers.SerializerMethodField()
    # country_id = serializers.SerializerMethodField()

    def get_postal_code(self, obj):
        locality = obj.locality
        return locality.postal_code if locality else None

    def get_city(self, obj):
        locality = obj.locality
        return locality.name if locality else None

    def get_state_id(self, obj):
        locality = obj.locality
        return locality.state.id if locality else None

    class Meta:
        model = Address
        fields = '__all__'

