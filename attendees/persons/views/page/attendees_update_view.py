from attendees.persons.forms import AttendeeForm
from attendees.persons.models import Attendee
from django.views.generic.edit import FormView
from django.db.models import Q
from django.http import Http404


class AttendeesUpdateView(FormView):
    template_name = 'persons/attendees_update_view.html'
    form_class = AttendeeForm
    success_url = '/'






# from django.contrib.auth.decorators import login_required

# from django.urls import reverse
#
# from django.utils.decorators import method_decorator
# from django.views.generic.edit import UpdateView, FormView
# from django.forms.models import inlineformset_factory
# # ChildFormset = inlineformset_factory(
# #     Parent, Child, fields=('name',)
# # )
#
# from attendees.persons.forms import AttendeesFormSet

# from attendees.users.authorization import RouteGuard
#
# # Todo: check attendee.user is current user or managers
# from attendees.utils.view_helpers import get_object_or_delayed_403
#
#
# @method_decorator([login_required], name='dispatch')
# class AttendeesUpdateView(RouteGuard, FormView):
#     success_url = '/'
#     model = Attendee
#     # context_object_name = 'attendee'
#     form_class = AttendeesFormSet
#     template_name = 'persons/attendees_update_view.html'
#
#     # def get_context_data(self, **kwargs):
#     #     context = super(AttendeesUpdateView, self).get_context_data(**kwargs)
#     #     return context
    def get_form_kwargs(self):
        form_kwargs = super(AttendeesUpdateView, self).get_form_kwargs()
        form_kwargs['instance'] = self.get_queryset()
        return form_kwargs

    def get_queryset(self):
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
                ).distinct().filter(id=user_checking_id).first()
            else:
                return Attendee.objects.filter(
                    Q(id=user_attendee.id)
                    |
                    Q(from_attendee__to_attendee__id=user_attendee.id, from_attendee__scheduler=True)
                ).distinct().filter(id=user_checking_id).first()

        else:
            raise Http404('Your profile does not have attendee')
#
#     # def get_success_url(self):
#     #     return reverse("persons:attendee_detail_view")
#


attendees_update_view = AttendeesUpdateView.as_view()
