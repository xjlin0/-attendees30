from attendees.persons.models import Past
from rest_framework import serializers


class PastSerializer(serializers.ModelSerializer):
    """
    Todo: Reason for special CRUD:
    If manager A checked "secret shared with you" for a Past, manager B
    can't see it (expected) and creating another relationship will fail due to uniq
    constrain (not expected). If relaxing uniq constraint, after manager B creating
    the very same relationship, manager A will see duplicated relationship. Instead we
    will add manager B id in secret shared with you of infos when manager B create it

    When both managers are in secret shared with you of infos, when manager A deletes
    such records, it will only remove manager A from secret shared with you of infos.
    """

    class Meta:  # It is critical not to have organization in the fields, to let perform_create set it
        model = Past
        fields = ('id', 'display_name', 'category', 'when', 'finish', 'infos', 'content_type', 'object_id')

