from django.contrib.auth.mixins import LoginRequiredMixin
from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed
import time
from attendees.occasions.services import GatheringService
from attendees.occasions.serializers import GatheringSerializer


class ApiOrganizationMeetGatheringsViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Team to be viewed or edited.
    """

    serializer_class = GatheringSerializer

    def get_queryset(self):
        current_user_organization = self.request.user.organization
        if current_user_organization:
            # Todo: probably need to check if the meets belongs to the organization?
            return GatheringService.by_organization_meets(
                organization_slug=current_user_organization.slug,
                meet_slugs=self.request.query_params.getlist('meets[]', []),
            )

        else:
            time.sleep(2)
            raise AuthenticationFailed(detail='Have you registered any events of the organization?')


api_organization_meet_gatherings_viewset = ApiOrganizationMeetGatheringsViewSet
