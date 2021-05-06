from django.contrib.postgres.aggregates.general import JSONBAgg

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Func, Value
from django.db.models.expressions import F

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from attendees.whereabouts.models import Locate
from attendees.persons.serializers import LocateSerializer


class ApiDatagridDataLocateViewSet(LoginRequiredMixin, ModelViewSet):  # from GenericAPIView
    """
    API endpoint that allows Locate & Place to be viewed or edited.
    """
    serializer_class = LocateSerializer

    def retrieve(self, request, *args, **kwargs):
        locate_id = self.request.query_params.get('locate_id')
        locate = Locate.objects.filter(pk=locate_id).first()
        serializer = LocateSerializer(locate)
        return Response(serializer.data)

    def get_queryset(self):  # Todo: check if current user are allowed to query this attendee's contact
        querying_locate_id = self.kwargs.get('locate_id')
        return Locate.objects.filter(pk=querying_locate_id)


api_datagrid_data_locate_viewset = ApiDatagridDataLocateViewSet
