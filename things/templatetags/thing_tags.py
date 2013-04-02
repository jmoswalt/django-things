from django.template import Library
from django.template.defaultfilters import date

from things.types import TYPE_DATE

register = Library()


@register.inclusion_tag('_edit_link.html')
def edit_link(obj):
    return {'object': obj}


@register.simple_tag(takes_context=True)
def thing_attr(context, attr):
    if attr['datatype'] == TYPE_DATE:
        return date(getattr(context['object'], attr['key']), "SHORT_DATETIME_FORMAT")
    return getattr(context['object'], attr['key'])
