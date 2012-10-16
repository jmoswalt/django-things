from dateutil.parser import parse

from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.db.models import Q
from django.core.urlresolvers import reverse
from things.types import *


class ThingManager(models.Manager):
    def get_query_set(self):
        return super(ThingManager, self).get_query_set().filter(content_type_id=self.model.content_type().pk)

    def filter(self, *args, **kwargs):
        new_kwargs = {}
        attrs = getattr(self.model, 'attrs')
        if isinstance(attrs, tuple):
            for f in attrs:
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

    def order_by(self, *args, **kwargs):
        new_qs = []
        new_args = []
        attrs = getattr(self.model, 'attrs')
        attrs_list = self.model.attrs_list()
        if isinstance(attrs, tuple):
            for a in args:
                ordering = ""
                if a.startswith("-"):
                    ordering = "-"
                    a = a[1:]
                if a in attrs_list:
                    for f in attrs:
                        key = f['key']
                        if key == a:
                            new_qs.append(Q(datum__key=key))
                            new_args.append("".join([ordering, "datum__value"]))
                else:
                    new_args.append(a)
        args = new_args
        if new_qs:
            return super(ThingManager, self).filter(*new_qs).order_by(*args, **kwargs)
        return super(ThingManager, self).order_by(*args, **kwargs)


class Thing(models.Model):
    """A Thing is simply a name, slug, and an object type."""

    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, unique=True)
    content_type_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = ThingManager()

    def __init__(self, *args, **kwargs):
        super(Thing, self).__init__(*args, **kwargs)
        for f in self.attrs:
            val = self.get_value_of_attribute(f['key'])

            if f['datatype'] == TYPE_DATE and val:
                val = parse(val)  # 2012-10-13 12:34:55-05:00

            if f['datatype'] == TYPE_BOOLEAN:
                val = bool(val)  # 'True' or ''

            setattr(self, f['key'], val)

    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return "%s %s" % (self.obj_type, self.pk)

    @classmethod
    def content_type(cls):
        # Waiting on Django 1.5 support for
        # return ContentType.objects.get_for_model(cls, for_concrete_model=False)
        return ContentType.objects.get_for_model(cls)

    @classmethod
    def attrs(cls):
        return cls.attrs

    @classmethod
    def attrs_list(cls):
        return [k['key'] for k in cls.attrs]

    def get_value_of_attribute(self, attr):
        try:
            data = Data.objects.get(thing=self.id, key=attr)
            return data.value
        except Data.DoesNotExist:
            # return a string since the database is storing
            # all Data objects as strings
            return ''

    @models.permalink
    def get_absolute_url(self):
        return ("%s_detail" % self.content_type().name, [self.slug])

    def get_edit_url(self):
        ct = self.content_type()
        url = "admin:%s_%s_change" % (ct.app_label, ct.name)
        return reverse(url, args=[self.pk])

    def save(self, *args, **kwargs):
        self.content_type_id = self.content_type().pk
        super(Thing, self).save(*args, **kwargs)
        values = self.values
        for f in self.attrs:
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


def register_thing(cls, attrs, ct=None):
    setattr(cls, 'attrs', attrs)
    for a in attrs:
        setattr(cls, a['key'], '')


class Data(models.Model):
    """
    Data is an EAV construct for a Thing
    """

    thing = models.ForeignKey(Thing, related_name='datum')
    key = models.CharField(max_length=100, db_index=True)
    value = models.TextField()
    datatype = models.CharField(max_length=50, db_index=True)
