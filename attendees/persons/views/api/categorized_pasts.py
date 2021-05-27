from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from attendees.persons.models import Attendee
from attendees.persons.serializers import PastSerializer
from attendees.users.authorization.route_guard import SpyGuard


class ApiCategorizedPastsViewsSet(LoginRequiredMixin, SpyGuard, viewsets.ModelViewSet):
    """
    API endpoint that allows Past(history/experience) to be viewed or edited.
    """
    serializer_class = PastSerializer

    def get_queryset(self):
        target_attendee = get_object_or_404(Attendee, pk=self.request.META.get('HTTP_X_TARGET_ATTENDEE_ID'))
        past_id = self.kwargs.get('pk')
        category__type = self.request.query_params.get('category__type')

        if past_id:
            return target_attendee.pasts.filter(pk=past_id, category__type=category__type)
        else:
            return target_attendee.pasts.filter(category__type=category__type)


api_categorized_pasts_viewset = ApiCategorizedPastsViewsSet
