from attendees.occasions.models import Gathering
from rest_framework import serializers


class GatheringSerializer(serializers.ModelSerializer):
    site = serializers.CharField(read_only=True)

    class Meta:
        model = Gathering
        fields = [f.name for f in model._meta.fields if f.name not in ['is_removed']] + [
            'gathering_label',
            'site',
        ]

