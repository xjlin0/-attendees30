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


class SpyGuard(UserPassesTestMixin):

    def test_func(self):  # Superusers can still access such attendee in admin UI
        targeting_attendee_id = self.request.META.get('HTTP_X_TARGET_ATTENDEE_ID', self.kwargs.get('attendee_id'))
        current_attendee = self.request.user.attendee
        if targeting_attendee_id:
            if current_attendee:
                if current_attendee.under_same_org_with(targeting_attendee_id):
                    return True  # Todo: check relation/scheduler permission for non-dada-admin
        else:
            return True

        time.sleep(2)
        return False

    def handle_no_permission(self):
        """ Show warning info so user can know what happened """
        return HttpResponse('Do you have attendee associated with your user? You do not have permissions to visit this!')


class RouteAndSpyGuard(UserPassesTestMixin):
    def test_func(self):
        return RouteGuard.test_func(self) and SpyGuard.test_func(self)
