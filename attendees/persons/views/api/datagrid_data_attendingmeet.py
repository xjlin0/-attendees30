from django.contrib.postgres.aggregates.general import JSONBAgg

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Func, Value
from django.db.models.expressions import F
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from attendees.persons.models import AttendingMeet
from attendees.persons.serializers import AttendingMeetEtcSerializer


class ApiDatagridDataAttendingMeetViewSet(LoginRequiredMixin, ModelViewSet):  # from GenericAPIView
    """
    API endpoint that allows AttendingMeet & Meet to be viewed or edited.
    """
    serializer_class = AttendingMeetEtcSerializer
    # queryset = AttendingMeet.objects.annotate(assembly=F('meet__assembly'))

    # def retrieve(self, request, *args, **kwargs):
    #     attendingmeet_id = self.request.query_params.get('attendingmeet_id')
    #     print("entering retrieve 24 here is query_params:")
    #     print(self.request.query_params)
    #     attendee = AttendingMeet.objects.annotate(
    #         joined_meets=JSONBAgg(
    #             Func(
    #                 Value('slug'), 'attendings__meets__slug',
    #                 Value('display_name'), 'attendings__meets__display_name',
    #                 function='jsonb_build_object'
    #             ),
    #         )
    #                ).filter(pk=attendingmeet_id).first()
    #     serializer = AttendingMeetEtcSerializer(attendee)
    #     return Response(serializer.data)








    def get_queryset(self):
        """

        """

        querying_attendingmeet_id = self.kwargs.get('attendingmeet_id')
        print("entering get_queryset 51 here is self.kwargs:")
        print(self.kwargs)
        print("in get_queryset 53 here is self.request.POST:")
        print(self.request.POST)
        return AttendingMeet.objects.annotate(
                    assembly=F('meet__assembly'),
                ).filter(pk=querying_attendingmeet_id)


api_datagrid_data_attendingmeet_viewset = ApiDatagridDataAttendingMeetViewSet
