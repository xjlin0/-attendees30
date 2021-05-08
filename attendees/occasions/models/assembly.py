from django.db import models
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import GinIndex
from django.urls import reverse

from model_utils.models import TimeStampedModel, SoftDeletableModel

from attendees.persons.models import Utility, Note


class Assembly(TimeStampedModel, SoftDeletableModel, Utility):
    locates = GenericRelation('whereabouts.Place')
    notes = GenericRelation(Note)
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    start = models.DateTimeField(null=True, blank=True, help_text='optional')
    finish = models.DateTimeField(null=True, blank=True, help_text='optional')
    # contacts = models.ManyToManyField('whereabouts.Place', through='AssemblyContact')
    category = models.CharField(max_length=20, default='normal', blank=False, null=False, db_index=True, help_text="normal, no-display, etc")
    display_name = models.CharField(max_length=50, blank=False, null=False)
    display_order = models.SmallIntegerField(default=0, blank=False, null=False)
    slug = models.SlugField(max_length=50, blank=False, null=False, unique=True, help_text='format: Organization_name-Assembly_name')
    need_age = models.BooleanField('Does registration need age info?', null=False, blank=False, default=False, help_text="Does the age info of the participants required?")
    division = models.ForeignKey('whereabouts.Division', null=False, blank=False, on_delete=models.SET(0))
    infos = JSONField(default=dict, null=True, blank=True, help_text="please keep {} here even there's no data")

    def get_absolute_url(self):
        return reverse('assembly_detail', args=[str(self.id)])

    class Meta:
        db_table = 'occasions_assemblies'
        verbose_name_plural = 'Assemblies'
        ordering = ('display_order',)
        indexes = [
            GinIndex(fields=['infos'], name='assembly_infos_gin', ),
        ]

    def __str__(self):
        return '%s' % self.display_name

    def get_addresses(self):
        return "\n".join([a.place.street for a in self.locates.all() if a is not None])

# from rest_framework import serializers
#
#
# class AssemblySerializer(serializers.ModelSerializer):
#     class Meta:
#         model = Assembly
#         fields = ['id', 'name', 'division', 'ttttt']

# from mainsite.models.assembly import AssemblySerializer
# k2=Assembly.objects.get(pk=2)
# serializer=AssemblySerializer(k2)
# serializer.data
# #=> {'id': 2, 'name': '2019 Fall kid programs', 'division': 'none', 'ttttt': 'ttttt'}
