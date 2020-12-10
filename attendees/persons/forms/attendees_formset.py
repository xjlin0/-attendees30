from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder, Row, Column

# from attendees.persons.forms import AttendeesFormSetHelper
from attendees.persons.forms import AttendeesFormSetHelper
from attendees.persons.models import Attendee
from django.forms.models import formset_factory


class AttendeesForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = '__all__'
        #     (
        #     'gender',
        #     'division',
        #     'first_name',
        #     'last_name',
        #     'first_name2',
        #     'last_name2',
        # )

#    def __init__(self, *args, **kwargs):
#        super().__init__(*args, **kwargs)
#        self.helper = AttendeesFormSetHelper()
        # self.helper.form_method = 'post'
        # self.helper.layout = Layout(
        #
        #     Fieldset(
        #         'some explaining text or other addition fields, such as id: {{id}}',
        #     ),
        #
        #     Row(
        #         Column('gender'),
        #         Column('division'),
        #     ),
        #
        #     Row(
        #         Column('first_name'),
        #         Column('last_name'),
        #         title="In English please",
        #     ),
        #
        #     Row(
        #         Column('first_name2'),
        #         Column('last_name2'),
        #         title="Can be in a different language",
        #     ),
        #
        #     ButtonHolder(
        #         Submit('submit', 'Save!', css_class='btn btn-success')
        #     ),
        # )


AttendeesFormSet = formset_factory(  # modelformset_factory ??
    AttendeesForm,
    extra=2,
    max_num=2,
    min_num=1
)

