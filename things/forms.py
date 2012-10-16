from django import forms
from django.contrib.contenttypes.models import ContentType
from django.contrib.admin.widgets import AdminSplitDateTime

from things.types import *


class ThingForm(forms.ModelForm):

    class Meta:
        exclude = ["content_type_id"]

    def __init__(self, *args, **kwargs):
        super(ThingForm, self).__init__(*args, **kwargs)
        if "content_type_id" in self.fields:
            # Get rid of the content_type_id field
            del self.fields['content_type_id']

        for f in self.instance.attrs():

            key = f['key']
            if key not in self.fields:
                # Add the field to the form
                if "form_field" in f:
                    self.fields[key] = f['form_field']
                else:
                    if f['datatype'] == TYPE_BOOLEAN:
                        self.fields[key] = forms.BooleanField(required=False)
                    elif f['datatype'] == TYPE_DATE:
                        self.fields[key] = forms.DateTimeField(widget=AdminSplitDateTime)
                    else:
                        self.fields[key] = forms.CharField(required=False)

            # Set the label
            if "name" in f:
                self.fields[key].label = f['name']
            else:
                self.fields[key].label = f['key']

            # Set the required status
            if "required" in f:
                self.fields[key].required = f['required']
            else:
                self.fields[key].required = False

            # Set the widget if it's defined
            if "form_widget" in f:
                self.fields[key].widget = f['form_widget']

            # Populate help text if it's defined
            if not self.fields[key].help_text:
                if "help_text" in f:
                    self.fields[key].help_text = f['help_text']
                elif "description" in f:
                    self.fields[key].help_text = f['description']

            # Grab the attribute and try to prepopulte the initial
            # if there is a value.
            attr = getattr(self.instance, key)
            if attr:
                self.fields[key].initial = attr

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug.startswith('/'):
            slug = slug[1:]
        if slug.endswith('/'):
            slug = slug[:-1]
        if not slug:
            raise forms.ValidationError("The slug can't only contain /'s.")

        slug = slug.replace(" ", "-")

        return slug

    def save(self, *args, **kwargs):
        thing = super(ThingForm, self).save(*args, **kwargs)
        thing.values = {}
        for f in self.instance.attrs():
            key = f['key']
            thing.values[key] = ''
            if key in self.cleaned_data and self.cleaned_data[key]:
                thing.values[key] = self.cleaned_data[key]
        return thing
