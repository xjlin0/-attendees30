from attendees.occasions.models import Gathering
from rest_framework import serializers


class GatheringSerializer(serializers.ModelSerializer):
    site = serializers.CharField(read_only=True)
    gathering_label = serializers.CharField(read_only=True)

    class Meta:
        model = Gathering
        fields = [f.name for f in model._meta.fields if f.name not in ['is_removed']] + [
            'gathering_label',
            'site',
        ]

    def update(self, instance, validated_data):
        """
        Update and return an existing `Gathering` instance, given the validated data.

        """
        print("hi 21 here is instance: "); print(instance)
        print("hi 22 here is validated_data: "); print(validated_data)
        obj, created = Gathering.objects.update_or_create(
            id=instance.id,
            defaults=validated_data,
        )

        return obj
