from attendees.persons.models import Relationship
from rest_framework import serializers

from attendees.persons.serializers import FamilySerializer, AttendeeSerializer, RelationSerializer


class RelationshipSerializer(serializers.ModelSerializer):
    """
    Todo: Reason for special CRUD:
    If manager A checked "secret shared with you" for a Relationship, manager B
    can't see it (expected) and creating another relationship will fail due to uniq
    constrain (not expected). If relaxing uniq constraint, after manager B creating
    the very same relationship, manager A will see duplicated relationship. Instead we
    will add manager B id in secret shared with you of infos when manager B create it.

    When both managers are in secret shared with you of infos, when manager A deletes
    such records, it will only remove manager A from secret shared with you of infos.
    """
    # in_family = FamilySerializer(many=False)
    # to_attendee = AttendeeSerializer(many=False)
    # relation = RelationSerializer(many=False)

    class Meta:
        model = Relationship
        fields = '__all__'

