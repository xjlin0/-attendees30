from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

from rest_framework import viewsets

from attendees.persons.models import Attendee
from attendees.persons.serializers import FamilySerializer
from attendees.users.authorization.route_guard import SpyGuard


class ApiAttendeeFamiliesViewsSet(LoginRequiredMixin, SpyGuard, viewsets.ModelViewSet):
    """
    API endpoint that allows families(attendees) of an Attendee to be viewed or edited.
    """
    serializer_class = FamilySerializer

    def get_queryset(self):
        attendee = get_object_or_404(Attendee, pk=self.kwargs.get('attendee_id'))
        family_id = self.request.query_params.get('family_id')
        if family_id:
            return attendee.families.filter(pk=family_id)
        else:
            return attendee.families.order_by('display_order')


api_attendee_families_viewset = ApiAttendeeFamiliesViewsSet
