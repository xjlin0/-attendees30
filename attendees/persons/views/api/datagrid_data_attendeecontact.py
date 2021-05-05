from django.contrib.postgres.aggregates.general import JSONBAgg

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Func, Value
from django.db.models.expressions import F

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from attendees.whereabouts.models import Locate
from attendees.persons.serializers import AttendeeContactSerializer


class ApiDatagridDataAttendeeContactViewSet(LoginRequiredMixin, ModelViewSet):  # from GenericAPIView
    """
    API endpoint that allows Locate & Place to be viewed or edited.
    """
    serializer_class = AttendeeContactSerializer

    def retrieve(self, request, *args, **kwargs):
        attendeecontact_id = self.request.query_params.get('attendeecontact_id')
        attendee = Locate.objects.filter(pk=attendeecontact_id).first()
        serializer = AttendeeContactSerializer(attendee)
        return Response(serializer.data)

    def get_queryset(self):  # Todo: check if current user are allowed to query this attendee's contact
        querying_attendeecontact_id = self.kwargs.get('attendeecontact_id')
        return Locate.objects.filter(pk=querying_attendeecontact_id)


api_datagrid_data_attendeecontact_viewset = ApiDatagridDataAttendeeContactViewSet
