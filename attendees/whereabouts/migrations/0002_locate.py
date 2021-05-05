# Generated by Django 3.0.2 on 2020-01-21 06:04

import attendees.persons.models.utility
from django.contrib.postgres.fields.jsonb import JSONField
from django.contrib.postgres.indexes import GinIndex
from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('whereabouts', '0001_place'),
    ]

    operations = [
        migrations.CreateModel(
            name='Locate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('is_removed', models.BooleanField(default=False)),
                ('place', models.ForeignKey(on_delete=models.CASCADE, to='whereabouts.Place', null=False, blank=False)),
                ('content_type', models.ForeignKey(on_delete=models.CASCADE, to='contenttypes.ContentType', null=False, blank=False)),
                # ('category', models.CharField(max_length=20, default='main', blank=False, null=False, help_text='main, resident, etc (main will be displayed first)')),
                ('display_order', models.SmallIntegerField(blank=False, default=0, null=False)),
                ('object_id', models.CharField(max_length=36, null=False, blank=False)),
                ('start', models.DateTimeField(blank=True, null=True, help_text='optional')),
                ('finish', models.DateTimeField(blank=True, null=True, help_text='optional')),
                ('display_name', models.CharField(db_index=True, max_length=50, default='main', blank=False, null=False, help_text='main, resident, etc (main will be displayed first)')),
                ('fields', JSONField(blank=True, default=dict, help_text="please keep {} here even there's no data", null=True)),
            ],
            options={
                'db_table': 'whereabouts_locates',
                'ordering': ('display_order',),
            },
            bases=(models.Model, attendees.persons.models.utility.Utility),
        ),
        # migrations.AddField(
        #     model_name='attendee',
        #     name='contacts',
        #     field=models.ManyToManyField(through='persons.Locate', to='whereabouts.Place', related_name='contacts'),
        # ),
        migrations.AddConstraint(
            model_name='locate',
            constraint=models.UniqueConstraint(fields=('place', 'content_type', 'object_id'), name='place_object'),
        ),
        migrations.AddIndex(
            model_name='locate',
            index=GinIndex(fields=['fields'], name='locate_fields_gin'),
        ),
    ]