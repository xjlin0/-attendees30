from crispy_forms.bootstrap import Accordion, AccordionGroup
from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, ButtonHolder, Row, Column

# from attendees.persons.forms import AttendeesFormSetHelper
from attendees.persons.forms import AttendeesFormSetHelper
from attendees.persons.models import Attendee
from django.forms.models import formset_factory, inlineformset_factory, modelformset_factory


class AttendeesForm(forms.ModelForm):
    class Meta:
        model = Attendee
        fields = '__all__'
        # help_texts = {
        #     "full_name": None,
        # }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper(self)  # somehow form info is unavailable in separated helper
        self.render_hidden_fields = True  # https://django-crispy-forms.readthedocs.io/en/latest/form_helper.html
        self.render_required_fields = True
        self.helper.form_id = kwargs.get('prefix', '')
        self.helper.form_method = 'post'
        self.helper.form_tag = False
        self.helper.disable_csrf = True
        instance = kwargs.get('instance', Attendee())
        self.helper.layout = Layout(
            Accordion(
                AccordionGroup(instance.full_name,
                    Row(
                       Column('gender'),
                       Column('division'),
                    ),

                    Row(
                       Column('first_name'),
                       Column('last_name'),
                       title="In English please",
                    ),

                    Row(
                       Column('first_name2'),
                       Column('last_name2'),
                       title="Can be in a different language",
                    ),
                    Row(
                       Column('related_ones'),
                       Column('families'),
                    ),
                    Row(
                       Column('addresses'),
                    ),
                    css_id='attendee_' + str(instance.id),
                )
            )
        )


AttendeesFormSet = modelformset_factory(
    Attendee,
    form=AttendeesForm,
    extra=1,
    max_num=2,
    min_num=1
)


