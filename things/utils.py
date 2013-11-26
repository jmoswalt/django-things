import os

from django.http import Http404
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.shortcuts import get_object_or_404
from django.contrib import admin


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
    internal_path = os.path.join(unicode("uploads"), unicode(obj.obj_type_plural().replace(' ', '_')), unicode(obj.id))
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
    public_order = model.public_order or ['-created_at']
    if type(public_order) == type(str()):
        public_order = [public_order,]

    if user.is_superuser:
        queryset = model.objects.order_by(*super_user_order)
    else:
        queryset = model.objects.filter(**public_filter_out).order_by(*public_order)

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



def load_models(msg=None):
    from .attrs import CONTENT, AUTHOR, PUBLISHED_AT, FEATURED
    from .types import TYPE_TEXT
    from .models import ThingType, register_thing
    from .admin import ThingAdmin
    new_classes = []

    # Add try in case ThingType table has not been created
    try:
        mods = ThingType.objects.all()
        len(mods)
    except:
        return None

    if not mods:
        example_type = ThingType()
        example_type.name = "Note"
        example_type.slug = 'notes'
        example_type.json = {
            'fields': (
            CONTENT,
            AUTHOR,
            PUBLISHED_AT,
            FEATURED,
            {
                "name": "Category",
                "key": "category",
                "description": "Add a Category to the {{ model }}.",
                "datatype": TYPE_TEXT,
                "required": False
            }
            )
        }

        example_type.save()
        mods = ThingType.objects.all()

    for mod in mods:
        new_class = mod.get_class()

        register_thing(new_class, attrs=mod.json['fields'])
        try:
            admin.site.register(new_class, ThingAdmin)
        except admin.sites.AlreadyRegistered:
            admin.site.unregister(new_class)
            admin.site.register(new_class, ThingAdmin)

        new_classes.append(new_class)

    return new_classes
