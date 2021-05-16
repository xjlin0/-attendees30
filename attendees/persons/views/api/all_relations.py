from django.contrib.auth.mixins import LoginRequiredMixin

from rest_framework import viewsets

from attendees.persons.models import Relation
from attendees.persons.serializers import RelationSerializer


class ApiAllRelationsViewsSet(LoginRequiredMixin, viewsets.ModelViewSet):
    """
    API endpoint that allows Relation(Role) to be viewed or edited.
    """
    serializer_class = RelationSerializer

    def get_queryset(self):
        return Relation.objects.all().order_by('display_order')


api_all_relations_viewset = ApiAllRelationsViewsSet
