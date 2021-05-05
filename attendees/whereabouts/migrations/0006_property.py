# Generated by Django 3.0.2 on 2020-01-14 06:35

import attendees.persons.models.utility
from django.db import migrations, models
import django.db.models.deletion
from django.contrib.postgres.fields.jsonb import JSONField
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('whereabouts', '0005_campus'),
    ]

    operations = [
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('is_removed', models.BooleanField(default=False)),
                ('campus', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='whereabouts.Campus')),
                ('display_name', models.CharField(db_index=True, max_length=50)),
                ('slug', models.SlugField(max_length=50, unique=True)),
                ('infos', JSONField(blank=True, default=dict, help_text='Example: {"2010id": "3"}. Please keep {} here even no data', null=True)),

            ],
            options={
                'db_table': 'whereabouts_properties',
                'verbose_name_plural': 'Properties',
            },
            bases=(models.Model, attendees.persons.models.utility.Utility),
        ),
        migrations.AddIndex(
            model_name='property',
            index=django.contrib.postgres.indexes.GinIndex(fields=['infos'], name='property_infos_gin'),
        ),
    ]
