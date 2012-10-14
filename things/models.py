from dateutil.parser import parse

from django.db import models
from things.types import *


class ThingManager(models.Manager):
    def get_query_set(self):
        return super(ThingManager, self).get_query_set().filter(obj_type=self.model.clstype())

    def filter(self, *args, **kwargs):
        new_kwargs = {}
        for f in self.model.attrs():
            key = f['key']
            for k in kwargs:
                if key in k:
                    new_kwargs['datum__key'] = key
                    # see if the keys end the same
                    if k.endswith(key):
                        new_kwargs['datum__value'] = kwargs[key]
                    # parse out the unmatching ending portion
                    else:
                        mixed_key = 'datum__value%s' % k[len(key):]
                        new_kwargs[mixed_key] = kwargs[k]
        if 'datum__key' in new_kwargs:
            kwargs = new_kwargs
        return super(ThingManager, self).filter(*args, **kwargs)


class Thing(models.Model):
    """A Thing is simply a name, slug, and an object type."""

    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, unique=True)
    obj_type = models.CharField(max_length=50)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ThingManager()

    def __init__(self, *args, **kwargs):
        super(Thing, self).__init__(*args, **kwargs)
        for f in self.attrs():
            val = self.get_value_of_attribute(f['key'])

            if f['datatype'] == TYPE_DATE and val:
                val = parse(val)  # 2012-10-13 12:34:55-05:00

            setattr(self, f['key'], val)

    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return "%s %s" % (self.obj_type, self.pk)

    @classmethod
    def attrs(cls):
        return ""

    @classmethod
    def clstype(cls):
        return "thing"

    def get_value_of_attribute(self, attr):
        try:
            data = Data.objects.get(thing=self.id, key=attr)
            return data.value
        except Data.DoesNotExist:
            # return a string since the database is storing
            # all Data objects as strings
            return ''

    def save(self, *args, **kwargs):
        self.obj_type = self.clstype()
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


class Data(models.Model):
    """
    Data is an EAV construct for a Thing
    """

    thing = models.ForeignKey(Thing, related_name='datum')
    key = models.CharField(max_length=100, db_index=True)
    value = models.TextField()
    datatype = models.CharField(max_length=50, db_index=True)
