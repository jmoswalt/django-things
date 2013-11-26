from django import forms
from django.contrib.admin.widgets import AdminSplitDateTime

from redactor.widgets import RedactorEditor

from .types import *
from .models import Thing, ThingType


class ThingTypeForm(forms.ModelForm):
    model = ThingType
    fields = [
        'name',
        'slug',
        'json',
        'creator',
        'list_template',
        'detail_template',
    ]


class ThingForm(forms.ModelForm):

    def __init__(self, *args, **kwargs):
        super(ThingForm, self).__init__(*args, **kwargs)
        if 'id' in self.fields:
            del self.fields['id']
        if 'json' in self.fields:
            del self.fields['json']
        if "content_type_id" in self.fields:
            if not self.instance.pk:
                del self.fields['content_type_id']
            else:
                choices = [(i.content_type().pk, i.content_type().name.title()) for i in Thing.__subclasses__()]
                self.fields['content_type_id'] = forms.ChoiceField(required=True, choices=choices, label="Thing Type", initial=self.instance.content_type().pk)

        if "creator" in self.fields:
            del self.fields['creator']
        # published_at field is re-added at the end to be last.
        if 'published_at' in self.fields:
            del self.fields['published_at']

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
                    elif f['datatype'] == TYPE_FOREIGNKEY:
                        choices = [(i.pk, i.name) for i in f['model'].objects.all()]
                        self.fields[key] = forms.ChoiceField(required=False, choices=choices)
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

            # Set the disabled status
            if "editable" in f:
                if not f['editable']:
                    self.fields[key].widget.attrs['disabled'] = 'disabled'

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
                else:
                    self.fields[key].help_text = "The %s of the %s" % (f['name'], self.instance.obj_type().title())

            # Grab the attribute and try to prepopulte the initial
            # if there is a value.
            attr = self.instance.get_val(f)
            if attr:
                if f['datatype'] == TYPE_FOREIGNKEY:
                    attr = attr.pk
                self.fields[key].initial = attr

        self.fields['published_at'] = forms.DateTimeField(label="Published", widget=AdminSplitDateTime, required=False, help_text="This field controls both the order of the item and whether it's publicly viewable. If the publish date is in the future or not set, this item won't be viewable to logged out viewers")

    def clean_slug(self):
        slug = self.cleaned_data['slug']

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
                except Thing.DoesNotExist:
                    exists = False
            else:
                try:
                    exists = Thing.all_things.exclude(pk=self.instance.pk).get(slug=slug)
                except Thing.DoesNotExist:
                    exists = False

            if exists:
                raise forms.ValidationError("That slug is already used.")

        slug = slug.replace(" ", "-").lower()

        return slug

    def save(self, *args, **kwargs):
        thing = super(ThingForm, self).save(*args, **kwargs)
        if 'content_type_id' in self.cleaned_data:
            thing.content_type_id = self.cleaned_data['content_type_id']
        if not thing.creator:
            thing.creator = self.user
        thing.values = {}
        for f in self.instance.attrs:
            key = f['key']
            thing.values[key] = ''

            if 'editable' in f:
                if not f['editable']:
                    self.cleaned_data[key] = thing.get_val(f)

            if key in self.cleaned_data and self.cleaned_data[key]:
                thing.values[key] = self.cleaned_data[key]
        return thing


class ThingImportForm(forms.Form):
    """Form used for importing new things."""

    thing_type = forms.CharField(required=False, label="Thing Type")
    thing_type_name = forms.CharField(label="Type Name", required=False, help_text='Singular name, like "Article"')
    upload_file = forms.FileField(label='File', required=True)

    def __init__(self, *args, **kwargs):
        super(ThingImportForm, self).__init__(*args, **kwargs)
        choices = [('', '---')] + [(i.content_type().pk, i.content_type().name.title()) for i in Thing.__subclasses__()]
        self.fields['thing_type'] = forms.ChoiceField(required=False, choices=choices, label="Thing Type", initial=None)
