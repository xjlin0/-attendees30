from django.db import models
from django.urls import reverse
from django.contrib.contenttypes.fields import GenericRelation, GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.contrib.postgres.fields.jsonb import JSONField
from model_utils.models import TimeStampedModel, SoftDeletableModel
from schedule.models import EventRelation

from attendees.persons.models import Utility, Note


class Meet(TimeStampedModel, SoftDeletableModel, Utility):
    notes = GenericRelation(Note)
    event_relations = GenericRelation(EventRelation)
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    assembly = models.ForeignKey('occasions.Assembly', null=True, blank=True, on_delete=models.SET_NULL)
    attendings = models.ManyToManyField('persons.Attending', through='persons.AttendingMeet', related_name="attendings")
    shown_audience = models.BooleanField('show AttendingMeet to participant?', null=False, blank=False, default=True, help_text="[some meets are only for internal records] show the AttendingMeet to attendee?")
    audience_editable = models.BooleanField('participant can edit AttendingMeet?', null=False, blank=False, default=True, help_text="[some meets are editable only by coworkers] participant can edit AttendingMeet?")
    start = models.DateTimeField(null=False, blank=False, default=Utility.now_with_timezone)
    finish = models.DateTimeField(null=False, blank=False, help_text="Required for user to filter by time")
    display_name = models.CharField(max_length=50, blank=True, null=True, db_index=True, help_text="The Rock, Little Foot, singspiration, A/V control, etc.")
    slug = models.SlugField(max_length=50, blank=False, null=False, unique=True)
    infos = JSONField(null=True, blank=True, default=dict, help_text='Example: {"info": "...", "url": "https://..."}. Please keep {} here even no data')
    site_type = models.ForeignKey(ContentType, on_delete=models.SET(0), help_text='location: django_content_type id for table name')
    site_id = models.BigIntegerField()
    location = GenericForeignKey('site_type', 'site_id')

    # def save(self):
    #     pass # https://stackoverflow.com/a/27241824

    def get_absolute_url(self):
        return reverse('character_detail', args=[str(self.id)])

    def info(self):
        return self.infos.get('info', '')

    def url(self):
        return self.infos.get('url', '')

    class Meta:
        db_table = 'occasions_meets'

    def __str__(self):
        return '%s %s %s' % (self.display_name or '', self.infos.get('info', ''), self.infos.get('url', ''))
