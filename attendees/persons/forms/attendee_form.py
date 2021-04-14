from django import forms
from django.forms.formsets import formset_factory

from attendees.persons.models import Attendee


class AttendeeForm(forms.ModelForm):
    fields = '__all__'

    class Meta:
        model = Attendee
        fields = "__all__"


AttendeeFormSet = formset_factory(
    AttendeeForm,
    extra=2,
    max_num=2,
    min_num=1
)
