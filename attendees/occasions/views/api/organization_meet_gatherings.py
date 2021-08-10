from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed
import time

from attendees.occasions.models import Gathering
from attendees.occasions.services import GatheringService
from attendees.occasions.serializers import GatheringSerializer


class ApiOrganizationMeetGatheringsViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Team to be viewed or edited.
    """

    serializer_class = GatheringSerializer

    def get_queryset(self):
        current_user_organization = self.request.user.organization
        print("hi ApiOrganizationMeetGatheringsViewSet 21 here is self.request.query_params: "); print(self.request.query_params)
        print("hi ApiOrganizationMeetGatheringsViewSet 22 here is self.kwargs: "); print(self.kwargs)
        if current_user_organization:
            pk = self.kwargs.get('pk')
            print("hi 25 here is pk: "); print(pk)
            if pk:
                gg = Gathering.objects.filter(
                    pk=pk,
                    meet__assembly__division__organization=current_user_organization,
                )
                print("hi 31 here is gg: "); print(gg)
                return gg

            else:
                # Todo: probably need to check if the meets belongs to the organization?
                return GatheringService.by_organization_meets(
                    organization_slug=current_user_organization.slug,
                    meet_slugs=self.request.query_params.getlist('meets[]', []),
                    start=self.request.query_params.get('start'),
                    finish=self.request.query_params.get('finish'),
                )

        else:
            time.sleep(2)
            raise AuthenticationFailed(detail='Have you registered any events of the organization?')


api_organization_meet_gatherings_viewset = ApiOrganizationMeetGatheringsViewSet
