from django.contrib.contenttypes.models import ContentType
from rest_framework import serializers, fields


class ContentTypeSerializer(serializers.ModelSerializer):

    class Meta:
        model = ContentType
        fields = [f.name for f in model._meta.fields] + [
            'endpoint',
        ]

    def build_unknown_field(self, field_name, model_class):
        """
        have to override https://stackoverflow.com/a/65035143/4257237
        """
        return fields.CharField, {'read_only': True}
