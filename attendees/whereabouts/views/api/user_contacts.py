import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import AuthenticationFailed
from attendees.whereabouts.models import Place
from attendees.whereabouts.serializers import PlaceSerializer


class ApiUserContactViewSet(LoginRequiredMixin, ModelViewSet):
    """
    API endpoint that allows Place to be viewed or edited.
    """
    serializer_class = PlaceSerializer

    def get_queryset(self, **kwargs):
        if self.request.user.organization:
            # Todo: 20210502 filter contacts the current user can see (for schedulers)
            contact_id = self.request.query_params.get('id', None)
            keywords = self.request.query_params.get('searchValue', ''),
            keyword = ''.join(map(str, keywords))  # Todo: crazy params parsed as tuple, add JSON.stringify() on browser does not help
            contacts = Place.objects if self.request.user.privileged() else self.request.user.attendee.contacts

            if contact_id:
                return contacts.filter(pk=contact_id)
            else:
                return contacts.filter(
                    Q(street_number__icontains=keyword)
                    |
                    Q(display_name__icontains=keyword)
                    |
                    Q(route__icontains=keyword)
                    |
                    Q(raw__icontains=keyword)
                )

        else:
            time.sleep(2)
            raise AuthenticationFailed(detail='Have your account assigned an organization?')


api_user_contact_view_set = ApiUserContactViewSet
