from django.db import models
from model_utils.models import TimeStampedModel, SoftDeletableModel
from . import Utility


class FamilyContact(TimeStampedModel, SoftDeletableModel, Utility):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    family = models.ForeignKey('Family', on_delete=models.CASCADE, null=False, blank=False)
    contact = models.ForeignKey('whereabouts.Contact', on_delete=models.CASCADE, null=False, blank=False)
    category = models.CharField(max_length=20, default='main', blank=False, null=False, help_text='main, resident, etc (main will be displayed first)')

    class Meta:
        db_table = 'persons_family_contacts'
        constraints = [
            models.UniqueConstraint(fields=['family', 'contact'], name="family_contact")
        ]

    def __str__(self):
        return '%s %s' % (self.family, self.contact)
