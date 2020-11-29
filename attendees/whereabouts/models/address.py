from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import GinIndex

from model_utils.models import TimeStampedModel, SoftDeletableModel, UUIDModel

from attendees.persons.models import Utility, Note
from attendees.occasions.models import Assembly, AssemblyAddress


class Address(UUIDModel, TimeStampedModel, SoftDeletableModel, Utility):
    notes = GenericRelation(Note)
    # id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    display_name = models.CharField(max_length=50, blank=True, null=True, db_index=True, help_text='optional label')
    assemblies = models.ManyToManyField(Assembly, through=AssemblyAddress)
    attendees = models.ManyToManyField('persons.Attendee', through='persons.AttendeeAddress')
    # families = models.ManyToManyField('persons.Families', through='persons.FamilyAddress')
    # email1 = models.EmailField(blank=True, null=True, max_length=254, db_index=True)
    # email2 = models.EmailField(blank=True, null=True, max_length=254)
    # phone1 = models.CharField(max_length=16, blank=True, null=True, db_index=True)
    # phone2 = models.CharField(max_length=16, blank=True, null=True)
    address_type = models.CharField(max_length=20, default='street', blank=True, null=True, help_text='mailing, remote or street address')
    street1 = models.CharField(max_length=50, blank=True, null=True)
    street2 = models.CharField(max_length=50, blank=True, null=True)
    city = models.CharField(max_length=50, blank=True, null=True)
    state = models.CharField(max_length=10, default='CA', blank=True, null=True)
    zip_code = models.CharField(max_length=10, null=True, blank=True)
    # url = models.URLField(max_length=255, blank=True, null=True)
    country = models.CharField(max_length=10, default='N/A', blank=True, null=True)
    fields = JSONField(default=dict, null=True, blank=True, help_text="please keep {} here even there's no data")

    def get_absolute_url(self):
        return reverse('address_detail', args=[str(self.id)])

    def clean(self):  #needs to check if fields are valid json (even empty json)
        if not (self.street1 or self.fields['phone1'] or self.fields['url'] or self.fields['email1']):
            raise ValidationError("You must specify at least a street or telephone or url or email")

# should validate the format of phone to be +1-123-456-7890 so it can be dialed directly on phones

    class Meta:
        db_table = 'whereabouts_addresses'
        verbose_name_plural = 'Addresses'
        ordering = ['created']
        indexes = [
            GinIndex(fields=['fields'], name='address_fields_gin', ),
        ]

    @property
    def street(self):
        return '{street1} {street2}'.format(street1=self.street1, street2=self.street2 or '').strip()

    def __str__(self):
        return '%s, %s, %s. %s' % (self.display_name or self.attendees.first() or '', self.street1, self.city, self.zip_code)
