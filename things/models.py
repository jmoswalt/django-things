from dateutil.parser import parse

from django.db import models
from things.types import *


class Thing(models.Model):
    """A Thing is simply a name, slug, and an object type."""

    name = models.CharField(max_length=200)
    type = models.CharField(max_length=50)
    slug = models.CharField(max_length=200, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        super(Thing, self).__init__(*args, **kwargs)
        for f in self.attrs():
            val = self.get_value_of_attribute(f['key'])

            if f['datatype'] == TYPE_DATE and val:
                val = parse(val)  # 2012-10-13 12:34:55-05:00

            setattr(self, f['key'], val)

    def attrs(self):
        return ""

    def get_value_of_attribute(self, attr):
        try:
            data = Data.objects.get(thing=self.id, key=attr)
            return data.value
        except Data.DoesNotExist:
            return None

    def save(self, *args, **kwargs):
        super(Thing, self).save(*args, **kwargs)
        values = self.values
        for f in self.attrs():
            key = f['key']
            value = values[key]
            datatype = f['datatype']
            try:
                data = Data.objects.get(thing=self, key=key)
                data.value = value
                data.datatype = datatype
                data.save()
            except Data.DoesNotExist:
                Data.objects.create(
                    thing=self,
                    key=key,
                    value=value,
                    datatype=datatype
                )

    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return "%s %s" % (self.type, self.pk)


class Data(models.Model):
    """
    Data is an EAV construct for a Thing
    """

    thing = models.ForeignKey(Thing, related_name='datum')
    key = models.CharField(max_length=100, db_index=True)
    value = models.TextField()
    datatype = models.CharField(max_length=50, db_index=True)
