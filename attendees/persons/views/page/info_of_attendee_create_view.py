from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic.edit import CreateView, UpdateView
from django.forms.models import inlineformset_factory
# ChildFormset = inlineformset_factory(
#     Parent, Child, fields=('name',)
# )
from attendees.persons.models import Attendee
from attendees.users.authorization import RouteGuard

# Todo: check attendee.user is current user or managers


@method_decorator([login_required], name='dispatch')
class InfoOfAttendeeCreateView(RouteGuard, CreateView):
    model = Attendee
    fields = '__all__'
    template_name = 'persons/info_of_attendee_create_view.html'

    def get_context_data(self, **kwargs):
        # we need to overwrite get_context_data to make sure that our formset is rendered
        data = super().get_context_data(**kwargs)
        if self.request.POST:
            pass  # data["children"] = ChildFormset(self.request.POST)
        else:
            pass  # data["children"] = ChildFormset()
        return data

    def form_valid(self, form):
        context = self.get_context_data()
        # children = context["children"]
        self.object = form.save()
        # if children.is_valid():
        #     children.instance = self.object
        #     children.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("users:detail", kwargs={"username": self.request.user.username})


info_of_attendee_create_view = InfoOfAttendeeCreateView.as_view()


