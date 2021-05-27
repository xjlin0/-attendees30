from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields.jsonb import JSONField
from django.contrib.postgres.indexes import GinIndex
from model_utils.models import TimeStampedModel, SoftDeletableModel, UUIDModel
from private_storage.fields import PrivateFileField
from . import Utility, Note


class Past(UUIDModel, TimeStampedModel, SoftDeletableModel, Utility):
    notes = GenericRelation(Note)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=False, blank=False)
    object_id = models.CharField(max_length=36, null=False, blank=False)
    subject = GenericForeignKey('content_type', 'object_id')
    start = models.DateTimeField(null=True, blank=True, default=Utility.now_with_timezone)
    finish = models.DateTimeField(null=True, blank=True)
    category = models.ForeignKey('persons.Category', null=False, blank=False, on_delete=models.SET(0), help_text="subtype: for education it's primary/high/college sub-types etc")
    display_order = models.SmallIntegerField(default=30000, blank=False, null=False, db_index=True)
    display_name = models.CharField(max_length=50, blank=True, null=True)
    file = PrivateFileField("File", blank=True, null=True, upload_to="past_files")
    infos = JSONField(null=True, blank=True, default=Utility.relationship_infos, help_text='Example: {"show_secret": {"attendee1id": true, "attendee2id": false}}. Please keep {} here even no data')  # compare to NoteAdmin

    class Meta:
        db_table = 'persons_pasts'
        ordering = ('category__type', 'display_order', 'category__display_order', 'start')
        indexes = [
            GinIndex(fields=['infos'], name='past_infos_gin', ),
        ]

    def __str__(self):
        return '%s %s %s' % (self.subject, self.category, self.display_name)
