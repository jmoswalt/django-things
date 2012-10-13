from django import forms

from things.models import Page


class ThingForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ThingForm, self).__init__(*args, **kwargs)
        for f in self.instance.attrs():
            # Set the label
            self.fields[f['slug']].label = f['name']

            # Populate help text if it's defined.
            if "help_text" in f:
                self.fields[f['slug']].help_text = f['help_text']

            # Grab the attribute and try to prepopulte the initial
            # if there is a value.
            attr = getattr(self.instance, f['slug'])
            if attr:
                self.fields[f['slug']].initial = attr

    def save(self, *args, **kwargs):
        thing = super(ThingForm, self).save(*args, **kwargs)
        thing.values = {}
        for f in self.instance.attrs():
            key = f['slug']
            thing.values[key] = ''
            if self.cleaned_data[key]:
                thing.values[key] = self.cleaned_data[key]
        return thing


class PageForm(ThingForm):

    content = forms.CharField(widget=forms.Textarea)

    class Meta:
        model = Page
