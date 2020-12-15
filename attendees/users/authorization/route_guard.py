import time
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse

from attendees.users.models import Menu


class RouteGuard(UserPassesTestMixin):

    def test_func(self):
        whether_user_allowed_to_read_the_page = Menu.objects.filter(
            auth_groups__in=self.request.user.groups.all(),
            url_name=self.request.resolver_match.url_name,
            menuauthgroup__read=True,
        ).exists()
        if not whether_user_allowed_to_read_the_page:
            time.sleep(2)

        return whether_user_allowed_to_read_the_page

    def handle_no_permission(self):
        """ Show warning info so user can know what happened """
        return HttpResponse('Is menu.url_name correct? You groups does not have permissions to visit such route!')
