import os

from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime
from django.core.files.base import ContentFile
from django.conf import settings

from redactor.widgets import RedactorEditor

from things.types import *
from things.models import Thing


class ThingForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ThingForm, self).__init__(*args, **kwargs)
        if "content_type_id" in self.fields:
            del self.fields['content_type_id']

        if "creator" in self.fields:
            del self.fields['creator']

        for f in self.instance.attrs:

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
                    elif f['datatype'] == TYPE_FILE:
                        self.fields[key] = forms.FileField(required=False, widget=forms.ClearableFileInput)
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
            elif f['datatype'] == TYPE_LONGTEXT:
                self.fields[key].widget = RedactorEditor()

            # Populate help text if it's defined
            if not self.fields[key].help_text:
                if "help_text" in f:
                    self.fields[key].help_text = f['help_text']
                elif "description" in f:
                    # Auto-create the description if using a shared field
                    if "{{ model }}" in f['description']:
                        self.fields[key].help_text = f['description'].replace("{{ model }}", self.instance.obj_type().title())
                    else:
                        self.fields[key].help_text = f['description']

            # Grab the attribute and try to prepopulte the initial
            # if there is a value.
            attr = getattr(self.instance, key)
            if attr:
                if f['datatype'] == TYPE_FILE:
                    # Do something to assign and 'url' attribute
                    # to the file so the ClearableFileInput works
                    file_path = attr
                    full_path = "%s%s" % (settings.PROJECT_ROOT, file_path)
                    with open(full_path, 'r') as f:
                        attr = ContentFile(f.read())
                    attr.url = file_path
                self.fields[key].initial = attr

    def clean_slug(self):
        slug = self.cleaned_data.get('slug')
        if slug.startswith('/'):
            slug = slug[1:]
        if slug.endswith('/'):
            slug = slug[:-1]
        if not slug:
            raise forms.ValidationError("The slug can't only contain /'s.")
        else:
            if not self.instance.pk:
                try:
                    exists = Thing.all_things.get(slug=slug)
                except TypeError:
                    raise forms.ValidationError("That slug is already used.")
                except Thing.DoesNotExist:
                    pass

        slug = slug.replace(" ", "-")

        return slug

    def save(self, *args, **kwargs):
        thing = super(ThingForm, self).save(*args, **kwargs)
        if not thing.creator:
            thing.creator = self.user
        thing.values = {}
        for f in self.instance.attrs:
            key = f['key']
            thing.values[key] = ''
            if key in self.cleaned_data and self.cleaned_data[key]:
                thing.values[key] = self.cleaned_data[key]
        return thing
