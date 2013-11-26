import os
from uuid import uuid4
import subprocess
from dateutil.parser import parse
from jsonfield import JSONField

from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse, NoReverseMatch
from django.utils import timezone
from django.core.files import File
from django.core.files.uploadedfile import InMemoryUploadedFile
from django.db import models
from django.conf import settings

from .types import *
from .utils import handle_uploaded_file, load_models

# Postgres want's a valid date for an empty datefield in json
# so the date below is used at the "empty" datetime
ZERO_DATE = '1970-01-01 01:00:00-00:00'


class AllThingsManager(models.Manager):
    pass


class ThingQuerySet(models.query.QuerySet):

    def order_by(self, *field_names):
        """
        Returns a new QuerySet instance with the ordering changed.
        """
        assert self.query.can_filter(), \
                "Cannot reorder a query once a slice has been taken."
        clone = self._clone()
        attrs_list = self.model.attrs_list()
        new_args = list()

        for arg in field_names:
            arg_key = arg.replace('-', '')
            if arg_key in attrs_list:
                # _orderby is appended so that we can use the val in the init
                # so we can format the value instead of the raw data being used
                # since we are casting the field
                fieldtype = 'varchar'
                for attr in self.model.attrs:
                    if attr['key'] == arg_key:
                        if attr['datatype'] == TYPE_DATE:
                            fieldtype = 'timestamp'
                arg_order_name = arg_key + "_orderby"
                clone.query.add_extra({arg_order_name: "(json->>'%s')::%s" % (arg_key, fieldtype)}, None, None, None, None, None)
                arg = arg + "_orderby"
            new_args.append(arg)

        clone.query.add_extra(None, None, None, None, None, new_args)
        return clone


KWARG_MAP = {
    'gt': ">",
    'lt': "<",
    'gte': ">=",
    'lte': "<=",
}

class ThingManager(models.Manager):
    def __init__(self, qs_class=ThingQuerySet):
        self.queryset_class = qs_class
        super(ThingManager, self).__init__()

    def get_query_set(self):
        return self.queryset_class(self.model).filter(content_type_id=self.model.content_type().pk)

    def filter(self, *args, **kwargs):
        """

        Example:

        k = 'published_at__gte'
        kw = 'published_at'
        new_key = 'filter_published_at__gte'
        new_key_name = 'filter_published_at'
        """
        thesuper = super(ThingManager, self)
        new_kwargs = kwargs

        if self.model != Thing:
            attrs_list = self.model.attrs_list()
            new_kwargs = {}
            for k, v in kwargs.items():
                if '__' in k:
                    kw = k.split('__', 1)[0]
                    kw_filter = k.split('__', 1)[1]
                else:
                    kw = k
                    kw_filter = ''
                if kw in attrs_list:
                    fieldtype = 'varchar'
                    for attr in self.model.attrs:
                        if attr['key'] == kw:
                            if attr['datatype'] == TYPE_DATE:
                                fieldtype = 'timestamp'
                                if v == 0 or not v:
                                    v = parse(ZERO_DATE)
                                v = v.replace(second=0, microsecond=0)
                            elif attr['datatype'] == TYPE_BOOLEAN:
                                fieldtype = 'boolean'
                                v = bool(v)
                    kw_compare = "="
                    if kw_filter in KWARG_MAP:
                        kw_compare = KWARG_MAP[kw_filter]
                    st = "(json->>'%s')::%s %s '%s'" % (kw, fieldtype, kw_compare, v)
                    thesuper = thesuper.extra(where=[st])
                else:
                    # Include 'real' field kwargs in the normal way
                    # If it's one of the known fields
                    if kw in [f.name for f in self.model._meta.fields]:
                        new_kwargs[k] = v

        return thesuper.filter(*args, **new_kwargs)


class ThingAbstract(models.Model):
    """A Thing is simply a name, slug, and an object type."""

    id = models.CharField(max_length=64, unique=True, primary_key=True, blank=True)
    name = models.CharField(max_length=200)
    slug = models.CharField(max_length=200, unique=True)
    json = JSONField(default={})
    created_at = models.DateTimeField('Created', auto_now_add=True)
    updated_at = models.DateTimeField('Updated', auto_now=True)
    creator = models.ForeignKey(User, null=True, blank=True)

    class Meta:
        abstract = True

