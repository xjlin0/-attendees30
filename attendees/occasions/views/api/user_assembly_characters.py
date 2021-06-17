import time

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed

from attendees.occasions.services import CharacterService
from attendees.occasions.serializers import CharacterSerializer


@method_decorator([login_required], name='dispatch')
class ApiUserAssemblyCharactersViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Character to be viewed or edited.
    """
    serializer_class = CharacterSerializer

    def get_queryset(self):
        current_user = self.request.user
        current_user_organization = current_user.organization
        #  Todo: this endpoint is used by datagrid_coworker_organization_attendances (no params) and datagrid_attendee_update_view page (with params). Do check if the editor and the editing target relations and permissions
        if current_user_organization:
            assemblies = self.request.query_params.getlist('assemblies[]', current_user.attendee.attendings.values_list('gathering__meet__assembly', flat=True))
            print("hi 25 here is assemblies: ")
            print(assemblies)
            return CharacterService.by_organization_assemblies(
                organization=current_user_organization,
                assemblies=assemblies,
            )

        else:
            time.sleep(2)
            raise AuthenticationFailed(detail='Have you registered any events of the organization?')


api_user_assembly_characters_viewset = ApiUserAssemblyCharactersViewSet
