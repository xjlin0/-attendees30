from django.contrib.postgres.aggregates.general import ArrayAgg, JSONBAgg

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Func, Value
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from attendees.persons.models import Attendee
from attendees.persons.services import AttendeeService
from attendees.persons.serializers import AttendeeMinimalSerializer


class ApiRelatedAttendeesViewSet(LoginRequiredMixin, ModelViewSet):  # from GenericAPIView
    """
    API endpoint that allows single attendee to be viewed or edited.
    """
    serializer_class = AttendeeMinimalSerializer

    def get_queryset(self):
        """
        Return all related attendees by the attendee id in headers (key: X-TARGET-ATTENDEE-ID)
        When passing any attendee id as pk, it will return that attendee if current user is admin,
        but if the current user is NOT admin, it will only return that attendee only if the requested
        attendee were related.

        """
        current_user = self.request.user  # Todo 20210523: guard this API so only admin or scheduler can call it.
        target_attendee = get_object_or_404(Attendee, pk=self.request.META.get('HTTP_X_TARGET_ATTENDEE_ID'))
        querying_attendee_id = self.kwargs.get('pk')

        if querying_attendee_id:
            if current_user.privileged:
                Attendee.objects.filter(pk=querying_attendee_id)
            else:
                target_attendee.related_ones.filter(pk=querying_attendee_id)
        else:
            return target_attendee.related_ones.all()



api_related_attendees_viewset = ApiRelatedAttendeesViewSet
