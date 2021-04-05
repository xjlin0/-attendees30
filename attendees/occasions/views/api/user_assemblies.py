import time

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed

from attendees.occasions.models import Assembly
from attendees.occasions.serializers.assembly_serializer import AssemblySerializer


@method_decorator([login_required], name='dispatch')
class ApiUserAssemblyViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Division to be viewed or edited.
    """
    serializer_class = AssemblySerializer

    def get_queryset(self):
        if self.request.user.organization:
            division = self.request.query_params.get('division', None),
            assembly_objects = Assembly.objects.filter(division=division) if division else Assembly.objects

            return assembly_objects.filter(
                division__organization=self.request.user.organization,
            )

        else:
            time.sleep(2)
            raise AuthenticationFailed(detail='Have your account assigned an organization?')


api_user_assembly_viewset = ApiUserAssemblyViewSet
