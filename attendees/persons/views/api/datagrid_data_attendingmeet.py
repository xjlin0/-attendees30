from django.contrib.postgres.aggregates.general import JSONBAgg

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Func, Value
from django.db.models.expressions import F
from django.shortcuts import get_object_or_404

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from attendees.persons.models import AttendingMeet
from attendees.persons.serializers import AttendingMeetSerializer


class ApiDatagridDataAttendingMeetViewSet(LoginRequiredMixin, ModelViewSet):  # from GenericAPIView
    """
    API endpoint that allows single attendee to be viewed or edited.
    """
    serializer_class = AttendingMeetSerializer
    # queryset = AttendingMeet.objects.all()

    def retrieve(self, request, *args, **kwargs):
        attendingmeet_id = self.request.query_params.get('attendingmeet_id')
        print("entering retrieve ... ")
        attendee = AttendingMeet.objects.annotate(
            joined_meets=JSONBAgg(
                Func(
                    Value('slug'), 'attendings__meets__slug',
                    Value('display_name'), 'attendings__meets__display_name',
                    function='jsonb_build_object'
                ),
            )
                    # joined_meets=ArrayAgg('attendings__meets__slug', distinct=True),
                   ).filter(pk=attendingmeet_id).first()
        # attendee = get_object_or_404(queryset)
        serializer = AttendingMeetSerializer(attendee)
        return Response(serializer.data)

    def get_queryset(self):
        """

        """
        current_user = self.request.user
        querying_attendingmeet_id = self.kwargs.get('attendingmeet_id')
        # return AttendeeService.single_record(
        #     current_user=current_user,
        #     attendee_id=querying_attendee_id,
        # )
        return AttendingMeet.objects.annotate(
                    division_name=F('meet__assembly__division__display_name'),
                    division=F('meet__assembly__division__id'),
                    assembly_name=F('meet__assembly__display_name'),
                    assembly=F('meet__assembly__id'),
                    character_name=F('character__display_name'),
                ).filter(pk=querying_attendingmeet_id)
        # return Attendee.objects.annotate(
        #             joined_meets=JSONBAgg(
        #                 Func(
        #                     Value('attendingmeet_id'), 'attendings__attendingmeet__id',
        #                     Value('attending_finish'), 'attendings__attendingmeet__finish',
        #                     Value('attending_start'), 'attendings__attendingmeet__start',
        #                     Value('meet_name'), 'attendings__meets__display_name',
        #                     function='jsonb_build_object'
        #                 ),
        #             )
        #             # joined_meets=ArrayAgg('attendings__meets__slug', distinct=True),
        #        ).filter(pk=querying_attendingmeet_id)


api_datagrid_data_attendingmeet_viewset = ApiDatagridDataAttendingMeetViewSet
