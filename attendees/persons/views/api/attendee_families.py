from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

from rest_framework import viewsets

from attendees.persons.models import Attendee
from attendees.persons.serializers import FamilySerializer
from attendees.users.authorization.route_guard import SpyGuard


class ApiAttendeeFamiliesViewsSet(LoginRequiredMixin, SpyGuard, viewsets.ModelViewSet):
    """
    API endpoint that allows families(attendees) of a single Attendee to be viewed or edited.
    """
    serializer_class = FamilySerializer

    def get_queryset(self):
        attendee = get_object_or_404(Attendee, pk=self.kwargs.get('attendee_id'))
        return attendee.families.all().order_by('display_order')


api_attendee_families_viewset = ApiAttendeeFamiliesViewsSet
