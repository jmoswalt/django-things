from django import forms


class ThingForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ThingForm, self).__init__(*args, **kwargs)
        for f in self.instance.attrs():

            key = f['key']
            if key in self.fields:
                # Set the label
                self.fields[f['key']].label = f['name']

                # Populate help text if it's defined.
                if "help_text" in f:
                    self.fields[f['key']].help_text = f['help_text']
                elif "description" in f:
                    self.fields[f['key']].help_text = f['description']

                # Grab the attribute and try to prepopulte the initial
                # if there is a value.
                attr = getattr(self.instance, f['key'])
                if attr:
                    self.fields[f['key']].initial = attr

    def save(self, *args, **kwargs):
        thing = super(ThingForm, self).save(*args, **kwargs)
        thing.values = {}
        for f in self.instance.attrs():
            key = f['key']
            thing.values[key] = ''
            if key in self.cleaned_data and self.cleaned_data[key]:
                thing.values[key] = self.cleaned_data[key]
        return thing
