import time
from django.contrib.auth.mixins import UserPassesTestMixin
from django.http import HttpResponse

from attendees.persons.models import Attendee
from attendees.users.models import Menu


class SpyGuard(UserPassesTestMixin):

    def test_func(self):
        print("hi 12 here is self.kwargs: ")
        print(self.kwargs)
        print("hi 14 here is self: ")
        print(self)
        print("hi 16 here is self.request: ")
        print(self.request)
        print("hi 18 here is self.request.query_params: ")
        print(self.request.query_params)
        targeting_attendee_id = self.kwargs.get('attendee_id', None)
        current_attendee = self.request.user.attendee

        if targeting_attendee_id:
            if current_attendee:
                if current_attendee.under_same_org_with(targeting_attendee_id):
                    return True
        else:
            return True

        time.sleep(2)
        return False

    def handle_no_permission(self):
        """ Show warning info so user can know what happened """
        return HttpResponse('Do you have attendee associate with your user? You do not have permissions to visit this!')
