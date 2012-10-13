from dateutil.parser import parse

from django.db import models
from things.types import *


class Thing(models.Model):
    """A Thing is simply a name and an object type."""

    name = models.CharField(max_length=200)
    type = models.CharField(max_length=50)
    create_dt = models.DateTimeField(auto_now_add=True)
    update_dt = models.DateTimeField(auto_now=True)

    def __init__(self, *args, **kwargs):
        super(Thing, self).__init__(*args, **kwargs)
        for f in self.attrs():
            val = self.get_value_of_attribute(f['slug'])

            if f['datatype'] == TYPE_DATE and val:
                val = parse(val)  # 2012-10-13 12:34:55-05:00

            setattr(self, f['slug'], val)

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
            key = f['slug']
            value = values[key]
            datatype = f['datatype']
            print key, value
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
    key = models.CharField(max_length=100)
    value = models.TextField()
    datatype = models.CharField(max_length=50)


PAGE_ATTRIBUTES = (
    {"name": "Content",
    "slug": "content",
    "description": "The main content of the ariticle.",
    "datatype": TYPE_TEXT},
    )


class PageManager(models.Manager):
    def get_query_set(self):
        return super(PageManager, self).get_query_set().filter(type="page")


class Page(Thing):
    objects = PageManager()

    class Meta:
        proxy = True

    def save(self, *args, **kwargs):
        self.type = "page"
        super(Page, self).save(*args, **kwargs)

    def attrs(self):
        return PAGE_ATTRIBUTES
