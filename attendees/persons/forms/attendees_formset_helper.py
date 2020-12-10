from crispy_forms.bootstrap import AccordionGroup, Accordion
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, ButtonHolder, Submit, HTML


class AttendeesFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.render_required_fields = True
        self.form_method = 'post'
        self.layout = Layout(
            Accordion(
                AccordionGroup("{{ first_name }}"+" {{forloop.counter}}",

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
                )
            )
        )
        self.render_required_fields = True
