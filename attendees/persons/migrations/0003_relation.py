# Generated by Django 3.0.5 on 2020-04-29 00:52

from django.db import migrations, models
from django.contrib.postgres.fields import ArrayField
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0002_note'),
    ]

    operations = [
        migrations.CreateModel(
            name='Relation',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('is_removed', models.BooleanField(default=False)),
                ('reciprocal_ids', ArrayField(base_field=models.BigIntegerField(), blank=True, default=list, help_text="Have to be completely empty or in the shape of '1,2,3', no brackets", null=True, size=None, verbose_name='corresponding relation ids')),
                ('title', models.CharField('To be called', max_length=50, blank=False, null=False, unique=True)),
                ('display_order', models.SmallIntegerField(default=0, blank=False, null=False, db_index=True)),
                ('emergency_contact', models.BooleanField('to be the emergency contact?', default=False, null=False, blank=False, help_text="default value, can be changed in relationships further")),
                ('scheduler', models.BooleanField('to be the scheduler?', default=False, null=False, blank=False, help_text="default value, can view/change the schedules of the caller?")),
                ('relative', models.BooleanField('is a relative?', default=False, null=False, blank=False, help_text="default value, can be changed in relationships further")),
            ],
            options={
                'db_table': 'persons_relations',
                'ordering': ('display_order', 'title'),
            },
        ),
    ]
