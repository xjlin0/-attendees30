from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit

from attendees.persons.models import Attendee


class AttendeeForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = (
            'gender',
            'division',
            'first_name',
            'last_name',
            'first_name2',
            'last_name2',
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Save'))
