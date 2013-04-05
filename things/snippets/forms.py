from django import forms

from things.forms import ThingForm
from .models import Snippet


class SnippetForm(ThingForm):
    model = Snippet

    def __init__(self, *args, **kwargs):
        super(SnippetForm, self).__init__(*args, **kwargs)

        if self.instance.pk:
            if not self.fields['allow_html'].initial:
                self.fields['content'].widget = forms.widgets.Textarea()

        self.fields['slug'].help_text = 'Do NOT edit the slug. It comes from the theme.'
