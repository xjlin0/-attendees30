from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Row, Column, ButtonHolder, Submit


class AttendeesFormSetHelper(FormHelper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.form_method = 'post'
        self.layout = Layout(

            Fieldset(
                "some explaining text or other addition fields, such as counter: {{ forloop.counter }}",
            ),

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

            ButtonHolder(
                Submit('submit', 'Save All', css_class='btn btn-success')
            ),
        )
        self.render_required_fields = True
