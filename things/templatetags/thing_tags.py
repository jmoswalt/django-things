from django.template import Library
from django.template.defaultfilters import date
from django.conf import settings

from things.types import TYPE_DATE, TYPE_FILE

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
            return '<img src="%s%s" alt="%s" />' % (settings.MEDIA_URL, value.name, value.name.split('/')[-1])
    return value
