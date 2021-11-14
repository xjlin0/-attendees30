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
                is_removed=False,
            )
        else:
            return Relationship.objects.filter(
                from_attendee=target_attendee,
                to_attendee__division__organization=target_attendee.division.organization,
                is_removed=False,
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
        print("hi 57 here is serializer.validated_data in perform_create()", serializer.validated_data)
        # from_attendee = serializer.validated_data['from_attendee']
        existing_relationship = Relationship.objects.filter(
            from_attendee=serializer.validated_data['from_attendee'],
            to_attendee=serializer.validated_data['to_attendee'],
            relation=serializer.validated_data['relation'],
            is_removed=False,
        ).first()
        # current manager can't see existing record & try to create one, means existing record is secret
        if existing_relationship and existing_relationship.infos.get('show_secret'):  # existing relationship must be secret
            print("67 updating existing record")
            existing_relationship.infos['show_secret'][current_user_attendee_id] = True
            existing_relationship.infos['updated_by'][current_user_attendee_id] = Utility.now_with_timezone()
            existing_relationship.save()  # manager's new data is intentionally discarded to show previous data
        else:
            print("72 updating new record")
            serializer.validated_data['infos']['updated_by'] = {current_user_attendee_id: Utility.now_with_timezone().isoformat()}
            serializer.save()

    def perform_update(self, serializer):
        """
        Reason for special update:
        For a public relationship, if a manager add him/herself in secret shared with you of
        infos, the original creator should be added too, or the original creator won't see it.
        """
        print("hi 82 here is serializer.validated_data in perform_update()", serializer.validated_data)
        print("hi 83 here is self.kwargs: ", self.kwargs)
        existing_relationship = get_object_or_404(Relationship, pk=self.kwargs['pk'])  # Relationship.objects.get(pk=self.kwargs['pk'])
        # Todo 20211114 need to test the case of unchecking the show_secret of a shared record, probably solved in browser end
        if serializer.validated_data.get('infos') and serializer.validated_data['infos'].get('show_secret') and not existing_relationship.infos.get('show_secret'):  # and not existing_relationship.infos['show_secret']:
            existing_relationship = get_object_or_404(Relationship, pk=self.kwargs.get('pk'))  # Relationship.objects.get(pk=self.kwargs['pk'])
            print("hi 88 converting a public record to secret here is serializer.validated_data: ", serializer.validated_data)
            for updater_attendee_id in existing_relationship.infos.get('updated_by', {}):
                serializer.validated_data['infos']['show_secret'][updater_attendee_id] = True
                existing_relationship.infos['show_secret'][updater_attendee_id] = True
            for new_attendee_id in serializer.validated_data['infos']['show_secret']:
                existing_relationship.infos['show_secret'][new_attendee_id] = True
        serializer.validated_data['infos'] = existing_relationship.infos
        serializer.validated_data['infos']['updated_by'][self.request.user.attendee_uuid_str()] = Utility.now_with_timezone().isoformat()
        print("hi 96 here is serializer.validated_data ENDING perform_update()", serializer.validated_data)
        serializer.save(**serializer.validated_data)

    def perform_destroy(self, instance):
        """
        Reason for special delete:
        When both managers are in secret shared with you of infos, when manager A deletes
        such records, it will only remove manager A from secret shared with you of infos.
        """
        print("hi 105 here is instance.__dict__ in perform_destroy()", instance.__dict__)
        current_user_attendee_id = self.request.user.attendee_uuid_str()
        instance.infos['updated_by'][current_user_attendee_id] = Utility.now_with_timezone().isoformat()
        if len(instance.infos.get('show_secret')) > 1:  # manager must able to see record before delete
            print("hi 109 removing show_secret since it's shared secret")
            del instance.infos['show_secret'][current_user_attendee_id]
            instance.save()
        else:
            print("hi 113 delete record since it's NOT shared secret")
            instance.save()
            instance.delete()


api_attendee_relationships_viewset = ApiAttendeeRelationshipsViewSet
