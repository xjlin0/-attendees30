from django.views.generic.list import ListView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from json import dumps
from django.shortcuts import render
from django.db.models import F, Q
from attendees.occasions.models import Meet
from attendees.persons.models import Utility
from attendees.users.authorization import RouteGuard
import logging

# from attendees.users.models import Menu

logger = logging.getLogger(__name__)


@method_decorator([login_required], name='dispatch')
class GatheringsListView(RouteGuard, ListView):
    queryset = []
    template_name = 'occasions/gatherings_list_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # family_attendances_menu = Menu.objects.filter(url_name='datagrid_user_organization_attendances').first()
        available_meets = Meet.objects.filter(
            (Q(finish__isnull=True) | Q(finish__gt=Utility.now_with_timezone())),
            assembly__division__organization=self.request.user.organization,
        ).annotate(
            assembly_name=F('assembly__display_name'),
        ).order_by('assembly_name').values('id', 'slug', 'display_name', 'assembly_name')  # Todo 20210711 only coworkers can see all Meet, general users should only see what they attended
        # allowed_to_create_attendee = Menu.user_can_create_attendee(self.request.user)
        context.update({
            'available_meets_json': dumps(list(available_meets)),
            # 'allowed_to_create_attendee': allowed_to_create_attendee,
        })
        return context

    def render_to_response(self, context, **kwargs):
        if self.request.is_ajax():
            pass

        else:
            return render(self.request, self.get_template_names()[0], context)


gatherings_list_view = GatheringsListView.as_view()
