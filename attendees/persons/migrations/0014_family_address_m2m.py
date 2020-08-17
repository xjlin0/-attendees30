# Generated by Django 3.0.6 on 2020-08-14 03:24

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('whereabouts', '0009_attendee_address_m2m'),
        ('persons', '0013_family_address'),
    ]

    operations = [
        migrations.AddField(
            model_name='family',
            name='addresses',
            field=models.ManyToManyField(through='persons.FamilyAddress', to='whereabouts.Address'),
        ),
    ]