import time

from address.models import Address
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from rest_framework.viewsets import ModelViewSet
from rest_framework.exceptions import AuthenticationFailed

from attendees.whereabouts.serializers import AddressSerializer


class ApiAllAddressViewSet(LoginRequiredMixin, ModelViewSet):
    """
    API endpoint that allows Place to be viewed or edited.
    """
    serializer_class = AddressSerializer

    def get_queryset(self, **kwargs):
        if self.request.user.organization:
            address_id = self.request.query_params.get('id', None)
            keywords = self.request.query_params.get('searchValue', ''),
            keyword = ''.join(map(str, keywords))  # Todo: crazy params parsed as tuple, add JSON.stringify() on browser does not help
            print("hi ApiAllAddressViewSet 23 here is address_id:")
            print(address_id)
            print("hi ApiAllAddressViewSet 25 here is keywords:")
            print(keywords)
            print("hi ApiAllAddressViewSet 27 here is keyword:")
            print(keyword)

            if address_id:
                return Address.objects.filter(pk=address_id)
            else:
                return Address.objects.filter(
                    Q(street_number__icontains=keyword)
                    |
                    Q(route__icontains=keyword)
                    |
                    Q(raw__icontains=keyword)
                )

        else:
            time.sleep(2)
            raise AuthenticationFailed(detail='Have your account assigned an organization?')


api_all_address_view_set = ApiAllAddressViewSet
