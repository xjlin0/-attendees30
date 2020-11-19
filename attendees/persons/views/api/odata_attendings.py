from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework.viewsets import ModelViewSet

from attendees.persons.models import Attending
from attendees.persons.services import AttendingService
from attendees.persons.serializers import AttendingSerializer


@method_decorator([login_required], name='dispatch')
class ApiODataAttendingsViewSet(ModelViewSet):  # from GenericAPIView
    """
    API endpoint that allows Attending to be viewed or edited.
    """
    serializer_class = AttendingSerializer
    queryset = Attending.objects.all().order_by('id')
    # Todo: probably also need to check if the assembly belongs to the division


api_odata_attendings_viewset = ApiODataAttendingsViewSet
