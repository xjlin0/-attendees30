from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator

from attendees.persons.forms import AttendeeForm, AttendeeFormSet
from attendees.persons.models import Attendee
from django.views.generic.edit import FormView
from django.db.models import Q
from django.http import Http404


# Todo: check attendee.user is current user or managers
@method_decorator([login_required], name='dispatch')
class AttendeesUpdateView(FormView):
    template_name = 'persons/attendees_update_view.html'
    form_class = AttendeeFormSet
    success_url = '/'

    def get_initial(self):
        """
        data admin can check all attendee. User can check other attendee if user is that attendee's scheduler
        :param queryset: attendee id may not be provided in the path params
        :return: user's attendee if no attendee id provided, or the requested attendee if by scheduler, or empty set.
        """
        current_user = self.request.user
        user_attendee = Attendee.objects.filter(user=current_user).first()

        if user_attendee:
            user_checking_id = self.kwargs.get('attendee_id', user_attendee.id)
            if current_user.privileged:
                return Attendee.objects.filter(
                    Q(id=user_checking_id)
                    |
                    Q(from_attendee__to_attendee__id=user_checking_id, from_attendee__scheduler=True)
                ).distinct().values()
            else:
                return Attendee.objects.filter(
                    Q(id=user_attendee.id)
                    |
                    Q(from_attendee__to_attendee__id=user_attendee.id, from_attendee__scheduler=True)
                ).distinct().values()

        else:
            raise Http404('Your profile does not have attendee')
#
#     # def get_success_url(self):
#     #     return reverse("persons:attendee_detail_view")
#


attendees_update_view = AttendeesUpdateView.as_view()
