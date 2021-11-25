from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework import viewsets

from attendees.persons.models import Attendee, FolkAttendee
from attendees.persons.serializers import FolkAttendeeSerializer
from attendees.users.authorization.route_guard import SpyGuard


class ApiDatagridDataFolkAttendeesViewsSet(LoginRequiredMixin, SpyGuard, viewsets.ModelViewSet):
    """
    API endpoint that allows FamiliesAttendees of a single Attendee in headers to be viewed or edited.
    For example, if Alice, Bob & Charlie are in a family, passing Alice's attendee id in headers (key:
    X-TARGET-ATTENDEE-ID) will return all 3 FamilyAttendee objects of Alice, Bob & Charlie. Also,
    attaching Bob's FamilyAttendee id at the end of the endpoint will return Bob's FamilyAttendee only.

    Note: If Dick is not in the family, passing Dick's attendee id in headers plus Bob's FamilyAttendee
    id at the end of the endpoint will return nothing.
    """
    serializer_class = FolkAttendeeSerializer

    def get_queryset(self):
        target_attendee = get_object_or_404(Attendee, pk=self.request.META.get('HTTP_X_TARGET_ATTENDEE_ID'))
        target_folkattendee_id = self.kwargs.get('pk')
        category = self.request.query_params.get('category', Attendee.FAMILY_CATEGORY)
        target_attendee_folkattendees = FolkAttendee.objects.filter(
            folk__in=target_attendee.folks.filter(folkattendee__is_removed=False),
            folk__category=category,
        ).order_by(  # Todo: 20210516 order by attendee's family attendee display_order, such as order_by annotate()
            '-folk__created', 'role__display_order',
        )  # Todo: 20210515 add filter by start/finish for end users but not data-admins

        if target_folkattendee_id:
            return target_attendee_folkattendees.filter(pk=target_folkattendee_id)
        else:
            return target_attendee_folkattendees



    # def update(self, request, *args, **kwargs):  # from UpdateModelMixin
    #     print("hi 27 here is request: ")
    #     print(request)
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #
    #     if getattr(instance, '_prefetched_objects_cache', None):
    #         # If 'prefetch_related' has been applied to a queryset, we need to
    #         # refresh the instance from the database.
    #         instance = self.get_object()
    #         serializer = self.get_serializer(instance)
    #
    #     return Response(serializer.data)
    #
    # def perform_update(self, serializer):  # from UpdateModelMixin
    #     serializer.save()
    #
    # def partial_update(self, request, *args, **kwargs):  # from UpdateModelMixin
    #     print("hi 47 here is request: ")
    #     print(request)
    #     kwargs['partial'] = True
    #     return self.update(request, *args, **kwargs)


api_datagrid_data_folkattendees_viewset = ApiDatagridDataFolkAttendeesViewsSet
