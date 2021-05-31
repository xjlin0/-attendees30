import time
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.exceptions import PermissionDenied

from attendees.persons.models import Relationship, Attendee, Utility
from attendees.persons.serializers import RelationshipSerializer
from attendees.users.authorization.route_guard import SpyGuard
from attendees.users.models import MenuAuthGroup


class ApiAttendeeRelationshipsViewSet(LoginRequiredMixin, SpyGuard, viewsets.ModelViewSet):
    """
    API endpoint that allows Relation(Role) to be viewed or edited.
    """
    serializer_class = RelationshipSerializer

    def get_queryset(self):
        # Todo 20210523, check if current user allowed to see attendee's relationships, temporarily use SpyGuard for now
        menu_name = self.__class__.__name__
        url_name = Utility.underscore(menu_name)

        if not MenuAuthGroup.objects.filter(
                    menu__organization=self.request.user.organization,
                    menu__category='API',
                    menu__url_name=url_name
                ).exists():
            time.sleep(2)
            raise PermissionDenied(detail="Your user group doesn't have permissions for this")

        target_attendee = get_object_or_404(Attendee, pk=self.request.META.get('HTTP_X_TARGET_ATTENDEE_ID'))
        target_relationship_id = self.kwargs.get('pk')
        if target_relationship_id:
            return Relationship.objects.filter(
                pk=target_relationship_id,
                to_attendee__division__organization=target_attendee.division.organization,
            )
        else:
            return Relationship.objects.filter(
                from_attendee=target_attendee,
                to_attendee__division__organization=target_attendee.division.organization,
            )


api_attendee_relationships_viewset = ApiAttendeeRelationshipsViewSet
