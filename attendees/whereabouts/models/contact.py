from django.db import models
from django.urls import reverse
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields import JSONField
from django.contrib.postgres.indexes import GinIndex
from address.models import AddressField
from model_utils.models import TimeStampedModel, SoftDeletableModel, UUIDModel

from attendees.persons.models import Utility, Note
from attendees.occasions.models import Assembly, AssemblyContact


class Contact(UUIDModel, TimeStampedModel, SoftDeletableModel, Utility):
    notes = GenericRelation(Note)
    # id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    display_name = models.CharField(max_length=50, blank=True, null=True, db_index=True, help_text='optional label')
    assemblies = models.ManyToManyField(Assembly, through=AssemblyContact)
    attendees = models.ManyToManyField('persons.Attendee', through='persons.AttendeeContact')
    # families = models.ManyToManyField('persons.Families', through='persons.FamilyAddress')
    # email1 = models.EmailField(blank=True, null=True, max_length=254, db_index=True)
    # email2 = models.EmailField(blank=True, null=True, max_length=254)
    # phone1 = models.CharField(max_length=16, blank=True, null=True, db_index=True)
    # phone2 = models.CharField(max_length=16, blank=True, null=True)
    address_type = models.CharField(max_length=20, default='street', blank=True, null=True, help_text='mailing, remote or street address')
    # street1 = models.CharField(max_length=50, blank=True, null=True)
    address = AddressField(blank=True, null=True, on_delete=models.SET_NULL)
    address_extra = models.CharField(max_length=50, blank=True, null=True, help_text='i.e. Apartment number')
    # city = models.CharField(max_length=50, blank=True, null=True)
    # state = models.CharField(max_length=10, default='CA', blank=True, null=True)
    # zip_code = models.CharField(max_length=10, null=True, blank=True)
    # url = models.URLField(max_length=255, blank=True, null=True)
    # country = models.CharField(max_length=10, default='N/A', blank=True, null=True)
    fields = JSONField(default=dict, null=True, blank=True, help_text="please keep {} here even there's no data")

    def get_absolute_url(self):
        return reverse('contact_detail', args=[str(self.id)])

    # def clean(self):  #needs to check if fields are valid json (even empty json)
    #     if not (self.street1 or self.fields['phone1'] or self.fields['url'] or self.fields['email1']):
    #         raise ValidationError("You must specify at least a street or telephone or url or email")

# should validate the format of phone to be +1-123-456-7890 so it can be dialed directly on phones

    class Meta:
        db_table = 'whereabouts_contacts'
        verbose_name_plural = 'Contacts'
        ordering = ['created']
        indexes = [
            GinIndex(fields=['fields'], name='contact_fields_gin', ),
        ]

    @property
    def street(self):
        # return '{street1} {street2}'.format(street1=self.street1, street2=self.street2 or '').strip()
        return self.address.raw

    def __str__(self):
        return '%s, %s' % (self.display_name or self.attendees.first() or '', self.address or '')
