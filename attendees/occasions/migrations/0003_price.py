# Generated by Django 3.0.2 on 2020-01-14 04:14

import attendees.persons.models.utility
import django.core.validators
from django.db import migrations, models
import django.db.models.deletion
import django.db.models.manager
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('occasions', '0002_assembly_address'),
    ]

    operations = [
        migrations.CreateModel(
            name='Price',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('start', models.DateTimeField(blank=False, null=False)),
                ('finish', models.DateTimeField(blank=False, null=False)),
                ('is_removed', models.BooleanField(default=False)),
                ('display_name', models.CharField(max_length=50)),
                ('price_type', models.CharField(db_index=True, max_length=20)),
                ('price_value', models.DecimalField(decimal_places=2, default=999999, max_digits=8, validators=[django.core.validators.MinValueValidator(0)])),
                ('assembly', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='occasions.Assembly')),
            ],
            options={
                'db_table': 'occasions_prices',
            },
            bases=(models.Model, attendees.persons.models.utility.Utility),
        ),
    ]
