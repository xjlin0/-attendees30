from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from attendees.persons.models import Relationship, Attendee
from attendees.persons.serializers import RelationshipSerializer
from attendees.users.authorization.route_guard import SpyGuard


class ApiAttendeeRelationshipsViewsSet(LoginRequiredMixin, SpyGuard, viewsets.ModelViewSet):
    """
    API endpoint that allows Relation(Role) to be viewed or edited.
    """
    serializer_class = RelationshipSerializer

    def get_queryset(self):
        # Todo 20210523, check if current user allowed to see attendee's relationships, temporarily use SpyGuard for now
        target_attendee = get_object_or_404(Attendee, pk=self.request.META.get('HTTP_X_TARGET_ATTENDEE_ID'))
        target_relationship_id = self.kwargs.get('pk')
        if target_relationship_id:
            return Relationship.objects.filter(pk=target_relationship_id)
        else:
            return Relationship.objects.filter(from_attendee=target_attendee)


api_attendee_relationships_viewset = ApiAttendeeRelationshipsViewsSet
