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
        orderby_list = []
        for orderby_dict in json.loads(orderby_string):
            direction = '-' if orderby_dict.get('desc', False) else ''
            field = orderby_dict.get('selector', 'id').replace('.', '__')  # convert attendee.division to attendee__division
            orderby_list.append(direction + field)

        # filters = {
        #     "division__organization":  current_user_organization,
        #     "attendings__meets__assembly__slug": assembly_slug,
        # } # merge the filters from
        # filters_list = ["division","=",2]
        # filterRow: [["names","contains","nameY"],"and",["division","=",2]]
        # searchPanel: [[["id","contains","idZ"],"and",["names","contains","nameX"],"and",["division","=",2]],"and",[["id","contains","nameY"],"or",["names","contains","nameY"]]]
        final_query = AttendeeService.parse_filter_arrays(
            query=Q(division__organization=current_user_organization).add(  # preventing browser hacks
                  Q(attendings__meets__assembly__slug=assembly_slug), Q.AND
            ),
            filters_list=filters_list,
        )

        return Attendee.objects.select_related().prefetch_related().annotate(
                meet_slugs=ArrayAgg('attendings__meets__slug', distinct=True, order='slug')
               ).filter(final_query).order_by(*orderby_list)

    @staticmethod
    def parse_filter_arrays(query, filters_list):
        # if filters_list:
        #     if isinstance(filters_list[0], list):  # this is a 2d list always using "and"
        #         pass
        #     else:  # this is only a 1d list simple filtering
        #         if filters_list[1]=='contains':
        #             pass

        return query

    @staticmethod
    def parse_unit_filter_array(filter_array):
        filters={}

        if filter_array:
            if filter_array[1] == '=':  # exact match from filter
                filters[filter_array[0]] = filter_array[2]

        return filters
