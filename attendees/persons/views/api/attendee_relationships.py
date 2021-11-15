import time
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
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
        requester_permission = {'infos__show_secret__' + self.request.user.attendee_uuid_str(): True}

        if target_relationship_id:
            return Relationship.objects.filter(
                Q(pk=target_relationship_id),
                Q(to_attendee__division__organization=target_attendee.division.organization),
                Q(is_removed=False),
                (Q(infos__show_secret={})
                 |
                 Q(infos__show_secret__isnull=True)
                 |
                 Q(**requester_permission)),
            )
        else:
            return Relationship.objects.filter(
                Q(from_attendee=target_attendee),
                Q(to_attendee__division__organization=target_attendee.division.organization),
                Q(is_removed=False),
                (Q(infos__show_secret={})
                 |
                 Q(infos__show_secret__isnull=True)
                 |
                 Q(**requester_permission)),
            )

    def perform_create(self, serializer):  #SpyGuard ensured requester & target_attendee belongs to the same org.
        """
        Reason for special create:
        If manager A checked "secret shared with you" for a Relationship, manager B
        can't see it (expected) and creating the same relationship will fail due to uniq
        constrain (not expected). If relaxing uniq constraint, after manager B creating
        the very same relationship, manager A will see duplicated relationship. Instead we
        will add manager B id in secret shared with you of infos when manager B create it.
        """
        current_user_attendee_id = self.request.user.attendee_uuid_str()
        existing_relationship = Relationship.objects.filter(
            from_attendee=serializer.validated_data['from_attendee'],
            to_attendee=serializer.validated_data['to_attendee'],
            relation=serializer.validated_data['relation'],
            is_removed=False,
        ).first()
        if existing_relationship and existing_relationship.infos.get('show_secret'):  # current manager can't see existing record & try to create one, means existing record must be secret
            existing_relationship.infos['show_secret'][current_user_attendee_id] = True
            existing_relationship.infos['updated_by'][current_user_attendee_id] = Utility.now_with_timezone().isoformat()
            existing_relationship.save()  # manager's new data is intentionally discarded to show previous data
        else:
            serializer.validated_data['infos']['updated_by'] = {current_user_attendee_id: Utility.now_with_timezone().isoformat()}
            serializer.save()

    def perform_update(self, serializer):
        """
        Reason for special update:
        For a public relationship, if a manager add him/herself in secret shared with you of
        infos, all updater should be added too, or updater won't see it.

        if manager A&B both in secret shared with you of infos, either manager can make it public.
        """
        existing_relationship = get_object_or_404(Relationship, pk=self.kwargs.get('pk'))
        if 'show_secret' in serializer.validated_data.get('infos', {}):
            if serializer.validated_data['infos']['show_secret']:  # user is checking "secret shared with you"
                for updater_attendee_id in existing_relationship.infos.get('updated_by', {}):
                    serializer.validated_data['infos']['show_secret'][updater_attendee_id] = True
                    existing_relationship.infos['show_secret'][updater_attendee_id] = True
                for new_attendee_id in serializer.validated_data['infos']['show_secret']:
                    existing_relationship.infos['show_secret'][new_attendee_id] = True
            else:  # user is unchecking "secret shared with you", making it public
                existing_relationship.infos['show_secret'] = {}
        serializer.validated_data['infos'] = existing_relationship.infos
        serializer.validated_data['infos']['updated_by'][self.request.user.attendee_uuid_str()] = Utility.now_with_timezone().isoformat()
        serializer.save()

    def perform_destroy(self, instance):
        """
        Reason for special delete:
        When both managers are in secret shared with you of infos, when manager A deletes
        such records, it will only remove manager A from secret shared with you of infos.
        """
        current_user_attendee_id = self.request.user.attendee_uuid_str()
        instance.infos['updated_by'][current_user_attendee_id] = Utility.now_with_timezone().isoformat()
        if len(instance.infos.get('show_secret', {})) > 1:  # manager must able to see record before delete
            del instance.infos['show_secret'][current_user_attendee_id]
            instance.save()
        else:
            instance.save()
            instance.delete()


api_attendee_relationships_viewset = ApiAttendeeRelationshipsViewSet
