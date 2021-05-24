from django.contrib.postgres.aggregates.general import ArrayAgg
from django.db.models import Q, F, Func, Case, When, Value
from django.db.models.expressions import OrderBy
from django.http import Http404

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
    def get_related_ones_by_permission(current_user, checking_attendee_id):
        """
        data admin can check all attendee and their related_ones. User can check other attendee if user is that attendee's scheduler
        :param current_user: current_user
        :param checking_attendee_id: the attendee_id requested
        :return: user's related attendees if no attendee id provided, or the requested related attendees if by scheduler, or empty set.
        """
        user_attendee = Attendee.objects.filter(user=current_user).first()

        if user_attendee:
            user_checking_id = checking_attendee_id or user_attendee.id
            if current_user.privileged:
                return Attendee.objects.filter(
                    Q(id=user_checking_id)
                    |
                    Q(from_attendee__to_attendee__id=user_checking_id, from_attendee__scheduler=True)
                    # Todo: add all families for data managers
                ).distinct().order_by(
                    OrderBy(Func(F('id'), function="'{}'=".format(user_checking_id)), descending=True),
                    'infos__names__original',
                )
            else:
                return Attendee.objects.filter(
                    Q(id=user_attendee.id)
                    |
                    Q(from_attendee__to_attendee__id=user_attendee.id, from_attendee__scheduler=True)
                ).distinct().order_by(
                    OrderBy(Func(F('id'), function="'{}'=".format(user_attendee.id)), descending=True),
                    'infos__names__original',
                )

        else:
            raise Http404('Your profile does not have attendee')

    @staticmethod
    def details(current_user, attendee_id):

        return []

    @staticmethod
    def find_related_ones(current_user, target_attendee, querying_attendee_id, filters_list):
        """
        return target_attendee's related ones according to current_user permissions
        :param current_user:
        :param target_attendee:
        :param querying_attendee_id:
        :param filters_list:
        :return: related attendees of targeting attendee, or matched attendee depends on filter conditions and current user permissions
        """

        # # Todo: need filter on attending_meet finish_date

        if querying_attendee_id:
            if current_user.privileged:
                qs = Attendee.objects

            else:
                qs = target_attendee.related_ones

            return qs.filter(
                    pk=querying_attendee_id,
                    division__organization=current_user.organization,
                    )
        else:
            init_query = Q(division__organization=current_user.organization)
            final_query = init_query.add(AttendeeService.filter_parser(filters_list, None), Q.AND)

            if current_user.privileged:
                return Attendee.objects.filter(final_query).order_by(
                    Case(When(id__in=target_attendee.related_ones.values_list('id'), then=0), default=1)
                )  # https://stackoverflow.com/a/52047221/4257237
            else:
                return target_attendee.related_ones.all()

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

        init_query = Q(attendings__meets__assembly__slug=assembly_slug)  # assembly_slug is from browser
        # Todo: need filter on attending_meet finish_date

        final_query = init_query.add(AttendeeService.filter_parser(filters_list, assembly_slug), Q.AND)

        return Attendee.objects.select_related().prefetch_related().annotate(
                    joined_meets=ArrayAgg('attendings__meets__slug', distinct=True),
                ).filter(final_query).filter(
                    division__organization=current_user_organization  #Bugfix 20210517 limit org in init_query doesn't work.
                ).order_by(*orderby_list)

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

    @staticmethod
    def field_convert(query_field, assembly_slug):
        """
        some of the values are calculated cell values, and need to convert back to db field for search
        :return: string of fields in database
        """
        field_converter = {
            'self_phone_numbers': 'infos__contacts',
            'self_email_addresses': 'infos__contacts',
        }
        if assembly_slug:
            for meet in Meet.objects.filter(assembly__slug=assembly_slug):
                field_converter[meet.slug] = 'attendings__meets__display_name'

        return field_converter.get(query_field, query_field).replace('.', '__')
