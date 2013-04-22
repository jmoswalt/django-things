import os

from django.http import Http404
from django.core.cache import cache
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404


def get_thing_object_or_404(cls, slug, **kwargs):
    """
    Checks if the object is viewable.
    Slug filter MUST be chained so it filters on the
    actual Thing object.
    """
    objs = cls.objects.filter(**kwargs).filter(slug=slug)

    if objs:
        return objs[0]
    else:
        raise Http404


def handle_uploaded_file(obj, f):
    internal_path = os.path.join(unicode("uploads"), unicode(obj.obj_type_plural().replace(' ', '_')), unicode(obj.pk))
    folder_path = os.path.join(settings.MEDIA_ROOT, internal_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = os.path.join(internal_path, f.name)
    full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
    with open(full_file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return file_path


def get_thing_objects_qs(model, user=AnonymousUser()):
    public_filter_out = model.public_filter_out or {}
    super_user_order = model.super_user_order or ['-created_at']
    public_order = model.public_order or ""

    if user.is_superuser:
        queryset = model.objects.order_by(*super_user_order)
    else:
        queryset = model.objects.filter(**public_filter_out)

        if public_order:
            if public_order.replace('-', '') in model.attrs_list():
                if public_order[0] == "-":
                    key = public_order[1:]
                    value = '-datum__value'
                else:
                    key = public_order
                    value = 'datum__value'

                queryset = queryset.filter(datum__key=key).order_by(value)
            else:
                queryset = queryset.order_by(public_order)

    return queryset


def get_thing_object(model, slug, user=AnonymousUser()):
    public_filter_out = model.public_filter_out or {}

    if user.is_superuser:
        obj = get_object_or_404(model, slug=slug)

    else:
        filters = public_filter_out
        obj = get_thing_object_or_404(
            cls=model,
            slug=slug,
            **filters)

    return obj


def clear_attr_cache(instance):
    clear_keys = []
    for key in instance.attrs_list():
        clear_keys.append((".".join([settings.SITE_CACHE_KEY, '%s', str(instance.pk)]) % key))

    cache.delete_many(clear_keys, None)
