from django.db import models
from model_utils.models import TimeStampedModel, SoftDeletableModel


class Category(TimeStampedModel, SoftDeletableModel):
    id = models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')
    slug = models.SlugField(max_length=50, help_text='uniq key', blank=False, null=False, unique=True)
    type = models.CharField(max_length=25, default='generic', db_index=True, blank=False, null=False, help_text='main type')
    display_name = models.CharField(max_length=50, blank=True, null=True)
    display_order = models.SmallIntegerField(default=0, blank=False, null=False, db_index=True)
    description = models.CharField(max_length=50, blank=True, null=True)

    def __str__(self):
        return '%s %s %s %s' % (self.display_name, self.slug, self.description, self.display_order)

    class Meta:
        db_table = 'persons_categories'
        verbose_name_plural = 'Categories'
        ordering = ('type', 'display_order')

