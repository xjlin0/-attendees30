import time, logging

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response

from attendees.persons.models import Attending
from attendees.persons.renderers import ODataRenderer
from attendees.persons.services import AttendingService
from attendees.persons.serializers import AttendingSerializer

logger = logging.getLogger(__name__)


@method_decorator([login_required], name='dispatch')
class ApiODataAttendingsViewSet(viewsets.ModelViewSet):  # from GenericAPIView
    """
    API endpoint that allows Attending to be viewed or edited.
    """
    serializer_class = AttendingSerializer
    renderer_classes = [ODataRenderer]  # BrowsableAPIRenderer

    # def get_queryset(self):
    #     skip = self.request.query_params.get('skip', '0')
    #     take = self.request.query_params.get('take', '10')
    #     if True:
    #     # if self.request.user.belongs_to_divisions_of([self.kwargs['division_slug']]):
    #         # Todo: probably also need to check if the assembly belongs to the division
    #         # return AttendingService.by_assembly_meet_characters(
    #         #     assembly_slug=self.kwargs['assembly_slug'],
    #         #     meet_slugs=self.request.query_params.getlist('meets[]', []),
    #         #     character_slugs=self.request.query_params.getlist('characters[]', []),
    #         # )
    #         return Attending.objects.all().order_by("id")[int(skip):int(take)]
    #
    #     else:
    #         time.sleep(2)
    #         raise AuthenticationFailed(detail='Have you registered any events of the organization?')

    def list(self, request, *args, **kwargs):
        skip = request.query_params.get('skip', '0')
        take = request.query_params.get('take', '10')
        queryset = Attending.objects.all().order_by("id")[int(skip):int(take)+int(skip)]
        serializer = AttendingSerializer(queryset, many=True)
        return Response(serializer.data)


    # def list(self, request):
    #     if True:
    #         skip = request.query_params.get('skip', '0')
    #         take = request.query_params.get('take', '10')
    #         queryset = Attending.objects.all().order_by("id")[int(skip):int(take)]
    #         serializer = AttendingSerializer(queryset, many=True)
    #         return Response(serializer.data)
    #     else:
    #         time.sleep(2)
    #         raise AuthenticationFailed(detail='Have you registered any events of the organization?')


api_odata_attendings_viewset = ApiODataAttendingsViewSet
