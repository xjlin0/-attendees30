from django.contrib.postgres.aggregates.general import ArrayAgg
from django.db.models import Q, Count, IntegerField
from django.db.models.expressions import Case, When

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
        orderby_list = AttendeeService.orderby_parser(orderby_string)

        init_query = Q(division__organization=current_user_organization).add(     # preventing browser hacks since
                      Q(attendings__meets__assembly__slug=assembly_slug), Q.AND)  # assembly_slug is from browser
        # need filter on attending_meet finish_date

        final_query = init_query.add(AttendeeService.filter_parser(filters_list), Q.AND)

        annotation_conditions = AttendeeService.annotation_parser(orderby_string)

        return Attendee.objects.select_related().prefetch_related().annotate(
                **annotation_conditions
                ).filter(final_query).order_by(*orderby_list)

    @staticmethod
    def orderby_parser(orderby_string):
        """
        Not supporting order by meet yet: it needs both annotation and order_by
        :param orderby_string: JSON fetched from search params, will convert attendee.division to attendee__division
        :return: a List of string for order_by()
        """
        orderby_list = []  # sort joined_meets is [{"selector":"<<dataField value in DataGrid>>","desc":false}]
        for orderby_dict in json.loads(orderby_string):
            direction = '-' if orderby_dict.get('desc', False) else ''
            field = orderby_dict.get('selector', 'id').replace('.', '__')
            orderby_list.append(direction + field)
        return orderby_list

    @staticmethod
    def annotation_parser(orderby_string):
        """
        Not supporting order by meet yet: it needs both annotation and order_by,
        (annotation create a new column, such as counting by conditions, for order by later)
        :param orderby_string: orderby_string: JSON fetched from search params
        :return: a dictionary of annotations
        """
        return {
            'joined_meets': ArrayAgg('attendings__meets__slug', distinct=True)  # , order='slug')
            # 'roaster_count': Count(Case(When(attendings__meets__slug='d7c8Fd_cfcc_congregation_roaster', then=1)))
            # 'joined_roaster': Count('attendings__meets__slug', filter=Q(attendings__meets__slug='d7c8Fd_cfcc_congregation_roaster'), distinct=True),
            # 'joined_roaster': Count(Case(When(attendings__meets__slug='d7c8Fd_cfcc_congregation_roaster', then=1), output_field=IntegerField())),
        }

    @staticmethod
    def filter_parser(filters_list):
        """
        A recursive method return Q function based on multi-level filter conditions
        :param filters_list: a string of multi-level list of filter conditions
        :return: Q function, could be an empty Q()
        """
        and_string = Q.AND.lower()
        or_string = Q.OR.lower()

        if filters_list:
            if and_string in filters_list and or_string in filters_list:
                raise Exception("Can't process both 'or'/'and' at the same level! please wrap them in separated lists.")
            elif filters_list[1] == and_string:
                and_list = [element for element in filters_list if element != and_string]
                and_query = AttendeeService.filter_parser(and_list[0])
                for and_element in and_list[1:]:
                    and_query.add(AttendeeService.filter_parser(and_element), Q.AND)
                return and_query
            elif filters_list[1] == or_string:
                or_list = [element for element in filters_list if element != or_string]
                or_query = AttendeeService.filter_parser(or_list[0])
                for or_element in or_list[1:]:
                    or_query.add(AttendeeService.filter_parser(or_element), Q.OR)
                return or_query
            elif filters_list[1] == '=':
                return Q(**{filters_list[0].replace('.', '__'): filters_list[2]})
            elif filters_list[1] == 'contains':
                return Q(**{AttendeeService.field_convert(filters_list[0]) + '__icontains': filters_list[2]})
        return Q()

    def field_convert(query_field):
        """
        some of the values are calculated cell values, and need to convert back to db field for search
        :return: string of fields in database
        """
        field_converter = {
            'self_phone_numbers': 'addresses__fields',
            'self_email_addresses': 'addresses__fields',
        }

        return field_converter.get(query_field, query_field).replace('.', '__')
