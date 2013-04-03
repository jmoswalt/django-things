import os

from django.http import Http404
from django.conf import settings


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
    internal_path = os.path.join(unicode("uploads"), unicode(obj.obj_type_plural()), unicode(obj.pk))
    folder_path = os.path.join(settings.MEDIA_ROOT, internal_path)
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)

    file_path = os.path.join(internal_path, f.name)
    full_file_path = os.path.join(settings.MEDIA_ROOT, file_path)
    with open(full_file_path, 'wb+') as destination:
        for chunk in f.chunks():
            destination.write(chunk)

    return file_path
