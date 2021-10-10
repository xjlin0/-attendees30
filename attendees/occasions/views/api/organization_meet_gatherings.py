from django.contrib.auth.mixins import LoginRequiredMixin

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

        if current_user_organization:
            pk = self.kwargs.get('pk')
            group_string = self.request.query_params.get('group')  # [{"selector":"meet","desc":false,"isExpanded":false}] if grouping
            orderby_string = self.request.query_params.get('sort', '[{"selector":"meet","desc":false},{"selector":"start","desc":false}]')  # order_by('meet','start')
            print("26 here is group_string: "); print(group_string)

            if pk:
                return Gathering.objects.filter(
                    pk=pk,
                    meet__assembly__division__organization=current_user_organization,
                )

            elif group_string:  # special case for server side grouping https://js.devexpress.com/Documentation/Guide/Data_Binding/Specify_a_Data_Source/Custom_Data_Sources/#Load_Data/Server-Side_Data_Processing
                print("35 here is special case for server side grouping")

            else:
                return GatheringService.by_organization_meets(
                    current_user=self.request.user,
                    meet_slugs=self.request.query_params.getlist('meets[]', []),
                    start=self.request.query_params.get('start'),
                    finish=self.request.query_params.get('finish'),
                    orderby_string=orderby_string,
                )

        else:
            time.sleep(2)
            raise AuthenticationFailed(detail='Have you registered any events of the organization?')


api_organization_meet_gatherings_viewset = ApiOrganizationMeetGatheringsViewSet
