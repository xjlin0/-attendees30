from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import GinIndex
from model_utils.models import TimeStampedModel, SoftDeletableModel

from attendees.persons.models import Utility


class Locate(TimeStampedModel, SoftDeletableModel, Utility):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    place = models.ForeignKey('whereabouts.Place', on_delete=models.CASCADE, null=False, blank=False)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE, null=False, blank=False)
    object_id = models.CharField(max_length=36, null=False, blank=False)
    subject = GenericForeignKey('content_type', 'object_id')
    # category = models.CharField(max_length=20, default='main', blank=False, null=False, help_text='main, resident, etc (main will be displayed first)')
    display_name = models.CharField(db_index=True, max_length=50, default='main', blank=False, null=False, help_text='main, resident, etc (main will be displayed first)')
    display_order = models.SmallIntegerField(default=0, blank=False, null=False)
    start = models.DateTimeField(null=True, blank=True, help_text='optional')
    finish = models.DateTimeField(null=True, blank=True, help_text='optional')
    fields = JSONField(default=dict, null=True, blank=True, help_text="please keep {} here even there's no data")
    # need to validate there only one 'main' for display_name

    class Meta:
        db_table = 'whereabouts_locates'
        ordering = ('display_order',)
        constraints = [
            models.UniqueConstraint(fields=['place', 'content_type', 'object_id'], name="place_object")
        ]
        indexes = [
            GinIndex(fields=['fields'], name='locate_fields_gin', ),
        ]

    def __str__(self):
        return '%s %s' % (self.place, self.subject)
