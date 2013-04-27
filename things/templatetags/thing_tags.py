from django.template import Library, Node, TemplateSyntaxError, Variable
from django.template.defaultfilters import date
from django.contrib.contenttypes.models import ContentType
from django.contrib.auth.models import AnonymousUser
from django.conf import settings
from django.utils import timezone

from things.types import TYPE_DATE, TYPE_FILE
from things.models import Thing
from things.utils import get_thing_objects_qs

register = Library()


@register.inclusion_tag('_edit_link.html')
def edit_link(obj):
    return {'object': obj}


@register.simple_tag(takes_context=True)
def thing_attr(context, attr):
    value = getattr(context['object'], attr['key'])
    if value:
        if attr['datatype'] == TYPE_DATE:
            return date(value, "SHORT_DATETIME_FORMAT")
        elif attr['datatype'] == TYPE_FILE:
            if value.name.split('.')[-1].lower() in ['gif', 'jpeg', 'jpg', 'png']:
                return '<img src="%s%s" alt="%s" />' % (settings.MEDIA_URL, value.name, value.name.split('/')[-1])
            else:
                return '<a href="%s%s">%s</a>' % (settings.MEDIA_URL, value.name, value.name.split('/')[-1])
    return value


@register.tag
def get_things_by_type(parser, token):
    """
    Pulls a queryset of Things

    Usage::

        {% get_things_by_type [app.model] as [varname] [options] %}

        ``limit``
           The number of things that are shown. **Default: 5**

    Example::

        {% get_things_by_type pages.page as things limit=5 %}
        {% for thing in things %}
            {{ thing.name }}
        {% endfor %}
    """
    args, kwargs = [], {}
    bits = token.split_contents()
    content_type = bits[1]
    context_var = bits[3]

    if len(bits) < 3:
        message = "'%s' tag requires more than 4" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[1] != "all" and "." not in bits[1]:
        message = "'%s' must contain a '.'" % bits[0]
        raise TemplateSyntaxError(message)

    if bits[2] != "as":
        message = "'%s' third argument must be 'as'" % bits[0]
        raise TemplateSyntaxError(message)

    kwargs = {}
    for bit in bits:
        if '=' in bit:
            key = bit.split("=", 1)[0]
            value = bit.split("=", 1)[1]
            kwargs[key] = value

    return ListThingsNode(content_type, context_var, *args, **kwargs)


class ListThingsNode(Node):
    def __init__(self, content_type, context_var, *args, **kwargs):
        self.context_var = context_var
        self.kwargs = kwargs

        if content_type == "all":
            self.model = None
        else:
            ct = ContentType.objects.get(
                app_label=content_type.split('.')[0],
                model=content_type.split('.')[1])
            self.model = ct.model_class()
            if self.model.__base__ is not Thing:
                message = "'%s' parent class must be Thing" % content_type
                raise TemplateSyntaxError(message)

    def render(self, context):
        limit = 3
        user = AnonymousUser()

        if 'user' in context:
            user = context['user']

        if 'limit' in self.kwargs:
            try:
                limit = Variable(self.kwargs['limit'])
                limit = limit.resolve(context)
            except:
                limit = self.kwargs['limit']

        limit = int(limit)

        if self.model:
            items = get_thing_objects_qs(self.model, user)
        else:
            pages_ct = ContentType.objects.get(app_label='pages', model='page')
            snippets_ct = ContentType.objects.get(app_label='snippets', model='snippet')
            sub_classes = Thing.__subclasses__()
            query_sets = []
            for sub_class in sub_classes:
                if sub_class not in [pages_ct.model_class(), snippets_ct.model_class()]:
                    query = get_thing_objects_qs(sub_class, user)[:limit]
                    query_sets.append([(item, timezone.make_aware(item.default_order_field(), timezone.utc)) for item in query])
            results = []
            for qs in query_sets:
                for t in qs:
                    results.append(t)
            items = sorted(results, key=lambda thing: thing[1], reverse=True)
            items = [i[0] for i in items]

        objects = [item for item in items[:limit]]

        context[self.context_var] = objects

        return ""
