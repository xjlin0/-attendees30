from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets

from attendees.persons.models import Attendee, FamilyAttendee
from attendees.persons.serializers import FamilyAttendeeSerializer
from attendees.users.authorization.route_guard import SpyGuard


class ApiDatagridDataFamilyAttendeesViewsSet(LoginRequiredMixin, SpyGuard, viewsets.ModelViewSet):
    """
    API endpoint that allows families(attendees) of a single Attendee to be viewed or edited.
    """
    serializer_class = FamilyAttendeeSerializer

    def get_queryset(self):
        attendee = get_object_or_404(Attendee, pk=self.kwargs.get('attendee_id'))
        return FamilyAttendee.objects.filter(
            family__in=attendee.families.all().order_by('display_order')
        ).order_by(  # Todo: 20210516 order by attendee's family attendee display_order, such as order_by annotate()
            '-family__created', 'role__display_order',
        )  # Todo: 20210515 add filter by start/finish for end users but not data-admins


    # def update(self, request, *args, **kwargs):
    #     print("hi 27 here is request: ")
    #     print(request)
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #
    #     if getattr(instance, '_prefetched_objects_cache', None):
    #         # If 'prefetch_related' has been applied to a queryset, we need to
    #         # refresh the instance from the database.
    #         instance = self.get_object()
    #         serializer = self.get_serializer(instance)
    #
    #     return Response(serializer.data)
    #
    # def perform_update(self, serializer):
    #     serializer.save()
    #
    # def partial_update(self, request, *args, **kwargs):
    #     print("hi 47 here is request: ")
    #     print(request)
    #     kwargs['partial'] = True
    #     return self.update(request, *args, **kwargs)


api_datagrid_data_family_attendees_viewset = ApiDatagridDataFamilyAttendeesViewsSet
