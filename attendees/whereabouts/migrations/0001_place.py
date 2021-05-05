# Generated by Django 3.0.2 on 2020-01-13 05:54

from uuid import uuid4
import attendees.persons.models.utility
from django.contrib.postgres.fields.jsonb import JSONField
from django.contrib.postgres.indexes import GinIndex
from django.db import migrations, models
import django.utils.timezone
from address.models import AddressField
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('whereabouts', '0000_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Place',
            fields=[
                # ('id', model_utils.fields.UUIDField(default=uuid4, editable=False, primary_key=True, serialize=False)),
                ('address_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to='address.Address')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('is_removed', models.BooleanField(default=False)),
                ('display_name', models.CharField(blank=True, null=True, db_index=True, max_length=50, help_text='optional label')),
                # ('email1', models.EmailField(blank=True, db_index=True, max_length=254, null=True)),
                # ('email2', models.EmailField(blank=True, max_length=254, null=True)),
                # ('phone1', models.CharField(blank=True, db_index=True, max_length=16, null=True)),
                # ('phone2', models.CharField(blank=True, max_length=16, null=True)),
                ('address_extra', models.CharField(max_length=50, blank=True, null=True, help_text='i.e. Apartment number')),
                ('address_type', models.CharField(max_length=20, default='street', blank=True, null=True, help_text='mailing, remote or street address')),
                # ('city', models.CharField(max_length=50, blank=True, null=True)),
                # ('state', models.CharField(default='CA', max_length=10, blank=True, null=True)),
                # ('zip_code', models.CharField(max_length=10, null=True, blank=True)),
                # ('url', models.URLField(blank=True, null=True, max_length=255)),
                # ('country', models.CharField(default='N/A', max_length=10, blank=True, null=True)),
                ('fields', JSONField(blank=True, default=dict, help_text="please keep {} here even there's no data", null=True)),
            ],
            options={
                'db_table': 'whereabouts_places',
                # 'verbose_name_plural': 'Contacts',
                'ordering': ('locality', 'route', 'street_number', 'address_extra'),
            },
            bases=(models.Model, attendees.persons.models.utility.Utility),
        ),
        # migrations.RemoveField(
        #     model_name='contact',
        #     name='id',
        # ),
        migrations.AddIndex(
            model_name='place',
            index=GinIndex(fields=['fields'], name='place_fields_gin'),
        ),
    ]