from rest_framework.utils import json

from attendees.persons.models import Attendee, Attending


class AttendeeService:

    @staticmethod
    def by_assembly_meets(assembly_slug, meet_slugs):
        return Attendee.objects.filter(
                    attendings__meets__slug__in=meet_slugs,
                    attendings__meets__assembly__slug=assembly_slug,
                ).order_by(
                    'last_name',
                    'last_name2',
                    'first_name',
                    'first_name2'
                )

    @staticmethod
    def by_datagrid_params(current_user_organization, orderby_string):
        """
        :param assembly_slug:
        :param meet_slugs:
        :param character_slugs:
        :return:
        """
        orderby_list = []
        for orderby_dict in json.loads(orderby_string):
            direction = '-' if orderby_dict.get('desc', False) else ''
            field = orderby_dict.get('selector', 'id').replace('.', '__')  # convert attendee.division to attendee__division
            orderby_list.append(direction + field)

        meet_slugs = ['d7c8Fd-cfcc-congregation-roaster', 'd7c8Fd-cfcc-congregation-directory',
                      'd7c8Fd-cfcc-congregation-member', 'd7c8Fd-cfcc-congregation-care']
        character_slugs = ['d7c8Fd-cfcc-congregation-data-general', 'd7c8Fd-cfcc-congregation-data-member',
                           'd7c8Fd-cfcc-congregation-data-directory']
        assembly_slug = 'cfcc-congregation-data'

        return Attending.objects.filter(
            attendee__division__organization=current_user_organization,
            meets__slug__in=meet_slugs,
            attendingmeet__character__slug__in=character_slugs,
            meets__assembly__slug=assembly_slug,
        ).order_by(*orderby_list).distinct()
