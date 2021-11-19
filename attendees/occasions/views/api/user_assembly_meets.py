import time

from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed
from django.db.models import F
from attendees.occasions.models import Meet
from attendees.occasions.serializers.meet import MeetSerializer


class ApiUserAssemblyMeetsViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Meet to be viewed or edited.
    """
    serializer_class = MeetSerializer

    def get_queryset(self):
        current_user = self.request.user
        current_user_organization = current_user.organization
        #  Todo: this endpoint is used by datagrid_attendee_update_view page (with params). Do check if the editor and the editing target relations and permissions
        if current_user_organization:
            filters = {'assembly__division__organization': current_user_organization}
            assemblies = self.request.query_params.getlist('assemblies[]')
            if assemblies:
                filters['assembly__in'] = assemblies
            return Meet.objects.filter(**filters).annotate(
                assembly_name=F('assembly__display_name'),
            )

        else:
            time.sleep(2)
            raise AuthenticationFailed(detail='Have you registered any events of the organization?')


api_user_assembly_meets_viewset = ApiUserAssemblyMeetsViewSet
