# Generated by Django 3.0.2 on 2020-01-13 02:58
from uuid import uuid4

from django.conf import settings
from django.db import migrations, models
from django.contrib.postgres.fields.jsonb import JSONField
from private_storage.fields import PrivateFileField
from private_storage.storage.files import PrivateFileSystemStorage
import django.utils.timezone
import model_utils.fields

from attendees.persons.models.enum import GenderEnum
from attendees.persons.models import Utility


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0005_family'),
        ('whereabouts', '0004_division'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Attendee',
            fields=[
                ('id', model_utils.fields.UUIDField(default=uuid4, editable=False, primary_key=True, serialize=False)),
                ('user', models.OneToOneField(blank=True, default=None, null=True, on_delete=models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('is_removed', models.BooleanField(default=False)),
                ('division', models.ForeignKey(default=0, blank=False, null=False, on_delete=models.SET(0), to='whereabouts.Division')),
                ('actual_birthday', models.DateField(blank=True, null=True)),
                ('estimated_birthday', models.DateField(blank=True, null=True)),
                ('deathday', models.DateField(blank=True, null=True)),
                ('first_name', models.CharField(blank=True, db_index=True, max_length=25, null=True)),
                ('last_name', models.CharField(blank=True, db_index=True, max_length=25, null=True)),
                ('first_name2', models.CharField(blank=True, db_index=True, max_length=12, null=True)),
                ('last_name2', models.CharField(blank=True, db_index=True, max_length=8, null=True)),
                ('gender', models.CharField(choices=GenderEnum.choices(), default=GenderEnum.UNSPECIFIED, max_length=11)),
                ('photo', PrivateFileField(blank=True, null=True, storage=PrivateFileSystemStorage(), upload_to='attendee_portrait', verbose_name='Photo')),
                ('progressions', JSONField(blank=True, default=dict, help_text='Example: {"Christian": true, "baptized": {"time": "12/31/2020", "place":"SF"}}. Please keep {} here even no data', null=True)),
                ('infos', JSONField(blank=True, null=True, default=Utility.attendee_infos, help_text='Example: {"fixed": {"food_pref": "peanut allergy", "nick_name": "John"}}. Please keep {} here even no data')),
            ],
            options={
                'db_table': 'persons_attendees',
                'ordering': ['last_name', 'first_name'],
            },
            bases=(Utility, models.Model),
        ),
        # migrations.RunSQL(
        #     sql="""
        #         ALTER TABLE persons_attendees DROP COLUMN full_name;
        #         ALTER TABLE persons_attendees ADD COLUMN full_name VARCHAR(70)
        #               GENERATED ALWAYS AS (TRIM(
        #                 COALESCE(first_name, '') || ' ' ||
        #                 COALESCE(last_name, '')  || ' ' ||
        #                 COALESCE(last_name2, '')   ||
        #                 COALESCE(first_name2, '')
        #               )) STORED;
        #         CREATE INDEX attendee_full_name_raw
        #           ON persons_attendees (full_name);
        #         """,
        #     # reverse_sql="",
        # ),  # switching to use opencc for language conversion in Attendee.save()
        migrations.AddIndex(
            model_name='attendee',
            index=django.contrib.postgres.indexes.GinIndex(fields=['infos'], name='attendee_infos_gin'),
        ),
        migrations.AddIndex(
            model_name='attendee',
            index=django.contrib.postgres.indexes.GinIndex(fields=['progressions'], name='attendee_progressions_gin'),
        ),
    ]
