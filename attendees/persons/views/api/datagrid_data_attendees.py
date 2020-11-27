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
        current_user_organization = self.request.user.organization
        orderby_string = self.request.query_params.get('sort', '[{"selector":"id","desc":false}]')  # default order
        assembly_slug = self.request.query_params.get('assembly')
        filters_list_string = self.request.query_params.get('filter', '[]')
        filters_list = ast.literal_eval(filters_list_string)  # Datagrid didn't send array in standard url params

        return AttendeeService.by_datagrid_params(
            current_user_organization=current_user_organization,
            assembly_slug=assembly_slug,
            orderby_string=orderby_string,
            filters_list=filters_list,
        )


api_datagrid_data_attendees_viewset = ApiDatagridDataAttendeesViewSet