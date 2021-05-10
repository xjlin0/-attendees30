from django.contrib.postgres.aggregates.general import JSONBAgg

from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Func, Value
from django.db.models.expressions import F

from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response

from attendees.whereabouts.models import Place
from attendees.whereabouts.serializers import PlaceSerializer


class ApiDatagridDataPlaceViewSet(LoginRequiredMixin, ModelViewSet):  # from GenericAPIView
    """
    API endpoint that allows Locate & Place to be viewed or edited.
    """
    serializer_class = PlaceSerializer

    def retrieve(self, request, *args, **kwargs):
        place_id = self.request.query_params.get('place_id')
        print("hi ApiDatagridDataPlaceViewSet 22 here is place_id")
        print(place_id)
        place = Place.objects.filter(pk=place_id).first()
        serializer = PlaceSerializer(place)
        return Response(serializer.data)

    def get_queryset(self):  # Todo: check if current user are allowed to query this attendee's contact
        querying_place_id = self.kwargs.get('place_id')
        print("hi ApiDatagridDataPlaceViewSet 30 here is querying_place_id")
        print(querying_place_id)
        return Place.objects.filter(pk=querying_place_id)


api_datagrid_data_place_viewset = ApiDatagridDataPlaceViewSet
