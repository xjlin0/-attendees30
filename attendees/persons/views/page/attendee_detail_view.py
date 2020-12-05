from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView
from django.forms.models import inlineformset_factory
# ChildFormset = inlineformset_factory(
#     Parent, Child, fields=('name',)
# )
from attendees.persons.models import Attendee
from attendees.users.authorization import RouteGuard

# Todo: check attendee.user is current user or managers


@method_decorator([login_required], name='dispatch')
class AttendeeDetailView(RouteGuard, DetailView):
    model = Attendee
    template_name = 'persons/attendee_detail_view.html'
    context_object_name = 'attendee'

    def get_object(self, queryset=None):
        queryset = self.get_queryset() if queryset is None else queryset
        attendee_id = self.kwargs.get('attendee_id')
        if attendee_id:  # Todo: need to check if user allowed to see
            return get_object_or_404(queryset, id=attendee_id)
        else:
            return get_object_or_404(queryset, user=self.request.user)

    # def get_queryset(self):
    #     attendee_queryset = super(AttendeeDetailView, self).get_queryset()
    #     return attendee_queryset

    # def get_context_data(self, **kwargs):
        # we need to overwrite get_context_data to make sure that our formset is rendered
        # data = super().get_context_data(**kwargs)
        # if self.request.POST:
        #     pass  # data["children"] = ChildFormset(self.request.POST)
        # else:
        #     pass  # data["children"] = ChildFormset()
        # return data
        # pass


attendee_detail_view = AttendeeDetailView.as_view()


