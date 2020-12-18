from django.contrib.postgres.aggregates.general import ArrayAgg

from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from attendees.persons.models import Attendee
from attendees.persons.services import AttendeeService
from attendees.persons.serializers import AttendeeMinimalSerializer


class ApiDatagridDataAttendeeViewSet(LoginRequiredMixin, ModelViewSet):  # from GenericAPIView
    """
    API endpoint that allows single attendee to be viewed or edited.
    """
    serializer_class = AttendeeMinimalSerializer
    # queryset = Attendee.objects.all()

    def retrieve(self, request, *args, **kwargs):
        attendee_id = self.request.query_params.get('attendee_id')
        print("entering retrieve ... ")
        attendee = Attendee.objects.annotate(
                    joined_meets=ArrayAgg('attendings__meets__slug', distinct=True),
                   ).filter(pk=attendee_id).first()
        # attendee = get_object_or_404(queryset)
        serializer = AttendeeMinimalSerializer(attendee)
        return Response(serializer.data)

    def get_queryset(self):
        """

        """
        current_user = self.request.user
        querying_attendee_id = self.kwargs.get('attendee_id')
        # return AttendeeService.single_record(
        #     current_user=current_user,
        #     attendee_id=querying_attendee_id,
        # )

        return Attendee.objects.annotate(
                    joined_meets=ArrayAgg('attendings__meets__slug', distinct=True),
               ).filter(pk=querying_attendee_id)


api_datagrid_data_attendee_viewset = ApiDatagridDataAttendeeViewSet
