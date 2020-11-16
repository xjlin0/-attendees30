import time

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed
from attendees.whereabouts.models import Division

from attendees.whereabouts.serializers import DivisionSerializer
from attendees.whereabouts.services import DivisionService


@method_decorator([login_required], name='dispatch')
class ApiUserDivisionViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows Division to be viewed or edited.
    """
    serializer_class = DivisionSerializer

    def get_queryset(self):
        if self.request.user.organization:
            return DivisionService.by_organization(self.request.user.organization.slug)

        else:
            time.sleep(2)
            raise AuthenticationFailed(detail='Have your account assigned an organization?')


api_user_division_viewset = ApiUserDivisionViewSet
