import time
from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType
from django.http import Http404
from django.shortcuts import render
from django.views.generic import DetailView, UpdateView

from attendees.persons.models import Attendee, Family
from attendees.users.authorization import RouteAndSpyGuard
from attendees.utils.view_helpers import get_object_or_delayed_403


class DatagridAttendeeUpdateView(LoginRequiredMixin, RouteAndSpyGuard, UpdateView):
    model = Attendee
    fields = '__all__'
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
        targeting_attendee_id = self.kwargs.get('attendee_id', self.request.user.attendee_uuid_str())
        context.update({
            'attendee_contenttype_id': ContentType.objects.get_for_model(Attendee).id,
            'family_contenttype_id': ContentType.objects.get_for_model(Family).id,
            'empty_image_link': f"{settings.STATIC_URL}images/empty.png",
            'characters_endpoint': '/occasions/api/user_assembly_characters/',
            'meets_endpoint': '/occasions/api/user_assembly_meets/',
            'assemblies_endpoint': '/occasions/api/user_assemblies/',
            'divisions_endpoint': '/whereabouts/api/user_divisions/',
            'addresses_endpoint': '/whereabouts/api/all_addresses/',
            'states_endpoint': '/whereabouts/api/all_states/',
            'relations_endpoint': '/persons/api/all_relations/',
            'pasts_endpoint': '/persons/api/categorized_pasts/',
            'categories_endpoint': '/persons/api/all_categories/',
            'relationships_endpoint': '/persons/api/attendee_relationships/',
            'related_attendees_endpoint': '/persons/api/related_attendees/',  # may not be families
            'attendee_families_endpoint': f"/persons/api/attendee_families/",
            'attendings_endpoint': '/persons/api/attendee_attendings/',
            'family_attendees_endpoint': "/persons/api/datagrid_data_familyattendees/",
            'targeting_attendee_id': targeting_attendee_id,
            'current_organization_slug': current_organization_slug,
            'current_division_slug': current_division_slug,
            'current_assembly_slug': current_assembly_slug,
            'attendee_urn': f"/persons/{current_division_slug}/{current_assembly_slug}/datagrid_attendee_update_view/",
        })
        return context

    def render_to_response(self, context, **kwargs):
        # Todo: Double check if the editor's admin or editor and editing target are scheduling-allowed, because belongs_to_divisions_of() will wrongly let admin pass unconditionally
        if self.request.user.belongs_to_divisions_of([context['current_division_slug']]):  # should NOT use belongs_to_divisions_of() since it allows cross organization access !! i.e. admin (org1) can edit John(e8c025ec-9ea2-4d61-8df3-9daeecbfb849, org2)
            if self.request.is_ajax():
                pass

            else:
                context.update({'attendee_endpoint': "/persons/api/datagrid_data_attendee/"})
                return render(self.request, self.get_template_names()[0], context)
        else:
            time.sleep(2)
            raise Http404('Have you registered any events of the organization?')


datagrid_attendee_update_view = DatagridAttendeeUpdateView.as_view()

