from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields.jsonb import JSONField
from django.contrib.postgres.indexes import GinIndex
from model_utils.models import TimeStampedModel, SoftDeletableModel, UUIDModel
from . import Utility, Note, Attendee


class Relationship(UUIDModel, TimeStampedModel, SoftDeletableModel, Utility):
    """
    Model to store relationships. Need to implement audience permissions. For example,
    coworker A wrote some notes of user B, however these notes may/should not be shared with user B.
    One potential way is to have infos similar to infos__show_secret__all_counselors_: True
    infos__show_secret__ATTENDEE: True so whoever can access to attendee, including user B, can see it
    infos__show_secret__COWORKER or ORGANIZER: True so only coworker/organizer, not user B, can see it
    """

    notes = GenericRelation(Note)
    from_attendee = models.ForeignKey(Attendee, related_name='from_attendee', on_delete=models.CASCADE)
    to_attendee = models.ForeignKey(Attendee, related_name='to_attendee', on_delete=models.CASCADE)
    relation = models.ForeignKey('persons.Relation', related_name='relation', null=False, blank=False, on_delete=models.SET(0), verbose_name='to_attendee is', help_text="[Title] What would from_attendee call to_attendee?")
    emergency_contact = models.BooleanField('to_attendee is the emergency contact?', null=False, blank=False, default=False, help_text="[from_attendee decide:] Notify to_attendee of from_attendee's emergency?")
    scheduler = models.BooleanField('to_attendee is the scheduler?', null=False, blank=False, default=False, help_text="[from_attendee decide:] to_attendee can view/change the schedules of the from_attendee?")
    in_family = models.ForeignKey('persons.Family', null=True, blank=True, on_delete=models.SET_NULL, related_name="in_family")
    start = models.DateTimeField(null=True, blank=True)
    finish = models.DateTimeField(blank=True, null=True, help_text="The relation will be ended at when")
    infos = JSONField(null=True, blank=True, default=Utility.relationship_infos, help_text='Example: {"show_secret": {"attendee1id": true, "attendee2id": false}}. Please keep {} here even no data')  # compare to NoteAdmin

    class Meta:
        db_table = 'persons_relationships'
        constraints = [
            models.UniqueConstraint(fields=['from_attendee', 'to_attendee', 'relation'], condition=models.Q(is_removed=False), name="attendee_relation")
        ]
        indexes = [
            GinIndex(fields=['infos'], name='relationship_infos_gin', ),
        ]

    def __str__(self):
        return '%s %s %s' % (self.from_attendee, self.to_attendee, self.relation)
