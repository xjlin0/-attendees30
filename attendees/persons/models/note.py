from django.db import models
from django.contrib.postgres.fields.jsonb import JSONField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from model_utils.models import UUIDModel, TimeStampedModel, SoftDeletableModel


class Note(UUIDModel, TimeStampedModel, SoftDeletableModel):
    COUNSELING = 'counseling'  # for private data, only counselor group

    content_type = models.ForeignKey(ContentType, on_delete=models.SET(0))
    object_id = models.CharField(max_length=36)
    content_object = GenericForeignKey('content_type', 'object_id')
    category = models.CharField(max_length=20, default='normal', blank=False, null=False, db_index=True, help_text="normal, for-address, etc")
    display_order = models.SmallIntegerField(default=0, blank=False, null=False)
    body = models.TextField()
    infos = JSONField(null=True, blank=True, default=dict, help_text='Example: {"owner": "John"}. Please keep {} here even no data')

    def __str__(self):
        return '%s %s %s' % (self.content_type, self.content_object, self.category)

    class Meta:
        db_table = 'persons_notes'
        ordering = ('display_order', '-modified',)
        indexes = [
            GinIndex(fields=['infos'], name='note_infos_gin', ),
        ]

    # @property
    # def iso_updated_at(self):
    #     return self.modified.isoformat()
