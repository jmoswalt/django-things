from django.http import Http404


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
