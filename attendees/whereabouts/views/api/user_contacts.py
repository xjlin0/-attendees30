import time

from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import AuthenticationFailed
from attendees.whereabouts.models import Contact
from attendees.whereabouts.serializers import ContactSerializer


class ApiUserContactViewSet(LoginRequiredMixin, ModelViewSet):
    """
    API endpoint that allows Contact to be viewed or edited.
    """
    serializer_class = ContactSerializer

    def get_queryset(self):
        if self.request.user.organization:
            if self.request.user.privileged:
                return Contact.objects.all()
            else:  # Todo: 20210502 filter contacts the current user can see (for schedulers)
                return self.request.user.attendee.contacts.all()

        else:
            time.sleep(2)
            raise AuthenticationFailed(detail='Have your account assigned an organization?')


api_user_contact_view_set = ApiUserContactViewSet
