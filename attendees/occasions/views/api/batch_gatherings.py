import time
from dateutil.relativedelta import relativedelta
import pytz
from urllib import parse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings
from django.db.models import F, Q

from rest_framework import viewsets
from rest_framework.exceptions import AuthenticationFailed, PermissionDenied
from rest_framework.response import Response

from attendees.occasions.serializers.batch_gatherings_serializer import BatchGatheringsSerializer
from attendees.occasions.services.gathering_service import GatheringService


class BatchGatheringsViewSet(LoginRequiredMixin, viewsets.ViewSet):
    """
    API endpoint that allows batch creation of gatherings.
    """
    serializer_class = BatchGatheringsSerializer  # Required for the Browsable API renderer to have a nice form.

    def create(self, request):
        # serializer = BatchGatheringsSerializer(request.data)
        tzname = request.COOKIES.get('timezone') or settings.CLIENT_DEFAULT_TIME_ZONE
        results = GatheringService.batch_create(
            **request.data,
            user_organization=request.user.organization,
            user_time_zone=pytz.timezone(parse.unquote(tzname)),
        )
        return Response(results)

    # def list(self, request):
    #     serializer = serializers.TaskSerializer(
    #         instance=tasks.values(), many=True)
    #     return Response(serializer.data)

    # def get_queryset(self):
    #     current_user_organization = self.request.user.organization
    #
    #     if current_user_organization:
    #         start = self.request.query_params.get('start')
    #         finish = self.request.query_params.get('finish')
    #
    #         extra_filter = Q(assembly__division__organization=current_user_organization)
    #
    #         if start:
    #             extra_filter.add((Q(finish__isnull=True) | Q(finish__gte=start)), Q.AND)
    #
    #         if finish:
    #             extra_filter.add((Q(start__isnull=True) | Q(start__lte=finish)), Q.AND)
    #
    #         return Meet.objects.filter(extra_filter).annotate(
    #             assembly_name=F('assembly__display_name'),
    #         ).order_by('assembly_name')
    #
    #     else:
    #         time.sleep(2)
    #         raise AuthenticationFailed(detail='Have you registered any events of the organization?')

    # def perform_create(self, serializer):
    #     if True:
    #         pass
    #     else:
    #         time.sleep(2)
    #         raise PermissionDenied(detail="Can't create attending across different organization")


batch_gatherings_viewset = BatchGatheringsViewSet
