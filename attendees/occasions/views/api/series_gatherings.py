import pytz

from urllib import parse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.conf import settings

from rest_framework import viewsets
from rest_framework.response import Response

from attendees.occasions.serializers.batch_gatherings_serializer import BatchGatheringsSerializer
from attendees.occasions.services.gathering_service import GatheringService
from attendees.users.authorization import RouteGuard


class SeriesGatheringsViewSet(LoginRequiredMixin, RouteGuard, viewsets.ViewSet):
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


series_gatherings_viewset = SeriesGatheringsViewSet
