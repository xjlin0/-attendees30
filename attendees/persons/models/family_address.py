from django.db import models
from model_utils.models import TimeStampedModel, SoftDeletableModel
from . import Utility


class FamilyAddress(TimeStampedModel, SoftDeletableModel, Utility):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    family = models.ForeignKey('Family', on_delete=models.CASCADE, null=False, blank=False)
    address = models.ForeignKey('whereabouts.Address', on_delete=models.CASCADE, null=False, blank=False)
    category = models.CharField(max_length=20, default='main', blank=False, null=False, help_text='main, resident, etc (main will be displayed first)')

    class Meta:
        db_table = 'persons_family_addresses'
        constraints = [
            models.UniqueConstraint(fields=['family', 'address'], name="family_address")
        ]

    def __str__(self):
        return '%s %s' % (self.family, self.address)
