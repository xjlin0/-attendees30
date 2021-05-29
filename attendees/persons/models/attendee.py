from opencc import OpenCC

from django.db import models
from django.conf import settings
from django.core.exceptions import ValidationError
from django.contrib.contenttypes.fields import GenericRelation
from django.contrib.postgres.fields.jsonb import JSONField
from django.contrib.postgres.indexes import GinIndex
from django.urls import reverse
from django.utils.functional import cached_property
from datetime import datetime, timezone, date, timedelta
from model_utils.models import TimeStampedModel, SoftDeletableModel, UUIDModel
from private_storage.fields import PrivateFileField
from . import GenderEnum, Note, Utility


class Attendee(UUIDModel, Utility, TimeStampedModel, SoftDeletableModel):
    # RELATIVES_KEYWORDS = ['parent', 'mother', 'guardian', 'father', 'caregiver']
    # AS_PARENT_KEYWORDS = ['notifier', 'caregiver']  # to find attendee's parents/caregiver in cowokers view of all activities
    # BE_LISTED_KEYWORDS = ['care receiver']  # let the attendee's attendance showed in their parent/caregiver account
    pasts = GenericRelation('persons.Past')
    places = GenericRelation('whereabouts.Place')
    notes = GenericRelation(Note)
    related_ones = models.ManyToManyField('self', through='Relationship', symmetrical=False, related_name='related_to')
    division = models.ForeignKey('whereabouts.Division', default=0, null=False, blank=False, on_delete=models.SET(0))
    user = models.OneToOneField(settings.AUTH_USER_MODEL, default=None, null=True, blank=True, on_delete=models.SET_NULL)
    families = models.ManyToManyField('persons.Family', through='FamilyAttendee', related_name='families')
    first_name = models.CharField(max_length=25, db_index=True, null=True, blank=True)
    last_name = models.CharField(max_length=25, db_index=True, null=True, blank=True)
    first_name2 = models.CharField(max_length=12, db_index=True, null=True, blank=True)
    last_name2 = models.CharField(max_length=8, db_index=True, null=True, blank=True)
    gender = models.CharField(max_length=11, blank=False, null=False, default=GenderEnum.UNSPECIFIED, choices=GenderEnum.choices())
    actual_birthday = models.DateField(blank=True, null=True)
    estimated_birthday = models.DateField(blank=True, null=True)
    deathday = models.DateField(blank=True, null=True)
    photo = PrivateFileField("Photo", blank=True, null=True, upload_to="attendee_portrait") #https://github.com/edoburu/django-private-storage
    progressions = JSONField(null=True, blank=True, default=dict, help_text='Example: {"Christian": true, "baptized": {"time": "12/31/2020", "place":"SF"}}. Please keep {} here even no data')
    infos = JSONField(null=True, blank=True, default=Utility.attendee_infos, help_text='Example: {"fixed": {"food_pref": "peanut allergy", "nick_name": "John"}}. Please keep {} here even no data')

    @property
    def display_label(self):
        return (self.first_name or '') + ' ' + (self.last_name or '') + ' ' + (self.last_name2 or '') + (self.first_name2 or '')

    @property
    def division_label(self):
        return self.division.display_name if self.division else None

    @cached_property
    def family_members(self):
        return self.__class__.objects.filter(families__in=self.families.all()).distinct()

    @cached_property
    def self_phone_numbers(self):
        return self.self_addresses_for_fields_of(['phone1', 'phone2'])

    @cached_property
    def self_email_addresses(self):
        return self.self_addresses_for_fields_of(['email1', 'email2'])

    def self_addresses_for_fields_of(self, fields):
        contacts = self.infos.get('contacts', {})
        return ', '.join([contacts.get(field) for field in fields if contacts.get(field)])

    @cached_property
    def caregiver_email_addresses(self):
        return self.caregiver_addresses_for_fields_of(['email1', 'email2'])

    @cached_property
    def caregiver_phone_numbers(self):
        return self.caregiver_addresses_for_fields_of(['phone1', 'phone2'])

    def caregiver_addresses_for_fields_of(self, fields):
        return ', '.join(set(
            a.self_addresses_for_fields_of(fields) for a in
                self.get_relative_emergency_contacts()
        ))

    def get_relative_emergency_contacts(self):
        return self.related_ones.filter(
                    to_attendee__relation__relative=True,
                    to_attendee__relation__emergency_contact=True,
                    to_attendee__finish__gte=datetime.now(timezone.utc),
                )

    def under_same_org_with(self, other_attendee_id):
        if other_attendee_id:
            return Attendee.objects.filter(pk=other_attendee_id, division__organization=self.division.organization).exists()
        return False

    @cached_property
    def parents_notifiers_names(self):
        """
        :return: attendees' names of their parents/caregiviers
        """
        return ', '.join(list(
                            self.get_relative_emergency_contacts().order_by(
                                '-to_attendee__relation__display_order',
                            ).values_list(
                                'infos__names__original',
                                flat=True
                            )
                        )
                    )

    def age(self):
        birthday = self.actual_birthday or self.estimated_birthday
        try:
            if birthday:
                return (date.today() - birthday) // timedelta(days=365.2425)
            else:
                return None
        except Exception as e:
            print(self.__str__() + "'s birthday incorrect: ", birthday, '. Type: ', type(birthday), ' exception: ', e)
            return None

    def __str__(self):
        return self.display_label

    # def all_relations(self): #cannot import Relationship, probably needs native query
    #     return dict(((r.from_attendee, r.relation) if r.to_attendee == self else (r.to_attendee, r.relation) for r in Relationship.objects.filter(Q(from_attendee=self.id) | Q(to_attendee=self.id))))
    # switching to symmetrical False with Facebook model (but add relationship both ways and need add/remove_relationship methods) http://charlesleifer.com/blog/self-referencing-many-many-through/
    # also attendee.related_ones will return deleted relationship, so extra filter is required (.filter(relationship__is_removed = False))

    def clean(self):
        if not (self.last_name or self.last_name2):
            raise ValidationError("You must specify a last_name")

    def get_absolute_url(self):
        return reverse('/persons/attendee_detail_view/', kwargs={'pk': self.pk})

    class Meta:
        db_table = 'persons_attendees'
        ordering = ['last_name', 'first_name']
        indexes = [
            GinIndex(fields=['infos'], name='attendee_infos_gin', ),
            GinIndex(fields=['progressions'], name='attendee_progressions_gin', ),
        ]

    def save(self, *args, **kwargs):
        name = f"{self.first_name or ''} {self.last_name or ''}".strip()
        name2 = f"{self.last_name2 or ''}{self.first_name2 or ''}".strip()
        self.infos['names']['original'] = f"{name} {name2}".strip()
        if self.division.organization.infos.get('flags', {}).get('opencc_convert'):  # Let search work in either language
            self.infos['names']['traditional'] = OpenCC('s2t').convert(name2)
            self.infos['names']['simplified'] = OpenCC('t2s').convert(name2)
        # if self.division.organization.infos.flags.accent_convert:  # For Spanish, Not in V1
        #     self.infos['names']['unaccented'] = converter(name)
        super(Attendee, self).save(*args, **kwargs)

    # class ReadonlyMeta:
    #     readonly = ["full_name"]  # generated column
