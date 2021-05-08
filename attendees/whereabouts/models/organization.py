from django.db import models
from django.contrib.postgres.fields.jsonb import JSONField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.contenttypes.fields import GenericRelation
from attendees.persons.models import Utility, Note
from model_utils.models import TimeStampedModel, SoftDeletableModel


class Organization(TimeStampedModel, SoftDeletableModel, Utility):
    notes = GenericRelation(Note)
    locates = GenericRelation('whereabouts.Place')
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    slug = models.SlugField(max_length=50, blank=False, null=False, unique=True, help_text="alphanumeric only")
    display_name = models.CharField(max_length=50, blank=False, null=False)
    infos = JSONField(null=True, blank=True, default=dict, help_text='Example: {"hostname": "where the app deployed"}. Please keep {} here even no data')

    class Meta:
        db_table = 'whereabouts_organizations'
        indexes = [
            GinIndex(fields=['infos'], name='organization_infos_gin', ),
        ]

    def __str__(self):
        return '%s' % self.display_name

