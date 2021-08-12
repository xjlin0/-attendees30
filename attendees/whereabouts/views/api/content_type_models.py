import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed

from attendees.whereabouts.serializers import ContentTypeSerializer


class ApiContentTypeModelsViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows ContentType to be viewed, need search params of 'query' to filter the models.
    """
    serializer_class = ContentTypeSerializer
    basic_locations = ['organization', 'division', 'campus', 'property', 'room', 'suite']

    def get_queryset(self):
        if self.request.user.organization:
            locations = self.basic_locations + ['place'] if self.request.user.can_see_all_organizational_meets_attendees else self.basic_locations
            content_type_id = self.kwargs.get('pk')
            query = self.request.query_params.get('query')
            if query == 'locations':
                if content_type_id:
                    return ContentType.objects.filter(pk=content_type_id, model__in=locations)
                else:
                    return ContentType.objects.filter(model__in=locations)
            else:
                return ContentType.objects.none()

        else:
            time.sleep(2)
            raise AuthenticationFailed(detail='Have your account assigned an organization?')


content_type_models_viewset = ApiContentTypeModelsViewSet
