from attendees.persons.models import Attending, Registration
from rest_framework import serializers

from attendees.persons.serializers import RegistrationSerializer


class AttendingMinimalSerializer(serializers.ModelSerializer):
    attending_label = serializers.CharField(read_only=True)
    registration = RegistrationSerializer(required=False)

    class Meta:
        model = Attending
        fields = '__all__'
        # fields = [f.name for f in model._meta.fields if f.name not in ['is_removed']] + [
        #     'attending_label',
        #     'registration',
        # ]

    def create(self, validated_data):
        """
        Create or update `Attending` instance, given the validated data.
        """
        attending_id = self._kwargs.get('data', {}).get('id')
        print("hi 24 here is family_id: ")
        print(attending_id)
        print("hi 26 here is validated_data: ")
        print(validated_data)

        obj, created = Attending.objects.update_or_create(
            id=attending_id,
            defaults=validated_data,
        )
        return obj

    def update(self, instance, validated_data):
        """
        Update and return an existing `Attending` instance, given the validated data.

        """
        if 'registration' in validated_data:
            registration_data = validated_data.pop('registration')
            print("hi 48 here is registration_data: ")
            print(registration_data)
            registration, created = Registration.objects.update_or_create(
                id=instance.registration.id if instance.registration else None,
                defaults=registration_data,
            )
            validated_data['registration'] = registration

        obj, created = Attending.objects.update_or_create(
            id=instance.id,
            defaults=validated_data,
        )

        return obj
