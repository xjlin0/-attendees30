from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.generic.edit import FormView

from attendees.persons.forms import AttendeesFormSet
from attendees.persons.services import AttendeeService


@method_decorator([login_required], name='dispatch')
class AttendeesUpdateView(FormView):
    template_name = 'persons/attendees_update_view.html'
    form_class = AttendeesFormSet
    success_url = '/'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        print("hi jack 24 here is self.request.user: ")
        print(self.request.user)
        print("hi jack 26 here is self.kwargs: ")
        print(self.kwargs)

        data['formset'] = AttendeesFormSet(
            queryset=AttendeeService.get_related_ones_by_permission(self.request.user, self.kwargs.get('attendee_id'))
        )
        return data

#
#     # def get_success_url(self):
#     #     return reverse("persons:attendee_detail_view")
#


attendees_update_view = AttendeesUpdateView.as_view()
