import time

from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed

from attendees.persons.models import Attending
from attendees.persons.serializers.attending_minimal_serializer import AttendingMinimalSerializer


class ApiAttendeeAttendingsViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Attending of an attendee to be viewed or edited.
    """
    serializer_class = AttendingMinimalSerializer

    def get_queryset(self):
        attendee_id = self.request.query_params.get('attendee-id', None)
        current_user_organization = self.request.user.organization
        if attendee_id and current_user_organization and self.request.user.privileged():  # Todo: scheduler should be able to do it too
            return Attending.objects.filter(
                attendee=attendee_id,
                attendee__division__organization=current_user_organization
            )  # With correct data this query will only work if current user's org is the same as targeting attendee's

        #     return AttendingService.by_assembly_meet_characters(
        #         assembly_slug=self.kwargs['assembly_slug'],
        #         meet_slugs=self.request.query_params.getlist('meets[]', []),
        #         character_slugs=self.request.query_params.getlist('characters[]', []),
        #     )
        # return Attending.objects.select_related().prefetch_related().filter(
        #     meets__slug__in=meet_slugs,
        #     attendingmeet__character__slug__in=character_slugs,
        #     meets__assembly__slug=assembly_slug,
        # ).distinct()

        else:
            time.sleep(2)
            raise AuthenticationFailed(detail='Are you data admin or counselor?')


api_attendee_attendings_viewset = ApiAttendeeAttendingsViewSet
