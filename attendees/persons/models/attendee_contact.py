from django.db import models
from model_utils.models import TimeStampedModel, SoftDeletableModel
from . import Utility


class AttendeeContact(TimeStampedModel, SoftDeletableModel, Utility):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    attendee = models.ForeignKey('Attendee', on_delete=models.CASCADE, null=False, blank=False)
    # contact = models.ForeignKey('whereabouts.Contact', on_delete=models.CASCADE, null=False, blank=False)
    # category = models.CharField(max_length=20, default='main', blank=False, null=False, help_text='main, resident, etc (main will be displayed first)')
    display_name = models.CharField(db_index=True, max_length=50, default='main', blank=False, null=False, help_text='main, resident, etc (main will be displayed first)')
    display_order = models.SmallIntegerField(default=0, blank=False, null=False)
    #need to validate there only one 'main' for display_name

    class Meta:
        db_table = 'persons_attendee_contacts'
        ordering = ('display_order',)
        constraints = [
            models.UniqueConstraint(fields=['attendee', 'contact'], name="attendee_contact")
        ]

    def __str__(self):
        return '%s %s' % (self.attendee, self.contact)
