from django.contrib.postgres.aggregates.general import JSONBAgg

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Func, Value
from django.db.models.expressions import F

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from attendees.persons.models import AttendeeContact
from attendees.persons.serializers import AttendeeContactSerializer


class ApiDatagridDataAttendeeContactViewSet(LoginRequiredMixin, ModelViewSet):  # from GenericAPIView
    """
    API endpoint that allows AttendeeContact & Contact to be viewed or edited.
    """
    serializer_class = AttendeeContactSerializer

    def retrieve(self, request, *args, **kwargs):
        attendeecontact_id = self.request.query_params.get('attendeecontact_id')
        print("hi 22 here is attendeecontact_id: ")
        print(attendeecontact_id)
        attendee = AttendeeContact.objects.filter(pk=attendeecontact_id).first()
        serializer = AttendeeContactSerializer(attendee)
        return Response(serializer.data)

    def get_queryset(self):
        querying_attendeecontact_id = self.kwargs.get('attendeecontact_id')
        print("hi 30 here is querying_attendeecontact_id: ")
        print(querying_attendeecontact_id)
        return AttendeeContact.objects.filter(pk=querying_attendeecontact_id)


api_datagrid_data_attendeecontact_viewset = ApiDatagridDataAttendeeContactViewSet
