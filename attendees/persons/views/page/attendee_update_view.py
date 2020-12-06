from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.http import Http404
from django.urls import reverse

from django.utils.decorators import method_decorator
from django.views.generic.edit import UpdateView
from django.forms.models import inlineformset_factory
# ChildFormset = inlineformset_factory(
#     Parent, Child, fields=('name',)
# )
from attendees.persons.forms import AttendeeForm
from attendees.persons.models import Attendee
from attendees.users.authorization import RouteGuard

# Todo: check attendee.user is current user or managers
from attendees.utils.view_helpers import get_object_or_delayed_403


@method_decorator([login_required], name='dispatch')
class AttendeeUpdateView(RouteGuard, UpdateView):

    model = Attendee
    # context_object_name = 'attendee'
    form_class = AttendeeForm
    template_name = 'persons/attendee_update_view.html'

    # def get_context_data(self, **kwargs):
    #     context = super(AttendeesUpdateView, self).get_context_data(**kwargs)
    #     return context

    def get_object(self, queryset=None):
        queryset = self.get_queryset() if queryset is None else queryset
        return get_object_or_delayed_403(queryset)

    def get_queryset(self):
        """
        data admin can check all attendee. User can check other attendee if user is that attendee's scheduler
        :param queryset: attendee id may not be provided in the path params
        :return: user's attendee if no attendee id provided, or the requested attendee if by scheduler, or empty set.
        """
        attendee_queryset = super(AttendeeUpdateView, self).get_queryset()
        current_user = self.request.user
        user_attendee = Attendee.objects.filter(user=current_user).first()

        if user_attendee:
            user_allowed_qs = attendee_queryset if current_user.privileged else attendee_queryset.filter(
                Q(from_attendee__to_attendee__id=user_attendee.id, from_attendee__scheduler=True)
                |
                Q(id=user_attendee.id)
            ).distinct()
            user_checking_id = self.kwargs.get('attendee_id', user_attendee.id)
            return user_allowed_qs.filter(id=user_checking_id)

        else:
            raise Http404('Your profile does not have attendee')

    def get_success_url(self):
        return reverse("persons:attendee_detail_view")


attendee_update_view = AttendeeUpdateView.as_view()
