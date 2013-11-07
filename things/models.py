import os
import subprocess
from dateutil.parser import parse

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.db.models import Q
from django.conf import settings

from .types import *
from .utils import handle_uploaded_file, clear_attr_cache


class AllThingsManager(models.Manager):
    pass


class ThingManager(models.Manager):
    def get_query_set(self):
        return super(ThingManager, self).get_query_set().filter(content_type_id=self.model.content_type().pk)

    def filter(self, *args, **kwargs):
        attrs = getattr(self.model, 'attrs')
        if isinstance(attrs, tuple):
            new_kwarg_list = []
            for f in attrs:
                new_kwargs = {}
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
                if new_kwargs:
                    new_kwarg_list.append(new_kwargs)

            # Make a set of querysets to reduce for
            # Multiple filters
            query_sets = []
            for item in new_kwarg_list:
                if 'datum__key' in item:
                    kwargs = item
                qs = super(ThingManager, self).filter(*args, **kwargs)
                query_sets.append(qs)

            # If we have filtered querysets, reduce them to their
            # mixed results
            if query_sets:
                return reduce(lambda x, y: x & y, query_sets)

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
                    new_args.append("".join([ordering, a]))
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
    creator = models.ForeignKey(User, null=True)

    objects = ThingManager()
    all_things = AllThingsManager()

    # Default properties
    public_filter_out = {}
    public_order = '-created_at'
    super_user_order = ('-created_at',)

    def __init__(self, *args, **kwargs):
        super(Thing, self).__init__(*args, **kwargs)
        if self.attrs and isinstance(self.attrs, tuple):
            for f in self.attrs:
                val = self.get_value_of_attribute(f['key'])

                if f['datatype'] == TYPE_DATE and val:
                    try:
                        val = parse(val)  # 2012-10-13 12:34:55-05:00
                    except ValueError:
                        val = val

                if f['datatype'] == TYPE_BOOLEAN:
                    val = bool(val)  # 'True' or ''

                if f['datatype'] == TYPE_FOREIGNKEY:
                    fk_model = f['model']
                    if val:
                        val = fk_model.objects.get(pk=val)  # Foreign Object

                if f['datatype'] == TYPE_FILE:
                    if val:
                        if val.startswith('/'):
                            val = val[1:]
                        try:
                            full_path = os.path.join(settings.MEDIA_ROOT, val)
                            with open(full_path, 'r') as fi:
                                val = File(fi)
                                val.url = val.name.replace(settings.PROJECT_ROOT, '')
                                val.name = val.name.replace(settings.MEDIA_ROOT, '')
                                if val.name.startswith('/'):
                                    val.name = val.name[1:]
                        except IOError:
                            val = ''

                setattr(self, f['key'], val)

    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return "%s %s" % (self.obj_type(), self.pk)

    @classmethod
    def content_type(cls):
        return ContentType.objects.get_for_model(cls, for_concrete_model=False)

    @classmethod
    def attrs(cls):
        return cls.attrs

    @classmethod
    def extra_apps(cls):
        classes = []
        pages_ct = ContentType.objects.get(app_label='pages', model='page')
        snippets_ct = ContentType.objects.get(app_label='snippets', model='snippet')
        sub_classes = cls.__subclasses__()
        for sub_class in sub_classes:
            if sub_class not in [pages_ct.model_class(), snippets_ct.model_class()]:
                classes.append(sub_class)
        return classes

    @classmethod
    def content_apps(cls):
        classes = []
        snippets_ct = ContentType.objects.get(app_label='snippets', model='snippet')
        sub_classes = cls.__subclasses__()
        for sub_class in sub_classes:
            if sub_class != snippets_ct.model_class():
                classes.append(sub_class)
        return classes

    @classmethod
    def attrs_list(cls):
        return [k['key'] for k in cls.attrs]


    @classmethod
    def get_add_url(cls):
        ct = cls.content_type()
        return reverse("admin:%s_%s_add" % (ct.app_label, ct.name))

    def obj_content_type(self):
        return ContentType.objects.get(pk=self.content_type_id)

    @models.permalink
    def get_absolute_url(self):
        return ("%s_detail" % self.obj_content_type().name.replace(' ', '_'), [self.slug])

    @models.permalink
    def get_edit_url(self):
        ct = self.obj_content_type()
        return ("admin:%s_%s_change" % (ct.app_label, ct.name), [self.pk])

    def save(self, *args, **kwargs):
        if not self.content_type_id:
            self.content_type_id = self.content_type().pk
        super(Thing, self).save(*args, **kwargs)
        values = getattr(self, 'values')
        if values:
            for f in self.attrs:
                key = f['key']
                value = values[key]
                datatype = f['datatype']
                if datatype == TYPE_FILE:
                    if isinstance(value, InMemoryUploadedFile):
                        value = handle_uploaded_file(self, value)
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

        clear_attr_cache(self)
        if settings.USE_STATIC_SITE:
            subprocess.Popen(["python", "manage.py", "rebuild_static_site"])

    def obj_type(self):
        return self.content_type().name

    def obj_type_plural(self):
        return self._meta.verbose_name_plural

    def default_order_field(self):
        return getattr(self, self.public_order.replace('-', ''))

    def get_value_of_attribute(self, attr):
        cache_key = "%s.%s.%s" % (settings.SITE_CACHE_KEY, attr, self.pk)
        cached = cache.get(cache_key)
        if cached is None:
            try:
                data = Data.objects.get(thing=self.id, key=attr)
                cached = data.value
            except Data.DoesNotExist:
                # return a string since the database is storing
                # all Data objects as strings
                cached = ''
            cache.set(cache_key, cached)

        return cached


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


class StaticBuild(models.Model):
    """
    StaticBuild is a record of when a static build was made, so that
    content that hasn't changed isn't rebuilt
    """
    created_at = models.DateTimeField(auto_now_add=True)
