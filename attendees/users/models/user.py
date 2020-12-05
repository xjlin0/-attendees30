from django.contrib.auth.models import AbstractUser
from django.db.models import CharField
from django.db import models
from django.urls import reverse
from django.utils.translation import ugettext_lazy as _
from attendees.whereabouts.models import Organization


class User(AbstractUser):

    # First Name and Last Name do not cover name patterns
    # around the globe.
    name = CharField(_("Name of User"), blank=True, max_length=255)
    organization = models.ForeignKey(Organization, null=True, blank=True, default=None, on_delete=models.SET_NULL, help_text='Primary organization of the user')

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def belongs_to_groups_of(self, auth_group_names): #.in_bulk() might take more memory
        return self.groups.filter(name__in=auth_group_names).exists()

    def belongs_to_organization_of(self, organization_slug):
        if self.is_superuser:
            return True
        else:
            return self.organization and self.organization.slug == organization_slug

    def privileged(self):
        """
        check if user allowed to see other's data without relationships, currently are data_admins or counselor group
        :return: boolean
        """
        if self.organization:
            privileged_groups = self.organization.infos.get('data_admins', []) + self.organization.infos.get('counselor', [])
            return self.belongs_to_groups_of(privileged_groups)
        return False

    def is_data_admin(self):
        organization_data_admin_group = self.organization.infos.get('data_admins', []) if self.organization else None
        return self.belongs_to_groups_of(organization_data_admin_group)

    def is_counselor(self):
        organization_counselor_group = self.organization.infos['counselor'] if self.organization else None
        return self.belongs_to_groups_of([organization_counselor_group])

    def attendee_uuid_str(self):
        return str(self.attendee.id) if self.attendee else ''

    def attend_divisions_of(self, division_slugs):
        return self.attendee and self.attendee.attending_set.filter(divisions__slug__in=division_slugs).exists()

    def belongs_to_divisions_of(self, division_slugs):
        if self.is_superuser:
            return True
        else:
            return self.organization and self.organization.division_set.filter(slug__in=division_slugs).exists()

    def belongs_to_organization_and_division(self, organization_slug, division_slug):
        if self.is_superuser:
            return True
        else:
            return self.organization and self.organization.slug == organization_slug and self.organization.division_set.filter(slug=division_slug).exists()

    def attended_divisions_slugs(self):
        if self.attendee:
            return self.attendee.attending_set.values_list('division__slug', flat=True)
        else:
            return []
