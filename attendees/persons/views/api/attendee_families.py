from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

from rest_framework import viewsets

from attendees.persons.models import Attendee
from attendees.persons.serializers import FamilySerializer
from attendees.users.authorization.route_guard import SpyGuard


class ApiAttendeeFamiliesViewsSet(LoginRequiredMixin, SpyGuard, viewsets.ModelViewSet):
    """
    API endpoint that allows families of an Attendee (in header) to be viewed or edited.
    """
    serializer_class = FamilySerializer

    def get_queryset(self):
        attendee = get_object_or_404(Attendee, pk=self.request.META.get('HTTP_X_TARGET_ATTENDEE_ID'))
        family_id = self.kwargs.get('pk')
        if family_id:
            return attendee.families.filter(pk=family_id)
        else:
            return attendee.families.order_by('display_order')


api_attendee_families_viewset = ApiAttendeeFamiliesViewsSet
