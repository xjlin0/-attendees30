from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

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
            family__in=attendee.families.all()
        ).order_by(
            'family', 'role__display_order',
        )  # Todo: 20210515 add filter by start/finish for end users but not data-admins


api_datagrid_data_family_attendees_viewset = ApiDatagridDataFamilyAttendeesViewsSet
