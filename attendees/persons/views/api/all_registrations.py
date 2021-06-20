from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import viewsets

from attendees.persons.models import Registration, Utility
from attendees.persons.serializers import RegistrationSerializer


class ApiAllRegistrationsViewsSet(LoginRequiredMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Registration to be viewed or edited by pk or by single assembly and main_attendee.
    Todo 20210619: need permission check beforehand
    """
    serializer_class = RegistrationSerializer

    def get_queryset(self):
        registration_id = self.kwargs.get('pk')

        if registration_id:
            return Registration.objects.filter(pk=registration_id)
        else:
            filters = {
                'assembly': Utility.presence(self.request.query_params.get('assembly')),
                'main_attendee': Utility.presence(self.request.query_params.get('main_attendee')),
            }  # None is a valid value since it's null=True
            return Registration.objects.filter(**filters)


api_all_registrations_viewset = ApiAllRegistrationsViewsSet
