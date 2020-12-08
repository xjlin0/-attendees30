from django import forms

from attendees.persons.models import Attendee


class AttendeeForm(forms.ModelForm):
    fields = '__all__'

    class Meta:
        model = Attendee
        fields = "__all__"
