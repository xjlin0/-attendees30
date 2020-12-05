from django.contrib.auth.decorators import login_required
from django.http import Http404

from django.db.models import Q
from django.utils.decorators import method_decorator
from django.views.generic.detail import DetailView
from django.core.exceptions import ObjectDoesNotExist
from django.views.generic.edit import CreateView, UpdateView
from django.forms.models import inlineformset_factory
# ChildFormset = inlineformset_factory(
#     Parent, Child, fields=('name',)
# )
from attendees.utils.view_helpers import get_object_or_delayed_403
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
        return get_object_or_delayed_403(queryset)

    def get_queryset(self):
        """
        data admin can check all attendee. User can check other attendee if user is that attendee's scheduler
        :param queryset: attendee id may not be provided in the path params
        :return: user's attendee if no attendee id provided, or the requested attendee if by scheduler, or empty set.
        """
        attendee_queryset = super(AttendeeDetailView, self).get_queryset()

        try:
            user_attendee = self.request.user.attendee
            is_data_admin = self.request.user.belongs_to_groups_of(self.request.user.organization.infos.get('data_admins'))
            user_allowed_qs = attendee_queryset if is_data_admin else attendee_queryset.filter(
                Q(from_attendee__to_attendee__id=user_attendee.id, from_attendee__scheduler=True)
                |
                Q(id=user_attendee.id)
            ).distinct()
            user_checking_id = self.kwargs.get('attendee_id', user_attendee.id)
            return user_allowed_qs.filter(id=user_checking_id)

        except ObjectDoesNotExist:
            raise Http404('Your profile does not have attendee')


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


