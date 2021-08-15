import time
from dateutil.relativedelta import relativedelta
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import F, Q

from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed

from attendees.occasions.models import Meet
from attendees.occasions.serializers.meet import MeetSerializer
from attendees.persons.models import Utility


class OrganizationMeetsViewSet(LoginRequiredMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows all Meet in current user's organization filtered by date to be viewed or edited.
    Todo 20210711 only coworkers/organizers can see all Meets, general users should only see what they attended
    Todo 20210815 if limiting by meet's shown_audience, non-coworker assigned to non-public meets won't show
    """
    serializer_class = MeetSerializer

    def get_queryset(self):
        current_user_organization = self.request.user.organization

        if current_user_organization:
            start = self.request.query_params.get('start')
            finish = self.request.query_params.get('finish')

            extra_filter = Q(assembly__division__organization=current_user_organization)

            if start:
                extra_filter.add((Q(finish__isnull=True) | Q(finish__gte=start)), Q.AND)

            if finish:
                extra_filter.add((Q(start__isnull=True) | Q(start__lte=finish)), Q.AND)

            return Meet.objects.filter(extra_filter).annotate(
                assembly_name=F('assembly__display_name'),
            ).order_by('assembly_name')

        else:
            time.sleep(2)
            raise AuthenticationFailed(detail='Have you registered any events of the organization?')


organization_meets_viewset = OrganizationMeetsViewSet