class Thing(ThingAbstract):
    """A Thing is simply a name, slug, published date, and an object type."""

    content_type_id = models.IntegerField()
    published_at = models.DateTimeField('Published', null=True, blank=True, default=timezone.now())

    objects = ThingManager()
    all_things = AllThingsManager()

    # Default properties
    public_filter_out = {
        'published_at__gte': parse(ZERO_DATE),
        'published_at__lte': timezone.now()
        }

    public_order = '-published_at'
    super_user_order = ('-published_at', '-created_at',)

    def __init__(self, *args, **kwargs):
        if 'rebuild' in kwargs: kwargs.pop('rebuild')
        super(Thing, self).__init__(*args, **kwargs)
        if not self.id:
            self.id = str(uuid4())
        if hasattr(self, 'attrs'):
            for f in self.attrs:
                setattr(self, f['key'], self.get_val(f))

    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return "%s %s" % (self.obj_type(), self.pk)

    @classmethod
    def content_type(cls):
        return ContentType.objects.get_for_model(cls, for_concrete_model=False)

    # @classmethod
    # def attrs(cls):
    #     return cls.attrs

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
    def admin_url(cls):
        ct = cls.content_type()
        try:
            return reverse("admin:%s_%s_changelist" % (ct.app_label, ct.name))
        except NoReverseMatch:
            return ''

    def obj_content_type(self):
        return self.content_type()

    @models.permalink
    def get_absolute_url(self):
        return ("%s_detail" % self.obj_content_type().name.replace(' ', '_').lower(), [self.slug])

    @models.permalink
    def get_edit_url(self):
        ct = self.obj_content_type()
        return ("admin:%s_%s_change" % (ct.app_label, ct.name), [self.pk])

    def get_val_from_key(self, key):
        for attr in self.attrs:
            if attr['key'] == key:
                return self.get_val(attr)
        return None

    def get_attr_from_key(self, key):
        for attr in self.attrs:
            if attr['key'] == key:
                return attr
        return None

    def get_val(self, f):
        if not self.json:
            return ''
        val = self.json.get(f['key'], None)

        if f['datatype'] == TYPE_DATE:
            if not val or val == ZERO_DATE:
                val = ''
            else:
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

        if f['datatype'] == TYPE_LONGTEXT:
            val = val

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

        return val

    def save(self, *args, **kwargs):
        # Handle preventing a rebuild on an import
        rebuild = True
        if 'rebuild' in kwargs:
            rebuild = kwargs.pop('rebuild')
        # Check if we are using get_or_create
        if kwargs.get('using') == 'default' and kwargs.get('force_insert'):
            rebuild = False

        if not self.content_type_id:
            self.content_type_id = self.content_type().pk
        try:
            values = getattr(self, 'values')
        except AttributeError:
            values = None
        if values:
            for f in self.attrs:
                # Handle uploaded file fields
                if isinstance(values[f['key']], InMemoryUploadedFile):
                    values[f['key']] = handle_uploaded_file(self, values[f['key']])
                elif isinstance(values[f['key']], File):
                    values[f['key']] = values[f['key']].__str__()

                if not values[f['key']]:
                    if f['datatype'] == TYPE_DATE:
                        values[f['key']] = ZERO_DATE

                    if f['datatype'] == TYPE_BOOLEAN:
                        values[f['key']] = False

            # Save all values to json
            self.json = values

        super(Thing, self).save(*args, **kwargs)

        if settings.USE_STATIC_SITE and rebuild:
            subprocess.Popen(["python", "manage.py", "rebuild_static_site"])

    def attr_obj(self, key):
        for attr in self.attrs:
            if attr['key'] == key:
                return attr
        return None

    def obj_type(self):
        return self.content_type().name

    def obj_type_plural(self):
        return self._meta.verbose_name_plural

    def default_order_field(self):
        field = self.public_order.replace('-', '')
        if field in self.attrs_list():
            return self.get_val(self.attr_obj(field)) or parse(ZERO_DATE)
        return getattr(self, field)

    def published_field(self):
        if self.default_order_field() == parse(ZERO_DATE):
            return None
        return self.default_order_field()

    @classmethod
    def thing_type_id(cls):
        try:
            tt = ThingType.objects.get(name=cls._meta.verbose_name)
            return tt.pk
        except:
            return None


class ThingType(ThingAbstract):
    """An expansion on a Content Type that includes field definitions."""

    # TODO: make this a one-to-one field
    content_type_id = models.IntegerField(null=True, blank=True)
    list_template = models.TextField(blank=True)
    detail_template = models.TextField(blank=True)

    objects = models.Manager()

    def __init__(self, *args, **kwargs):
        super(ThingType, self).__init__(*args, **kwargs)
        if not self.id:
            self.id = str(uuid4())

    def __unicode__(self):
        if self.name:
            return self.name
        else:
            return "%s" % self.pk

    def get_class(self):
        meta = {'verbose_name': str(self.name), 'ordering': ('-published_at',)}
        return type(str(self.name), (Thing,), {
            '__module__': 'things.models',
            'Meta': ThingMeta(**meta),
        })

    def get_feed_class(self):
        from .feeds import ThingFeed
        return type(str(self.name), (ThingFeed,), {
            '__module__': 'things.feeds',
            'item_pubdate': lambda x,y: y.published_at,
            'item_description': lambda x,y: getattr(y, 'content', y.name),
            'model': self.get_class()
        })

    def save_template(self, template_name, field):
        folder_path = os.path.join(settings.THEME_PATH, "templates", "things")
        file_path = os.path.join(folder_path, "%s_%s.html" % (self.get_class()._meta.verbose_name.lower(), template_name))
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)
        with open(file_path, 'wb+') as destination:
            destination.write(getattr(self, field))

    def save(self, *args, **kwargs):
        if not self.content_type_id:
            cts = ContentType.objects.filter(name=self.name, app_label='things')
            if cts:
                self.content_type_id = cts[0].id

        # TODO: if name changes, update the ContentType with the new name

        super(ThingType, self).save(*args, **kwargs)

        if self.list_template:
            self.save_template('list', 'list_template')
        if self.detail_template:
            self.save_template('detail', 'detail_template')

        load_models()

        if settings.PROCESS_NAME != '':
            os.system('sudo service %s reload' % settings.PROCESS_NAME)


class ThingMeta(object):
    """
    Proxy meta class to use to create dynamic models.

    This class sets proxy to be True and sets other attributes
    that are passed in the instantiation. Only certain keys are
    accepted.
    """
    proxy = True

    def __init__(self, *args, **kwargs):
        keys = ['verbose_name', 'verbose_name_plural', 'ordering']
        for k, v in kwargs.items():
            if k in keys:
                setattr(self, k, v)


def register_thing(cls, attrs=None, ct=None):
    if hasattr(cls, 'cls_attrs'):
        ats = cls.cls_attrs
    else:
        ats = attrs
    setattr(cls, 'attrs', ats)
    for a in ats:
        if 'key' in a:
            setattr(cls, a['key'], '')


class StaticBuild(models.Model):
    """
    StaticBuild is a record of when a static build was made, so that
    content that hasn't changed isn't rebuilt
    """
    created_at = models.DateTimeField(auto_now_add=True)
