import time

from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import Http404
from django.shortcuts import render
from django.views.generic import DetailView

from attendees.persons.models import Attendee
from attendees.users.authorization import RouteGuard
from attendees.utils.view_helpers import get_object_or_delayed_403


class DatagridAttendeeUpdateView(LoginRequiredMixin, RouteGuard, DetailView):
    model = Attendee
    template_name = 'persons/datagrid_attendee_update_view.html'

    def get_object(self, queryset=None):
        # queryset = self.get_queryset() if queryset is None else queryset
        if queryset:
            return get_object_or_delayed_403(queryset)
        else:
            return None

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_division_slug = self.kwargs.get('division_slug', None)
        current_organization_slug = self.kwargs.get('organization_slug', None)
        current_assembly_slug = self.kwargs.get('assembly_slug', None)
        current_attendee_id = self.kwargs.get('attendee_id', self.request.user.attendee_uuid_str)
        context.update({
            'characters_endpoint': '/occasions/api/user_assembly_characters/',
            'assemblies_endpoint': '/occasions/api/user_assemblies/',
            'targeting_attendee_id': current_attendee_id,
            'current_organization_slug': current_organization_slug,
            'current_division_slug': current_division_slug,
            'current_assembly_slug': current_assembly_slug,
        })
        return context

    def render_to_response(self, context, **kwargs):
        # Todo: Double check if the editor's admin or editor and editing target are scheduling-allowed, because belongs_to_divisions_of() will wrongly let admin pass unconditionally
        if self.request.user.belongs_to_divisions_of([context['current_division_slug']]):  # should NOT use belongs_to_divisions_of() since it allows cross organization access !!
            if self.request.is_ajax():
                pass

            else:
                context.update({'attendee_endpoint': "/persons/api/datagrid_data_attendee/"})
                return render(self.request, self.get_template_names()[0], context)
        else:
            time.sleep(2)
            raise Http404('Have you registered any events of the organization?')


datagrid_attendee_update_view = DatagridAttendeeUpdateView.as_view()

