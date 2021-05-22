# Generated by Django 3.0.5 on 2020-05-02 19:15

from django.db import migrations, models
import django.utils.timezone
import model_utils.fields


class Migration(migrations.Migration):

    dependencies = [
        ('persons', '0011_attendance_m2m'),
    ]

    operations = [
        migrations.CreateModel(
            name='FamilyAttendee',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', model_utils.fields.AutoCreatedField(default=django.utils.timezone.now, editable=False, verbose_name='created')),
                ('modified', model_utils.fields.AutoLastModifiedField(default=django.utils.timezone.now, editable=False, verbose_name='modified')),
                ('is_removed', models.BooleanField(default=False)),
                ('display_order', models.SmallIntegerField(db_index=True, default=1, help_text="0 will be first family")),
                ('attendee', models.ForeignKey(on_delete=models.CASCADE, to='persons.Attendee')),
                ('family', models.ForeignKey(on_delete=models.CASCADE, to='persons.Family')),
                ('role', models.ForeignKey(help_text='[Title] the family role of the attendee?', on_delete=models.SET(0), related_name='role', to='persons.Relation', verbose_name='attendee is')),
                ('start', models.DateField(blank=True, null=True, help_text='date joining family')),
                ('finish', models.DateField(blank=True, null=True, help_text='date leaving family')),
            ],
            options={
                'db_table': 'persons_family_attendees',
                'ordering': ('display_order',),
            },
        ),
        migrations.AddField(
            model_name='attendee',
            name='families',
            field=models.ManyToManyField(related_name='families', through='persons.FamilyAttendee', to='persons.Family'),
        ),
        migrations.AddConstraint(
            model_name='familyattendee',
            constraint=models.UniqueConstraint(fields=('family', 'attendee'), name='family_attendee'),
        ),
        migrations.AddField(
            model_name='family',
            name='attendees',
            field=models.ManyToManyField(related_name='attendees', through='persons.FamilyAttendee',
                                         to='persons.Attendee'),
        ),
    ]
