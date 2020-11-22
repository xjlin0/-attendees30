from django.contrib.postgres.aggregates.general import ArrayAgg
from django.db.models import Q

from rest_framework.utils import json

from attendees.persons.models import Attendee


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
    def by_datagrid_params(current_user_organization, assembly_slug, orderby_string, filters_list):
        """
        :param current_user_organization:
        :param assembly_slug:
        :param orderby_string:
        :param filters_list:
        :return:
        """
        orderby_list = AttendeeService.filter_order(orderby_string)

        init_query = Q(division__organization=current_user_organization).add(     # preventing browser hacks since
                      Q(attendings__meets__assembly__slug=assembly_slug), Q.AND)  # assembly_slug is from browser

        final_query = init_query.add(AttendeeService.filter_parser(filters_list), Q.AND)

        return Attendee.objects.select_related().prefetch_related().annotate(
                meet_slugs=ArrayAgg('attendings__meets__slug', distinct=True, order='slug')
               ).filter(final_query).order_by(*orderby_list)

    @staticmethod
    def filter_order(orderby_string):
        orderby_list = []
        for orderby_dict in json.loads(orderby_string):
            direction = '-' if orderby_dict.get('desc', False) else ''
            field = orderby_dict.get('selector', 'id').replace('.', '__')  # convert attendee.division to attendee__division
            orderby_list.append(direction + field)
        return orderby_list

    @staticmethod
    def filter_parser(filters_list):
        if filters_list:
            if 'and' in filters_list and 'or' in filters_list:
                raise Exception('cannot process both or + and at the same level!')
            elif filters_list[1] == 'and':
                and_list = [element for element in filters_list if element != 'and']
                and_query = AttendeeService.filter_parser(and_list[0])
                for and_element in and_list[1:]:
                    and_query.add(AttendeeService.filter_parser(and_element), Q.AND)
                return and_query
            elif filters_list[1] == 'or':
                or_list = [element for element in filters_list if element != 'or']
                or_query = AttendeeService.filter_parser(or_list[0])
                for or_element in or_list[1:]:
                    or_query.add(AttendeeService.filter_parser(or_element), Q.OR)
                return or_query
            elif filters_list[1] == '=':
                return Q(**{filters_list[0].replace('.', '__'): filters_list[2]})
            elif filters_list[1] == 'contains':
                return Q(**{filters_list[0].replace('.', '__') + '__icontains': filters_list[2]})
        return Q()
