import ast

from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from rest_framework.viewsets import ModelViewSet

from attendees.persons.services import AttendeeService
from attendees.persons.serializers import AttendeeMinimalSerializer


@method_decorator([login_required], name='dispatch')
class ApiDatagridDataAttendeesViewSet(ModelViewSet):  # from GenericAPIView
    """
    API endpoint that allows Attending to be viewed or edited.
    """
    serializer_class = AttendeeMinimalSerializer

    # Todo: probably also need to check if the assembly belongs to the division
    def get_queryset(self):
        """
        still need to work with filter and grouping and move to service layer
        filter = '["attendee","contains","Lydia"]', 'filter: ["attendee.division","=",2]' or '[["id","=",3],"and",["attendee","contains","John"]]'
        group =  '[{"selector":"attendee.division","desc":false,"isExpanded":false}]'
        :return: queryset ordered by query params from DataGrid
        """
        orderby_string = self.request.query_params.get('sort', '[{"selector":"id","desc":false}]')  # default order
        assemblies_string = self.request.query_params.get('assemblies', '[]')
        filters_list_string = self.request.query_params.get('filter', '[]')

        return AttendeeService.by_datagrid_params(
            current_user=self.request.user,
            assemblies=ast.literal_eval(assemblies_string),
            orderby_string=orderby_string,
            filters_list=ast.literal_eval(filters_list_string),
        )  # Datagrid can't send array in standard url params since filters can be dynamic nested arrays


api_datagrid_data_attendees_viewset = ApiDatagridDataAttendeesViewSet
