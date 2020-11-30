import time

from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed

from attendees.occasions.services import AttendanceService

from attendees.occasions.serializers import AttendanceSerializer
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from attendees.persons.models import Attendee


@method_decorator([login_required], name='dispatch')
class ApiFamilyOrganizationAttendancesViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Attendances to be viewed.   All authenticated user (and
    the users kids/care receiver)'s Attendance will be shown.
    """
    serializer_class = AttendanceSerializer

    def get_queryset(self):
        """
        :permission: this API is only for authenticated users (participants, coworker or organization).
                     Anonymous users should not get any info from this API.
        :query: Find all gatherings of all Attendances of the current user and their kid/care receiver,
                , so all their "family" Attendances will show up.
        :return:  Attendances of the logged in user and their kids/care receivers
        """
        # Todo 1. reorganize the view/api/js files to match urls that make sense
        #      2. extract current_user.belongs_to_organization_of ... to route guard
        #      3. check if the meets belongs to the organization
        current_user = self.request.user
        current_user_organization = current_user.organization
        attendee = current_user.attendee
        attendee_id = self.request.query_params.get('attendee')
        if attendee_id is not None and current_user.belongs_to_groups_of(current_user_organization.infos.get('data_admins')):
            other_user = Attendee.objects.filter(pk=attendee_id).first()
            if other_user is not None:
                attendee = other_user
        if current_user_organization:
            return AttendanceService.by_family_meets_gathering_intervals(
                attendee=attendee,
                current_user_organization=current_user_organization,
                meet_slugs=self.request.query_params.getlist('meets[]', []),
                gathering_start=self.request.query_params.get('start', None),
                gathering_finish=self.request.query_params.get('finish', None),
            )

        else:
            time.sleep(2)
            raise AuthenticationFailed(detail='Have you registered any events of the organization?')


api_family_organization_attendances_viewset = ApiFamilyOrganizationAttendancesViewSet
