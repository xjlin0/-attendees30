from django.contrib.postgres.aggregates.general import ArrayAgg
from django.db.models import Q, F, Func, Value
from django.db.models.expressions import OrderBy

from rest_framework.utils import json

from attendees.occasions.models import Meet
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
        orderby_list = AttendeeService.orderby_parser(orderby_string, assembly_slug)

        init_query = Q(division__organization=current_user_organization).add(     # preventing browser hacks since
                      Q(attendings__meets__assembly__slug=assembly_slug), Q.AND)  # assembly_slug is from browser
        # Todo: need filter on attending_meet finish_date

        final_query = init_query.add(AttendeeService.filter_parser(filters_list, assembly_slug), Q.AND)

        return Attendee.objects.select_related().prefetch_related().annotate(
                joined_meets=ArrayAgg('attendings__meets__slug', distinct=True),
                ).filter(final_query).order_by(*orderby_list)

    @staticmethod
    def orderby_parser(orderby_string, assembly_slug):
        """
        generates sorter (column or OrderBy Func) based on user's choice
        :param orderby_string: JSON fetched from search params, will convert attendee.division to attendee__division
        :param assembly_slug: assembly_slug
        :return: a List of sorter for order_by()
        """
        meet_sorters = {meet.slug: Func(F('joined_meets'), function="'{}'=ANY".format(meet.slug)) for meet in Meet.objects.filter(assembly__slug=assembly_slug)}

        orderby_list = []  # sort joined_meets is [{"selector":"<<dataField value in DataGrid>>","desc":false}]
        for orderby_dict in json.loads(orderby_string):
            field = orderby_dict.get('selector', 'id').replace('.', '__')
            if field in meet_sorters:
                sorter = OrderBy(meet_sorters[field], descending=orderby_dict.get('desc', False))
                orderby_list.append(sorter)
            else:
                direction = '-' if orderby_dict.get('desc', False) else ''
                orderby_list.append(direction + field)
        return orderby_list

    @staticmethod
    def filter_parser(filters_list, assembly_slug):
        """
        A recursive method return Q function based on multi-level filter conditions
        :param filters_list: a string of multi-level list of filter conditions
        :param assembly_slug: assembly_slug
        :return: Q function, could be an empty Q()
        """
        and_string = Q.AND.lower()
        or_string = Q.OR.lower()

        if filters_list:
            if and_string in filters_list and or_string in filters_list:
                raise Exception("Can't process both 'or'/'and' at the same level! please wrap them in separated lists.")
            elif filters_list[1] == and_string:
                and_list = [element for element in filters_list if element != and_string]
                and_query = AttendeeService.filter_parser(and_list[0], assembly_slug)
                for and_element in and_list[1:]:
                    and_query.add(AttendeeService.filter_parser(and_element, assembly_slug), Q.AND)
                return and_query
            elif filters_list[1] == or_string:
                or_list = [element for element in filters_list if element != or_string]
                or_query = AttendeeService.filter_parser(or_list[0], assembly_slug)
                for or_element in or_list[1:]:
                    or_query.add(AttendeeService.filter_parser(or_element, assembly_slug), Q.OR)
                return or_query
            elif filters_list[1] == '=':
                return Q(**{filters_list[0].replace('.', '__'): filters_list[2]})
            elif filters_list[1] == 'contains':
                return Q(**{AttendeeService.field_convert(filters_list[0], assembly_slug) + '__icontains': filters_list[2]})
        return Q()

    def field_convert(query_field, assembly_slug):
        """
        some of the values are calculated cell values, and need to convert back to db field for search
        :return: string of fields in database
        """
        field_converter = {
            'self_phone_numbers': 'addresses__fields',
            'self_email_addresses': 'addresses__fields',
        }

        for meet in Meet.objects.filter(assembly__slug=assembly_slug):
            field_converter[meet.slug] = 'attendings__meets__display_name'

        return field_converter.get(query_field, query_field).replace('.', '__')
