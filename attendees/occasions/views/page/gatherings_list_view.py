from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic.list import ListView
from django.shortcuts import render

from attendees.users.authorization import RouteGuard


class GatheringsListView(LoginRequiredMixin, RouteGuard, ListView):
    queryset = []
    template_name = 'occasions/gatherings_list_view.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'meets_endpoint': '/occasions/api/organization_meets/',
        })
        return context

    def render_to_response(self, context, **kwargs):
        if self.request.is_ajax():
            pass

        else:
            return render(self.request, self.get_template_names()[0], context)


gatherings_list_view = GatheringsListView.as_view()
