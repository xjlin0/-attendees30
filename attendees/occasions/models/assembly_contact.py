from django.db import models
from django.contrib.contenttypes.fields import GenericRelation

from model_utils.models import TimeStampedModel, SoftDeletableModel

from attendees.persons.models import Utility, Note

from . import Assembly


class AssemblyContact(TimeStampedModel, SoftDeletableModel, Utility):
    notes = GenericRelation(Note)
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    assembly = models.ForeignKey(Assembly, on_delete=models.SET(0), null=False, blank=False)
    contact = models.ForeignKey('whereabouts.Contact', on_delete=models.CASCADE, null=False, blank=False)
    category = models.CharField(max_length=20, default='normal', null=True, help_text="primary, backup, etc")

    class Meta:
        db_table = 'occasions_assembly_contacts'
        verbose_name_plural = 'Assembly Contacts'
        constraints = [
            models.UniqueConstraint(fields=['assembly', 'contact'], name="assembly_contact")
        ]

    def __str__(self):
        return '%s %s' % (self.assembly or '', self.contact or '')
