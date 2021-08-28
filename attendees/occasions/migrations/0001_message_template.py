# Generated by Django 3.0.14 on 2021-08-28 17:55

from django.contrib.postgres.fields.jsonb import JSONField
from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('whereabouts', '0002_minimal_place'),
        ('occasions', '0000_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='MessageTemplate',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('is_removed', models.BooleanField(default=False)),
                ('organization', models.ForeignKey(null=False, blank=False, on_delete=models.SET(0), to='whereabouts.Organization')),
                ('template', models.TextField(null=False, blank=False, help_text='whatever in curly braces will be interpolated by variables')),
                ('defaults', JSONField(null=True, blank=True, default=dict, help_text='Example: {"name": "John", "Date": "08/31/2020"}. Please keep {} here even no data')),
                ('type', models.SlugField(blank=False, null=False, help_text='format: Organization_slug-prefix-message-type-name')),

            ],
            options={
                'db_table': 'occasions_message_templates',
            },
        ),
        migrations.AddConstraint(
            model_name='messagetemplate',
            constraint=models.UniqueConstraint(condition=models.Q(is_removed=False), fields=('organization', 'type'), name='organization_type'),
        ),
    ]
