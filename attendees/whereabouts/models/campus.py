from django.db import models
from django.urls import reverse
from django.contrib.postgres.fields.jsonb import JSONField
from django.contrib.postgres.indexes import GinIndex
from django.contrib.contenttypes.fields import GenericRelation
from model_utils.models import TimeStampedModel, SoftDeletableModel

from attendees.persons.models import Utility, Note
from attendees.occasions.models import Gathering


class Campus(TimeStampedModel, SoftDeletableModel, Utility):
    notes = GenericRelation(Note)
    places = GenericRelation('whereabouts.Place')
    gathering = GenericRelation(Gathering)
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    display_name = models.CharField(max_length=50, blank=False, null=False, db_index=True)
    slug = models.SlugField(max_length=50, blank=False, null=False, unique=True)
    infos = JSONField(null=True, blank=True, default=dict, help_text='Example: {"hostname": "where the app deployed"}. Please keep {} here even no data')

    class Meta:
        db_table = 'whereabouts_campus'
        verbose_name_plural = 'Campuses'
        indexes = [
            GinIndex(fields=['infos'], name='campus_infos_gin', ),
        ]

    def get_absolute_url(self):
        return reverse('campus_detail', args=[str(self.id)])

    def __str__(self):
        return '%s' % self.display_name
