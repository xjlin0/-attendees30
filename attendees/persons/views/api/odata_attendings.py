

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.utils import json
from rest_framework.viewsets import ModelViewSet

from attendees.persons.models import Attending
from attendees.persons.services import AttendingService
from attendees.persons.serializers import AttendingMinimalSerializer


@method_decorator([login_required], name='dispatch')
class ApiODataAttendingsViewSet(ModelViewSet):  # from GenericAPIView
    """
    API endpoint that allows Attending to be viewed or edited.
    """
    serializer_class = AttendingMinimalSerializer

    # Todo: probably also need to check if the assembly belongs to the division
    def get_queryset(self):
        """
        :return: queryset ordered by query params from DataGrid
        """
        orderby_string = self.request.query_params.get('sort', '[{"selector":"id","desc":false}]')  # default order
        orderby_list = []
        for orderby_dict in json.loads(orderby_string):
            direction = '-' if orderby_dict.get('desc', False) else ''
            field = orderby_dict.get('selector', 'id').replace('.', '__')  # convert attendee.division to attendee__division
            orderby_list.append(direction + field)
        return Attending.objects.order_by(*orderby_list)


api_odata_attendings_viewset = ApiODataAttendingsViewSet
